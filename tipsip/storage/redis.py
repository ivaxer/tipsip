# -*- coding: utf-8 -*-

from twisted.internet import defer, protocol, reactor

from txredis.protocol import Redis
from twisted.internet.protocol import ReconnectingClientFactory

class RedisStorage(ReconnectingClientFactory):
    protocol = Redis

    def __init__(self):
        self._callbacks = []

    def buildProtocol(self, addr):
        self.redis = self.protocol()
        self.resetDelay()
        reactor.callLater(0, self.runConnectedCallbacks)
        return self.redis

    def runConnectedCallbacks(self):
        for callback, arg, kw in self._callbacks:
            callback(*arg, **kw)

    def addCallbackOnConnected(self, callback, *arg, **kw):
        self._callbacks.append((callback, arg, kw))

    @defer.inlineCallbacks
    def hset(self, table, field, value):
        r = yield self.redis.hset(table, field, value)

    @defer.inlineCallbacks
    def hsetn(self, table, items):
        for field, value in items.iteritems():
            yield self.hset(table, field, value)

    @defer.inlineCallbacks
    def hget(self, table, field):
        r = yield self.redis.hget(table, field)
        if not r:
            raise KeyError("Table '%s' or field '%s' not found" % (table, field))
        defer.returnValue(r[field])

    @defer.inlineCallbacks
    def hgetall(self, table):
        r = yield self.redis.hgetall(table)
        if not r:
            raise KeyError("Unknown table '%s'" % (table,))
        defer.returnValue(r)

    @defer.inlineCallbacks
    def hdel(self, table, field):
        r = yield self.redis.hdelete(table, field)
        if r == 0:
            raise KeyError("Table '%s' or field '%s' not found" % (table, field))

    @defer.inlineCallbacks
    def hincr(self, table, field, value):
        yield self.redis.hincr(table, field, value)

    @defer.inlineCallbacks
    def hdrop(self, table):
        r = yield self.redis.delete(table)
        if r == 0:
            raise KetError("Table '%s' not found" % table)

    @defer.inlineCallbacks
    def sadd(self, s, item):
        r = yield self.redis.sadd(s, item)

    @defer.inlineCallbacks
    def srem(self, s, item):
        r = yield self.redis.srem(s, item)
        if r == 0:
            raise KeyError("Set '%s' or item '%s' not found" % (s, item))

    @defer.inlineCallbacks
    def sgetall(self, s):
        r = yield self.redis.smembers(s)
        if r == 0:
            raise KeyError("Set '%s' not found" % (s,))
        defer.returnValue(r)

    def sdrop(self, s):
        raise NotImplementedError

