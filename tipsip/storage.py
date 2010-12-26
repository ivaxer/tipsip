# -*- coding: utf-8 -*-

from collections import defaultdict

from twisted.internet import reactor, defer, protocol, error


class MemoryStorage(object):
    def __init__(self):
        self.htables = defaultdict(dict)
        self.sets = defaultdict(set)

    def hset(self, table, field, value):
        self.htables[table][field] = value
        return defer.succeed(0)

    def hsetn(self, table, items):
        self.htables[table].update(items)
        return defer.succeed(0)

    def hget(self, table, field):
        try:
            r = self.htables[table][field]
        except KeyError:
            return defer.fail( KeyError("Table '%s' or field '%s' not found" % (table, field)) )
        return defer.succeed(r)

    def hgetall(self, table):
        try:
            r = self.htables[table]
        except KeyError:
            return defer.fail( KeyError("Table '%s' not found" % (table,)) )
        return defer.succeed(r)

    def hdel(self, table, field):
        try:
            del self.htables[table][field]
        except KeyError:
            return defer.fail( KeyError("Table '%s' or field '%s' not found" % (table, field)) )
        return defer.succeed(0)

    def sadd(self, s, item):
        self.sets[s].add(item)
        return defer.succeed(0)

    def saddn(self, s, items):
        self.sets[s].update(items)
        return defer.succeed(0)

    def srem(self, s, item):
        try:
            self.sets[s].remove(item)
        except KeyError:
            return defer.fail( KeyError("Set '%s' or item '%s' not found" % (s, item)) )
        return defer.succeed(0)

    def sgetall(self, s):
        try:
            r = self.sets[s]
        except KeyError:
            return defer.fail( KeyError("Set '%s' not found" % (s,)) )
        return defer.succeed(r)


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


