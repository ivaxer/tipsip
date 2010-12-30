# -*- coding: utf-8 -*-

import json

import utils

from twisted.internet import reactor, defer

class Status(dict):
    def __init__(self, pdoc, expiresat, priority):
        self['presence'] = pdoc
        self['expiresat'] = expiresat
        self['priority'] = priority

    def serialize(self):
        return json.dumps(self)

    @staticmethod
    def parse(s):
        return json.loads(s)

class PresenceService(object):
    def __init__(self, storage):
        self.storage = storage
        self._callbacks = []
        self._status_timers = {}

    @defer.inlineCallbacks
    def putStatus(self, resource, pdoc, expires, priority=0, tag=None):
        if not tag:
            tag = utils.random_str(10)
        expiresat = expires + utils.seconds()
        table = self._resourceTable(resource)
        status = Status(pdoc, expiresat, priority)
        yield self.storage.hset(table, tag, status.serialize())
        self._setStatusTimer(resource, tag, expires)
        self._notifyWatchers(resource)
        defer.returnValue(tag)

    @defer.inlineCallbacks
    def getStatus(self, resource):
        table = self._resourceTable(resource)
        r = yield self.storage.hgetall(table)
        statuses = [(tag, Status.parse(x)) for (tag,  x) in r.iteritems()]
        active, expired = self._splitExpiredStatuses(statuses)
        if expired:
            self._log("Expired statuses of resource '%s' found: %s" % (resource, expired))
            for tag, _ in expired:
                self.removeStatus(resource, tag)
        defer.returnValue(active)

    def dumpStatuses(self):
        raise NotImplemented

    @defer.inlineCallbacks
    def removeStatus(self, resource, tag):
        table = self._resourceTable(resource)
        try:
            yield self.storage.hdel(table, tag)
            r = 'Status removed'
        except KeyError, e:
            self._log('Storage error: %s' % (e,))
            r = 'Not found'
        self._cancelStatusTimer(resource, tag)
        defer.returnValue(r)

    def watch(self, callback, *args, **kwargs):
        self._callbacks.append((callback, args, kwargs))

    def _splitExpiredStatuses(self, statuses):
        active = []
        expired = []
        cur_time = utils.seconds()
        for tag, status in statuses:
            if status['expiresat'] < cur_time:
                expired.append((tag, status))
            else:
                active.append((tag, status))
        return active, expired

    def _setStatusTimer(self, resource, tag, delay):
        if (resource, tag) in self._status_timers:
            self._status_timers[resource, tag].reset(delay)
        else:
            self._status_timers[resource, tag] = reactor.callLater(delay, self.removeStatus, resource, tag)
        self._storeStatusTimer(resource, tag, delay)

    def _cancelStatusTimer(self, resource, tag):
        if (resource, tag) in self._status_timers:
            timer = self._status_timers.pop((resource, tag))
            if timer.active():
                timer.cancel()
            self._dropStatusTimer(resource, tag)
        else:
            self._log("Timer (%s, %s) already deleted" % (resource, tag))

    @defer.inlineCallbacks
    def _storeStatusTimer(self, resource, tag, delay):
        table = self._timersTable()
        key = '%s:%s' % (resource, tag)
        expiresat = utils.seconds() + delay
        yield self.storage.hset(table, key, expiresat)

    @defer.inlineCallbacks
    def _dropStatusTimer(self, resource, tag):
        table = self._timersTable()
        key = '%s:%s' % (resource, tag)
        yield self.storage.hdel(table, key)

    @defer.inlineCallbacks
    def _loadStatusTimers(self):
        table = self._timersTable()
        timers = yield self.storage.hgetall(table)
        stale_timers = []
        cur_time = utils.seconds()
        for key, expiresat in timers.iteritems():
            resource, tag = key.split(':')
            if expiresat < cur_time:
                self._dropStatusTimer(self, resource, tag)
            else:
                delay = expiresat - cur_time
                self._setStatusTimer(resource, tag, delay)

    @defer.inlineCallbacks
    def _notifyWatchers(self, resource):
        status = yield self.getStatus(resource)
        for callback, arg, kw in self._callbacks:
            callback(resource, status, *args, **kw)

    def _resourceTable(self, resource):
        return 'res:' + resource

    def _timersTable(self):
        return 'sys:timers'

    def _log(self, *args, **kw):
        kw['system'] = 'presence'
        utils.msg(*args, **kw)


