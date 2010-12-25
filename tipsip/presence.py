# -*- coding: utf-8 -*-

import json

import utils

from twisted.internet import reactor

class Status(dict):
    def __init__(self, pdoc, expiresat, priority):
        self['pdoc'] = pdoc
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

    def putStatus(self, resource, tag, pdoc, expires, priority=0):
        expiresat = expires + utils.seconds()
        table = self._resourceTable(resource)
        status = Status(pdoc, expiresat, priority)
        self.storage.hset(table, tag, status.serialize())
        self._setStatusTimer(resource, tag, expires)
        self._notifyWatchers(resource)

    def getStatus(self, resource):
        table = self._resourceTable(resource)
        statuses = [(tag, Status.parse(x)) for (tag,  x) in self.storage.hgetall(table)]
        active, expired = self._splitExpiredStatuses(statuses)
        if expired:
            self._log("Expired statuses of resource '%s' found: %s" % (resource, expired))
            for tag, _ in expired:
                self.removeStatus(resource, tag)
        return active

    # Consider to move this function from presence core
    def getAggrPdoc(self, resource, f=None):
        def aggr(statuses):
            max_priority = aggr_pdoc = None
            for tag, status in statuses:
                cur_priority = status['priority']
                if cur_priority > max_priority:
                    max_priority = cur_priority
                    aggr_pdoc = status['pdoc']
                elif max_priority == cur_priority and aggr_pdoc and aggr_pdoc['status'] == 'offline' and status['pdoc']['status'] == 'online':
                    aggr_pdoc = status['pdoc']
            return aggr_pdoc
        if not f:
            f = aggr
        statuses = self.getStatus(resource)
        return f(statuses)

    def dumpStatuses(self):
        raise NotImplemented

    def removeStatus(self, resource, tag):
        table = self._resourceTable(resource)
        try:
            self.storage.hdel(table, tag)
        except KeyError, e:
            self._log('Storage error: %s' % (e,))
        self._cancelStatusTimer(resource, tag)

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

    def _storeStatusTimer(self, resource, tag, delay):
        table = self._timersTable()
        key = '%s:%s' % (resource, tag)
        expiresat = utils.seconds() + delay
        self.storage.hset(table, key, expiresat)

    def _dropStatusTimer(self, resource, tag):
        table = self._timersTable()
        key = '%s:%s' % (resource, tag)
        self.storage.hdel(table, key)

    def _loadStatusTimers(self):
        table = self._timersTable()
        timers = self.storage.hgetall(table)
        stale_timers = []
        cur_time = utils.seconds()
        for key, expiresat in timers:
            resource, tag = key.split(':')
            if expiresat < cur_time:
                self._dropStatusTimer(self, resource, tag)
            else:
                delay = expiresat - cur_time
                self._setStatusTimer(resource, tag, delay)

    def _notifyWatchers(self, resource):
        status = self.getStatus(resource)
        for callback, arg, kw in self._callbacks:
            callback(resource, status, *args, **kw)

    def _resourceTable(self, resource):
        return 'res:' + resource

    def _timersTable(self):
        return 'sys:timers'

    def _log(self, *args, **kw):
        kw['system'] = 'presence'
        utils.msg(*args, **kw)

