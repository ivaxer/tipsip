# -*- coding: utf-8 -*-

from twisted.internet import defer, protocol, reactor

from txredis.protocol import Redis

class RedisStorage(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @defer.inlineCallbacks
    def connect(self):
        clientCreator = protocol.ClientCreator(reactor, Redis)
        self.redis = yield clientCreator.connectTCP(self.host, self.port)

    def disconnect(self):
        self.redis.transport.loseConnection()

    @defer.inlineCallbacks
    def hset(self, table, field, value):
        r = yield self.redis.hset(table, field, value)

    @defer.inlineCallbacks
    def hsetn(self, table, items):
        for field, value in items:
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

    def hincr(self, table, field, value):
        raise NotImplementedError

    def hdrop(self, table):
        raise NotImplementedError

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

