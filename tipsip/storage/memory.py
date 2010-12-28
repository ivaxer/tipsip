# -*- coding: utf-8 -*-

from collections import defaultdict

from twisted.internet import defer


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

