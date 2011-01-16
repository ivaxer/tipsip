# -*- coding: utf-8 -*-

from collections import defaultdict

from twisted.internet import defer


class MemoryStorage(object):
    def __init__(self):
        self.htables = {}
        self.sets = defaultdict(set)

    def hset(self, table, field, value):
        if table not in self.htables:
            self.htables[table] = {}
        self.htables[table][field] = value
        return defer.succeed(0)

    def hsetn(self, table, items):
        if table not in self.htables:
            self.htables[table] = {}
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
            r = self.htables[table].copy()
        except KeyError:
            return defer.fail( KeyError("Table '%s' not found" % (table,)) )
        return defer.succeed(r)

    def hdel(self, table, field):
        try:
            del self.htables[table][field]
        except KeyError:
            return defer.fail( KeyError("Table '%s' or field '%s' not found" % (table, field)) )
        return defer.succeed(0)

    def hincr(self, table, field, value):
        try:
            self.htables[table][field] += value
        except KeyError:
            return defer.fail( KeyError("Table '%s' or field '%s' not found" % (table, field)) )
        return defer.succeed(self.htables[table][field])

    def hdrop(self, table):
        try:
            self.htables.pop(table)
        except KeyError:
            return defer.fail( KeyError("Table '%s' not found" % table) )
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
            r = self.sets[s].copy()
        except KeyError:
            return defer.fail( KeyError("Set '%s' not found" % (s,)) )
        return defer.succeed(r)

    def sdrop(self, s):
        try:
            self.sets.pop(table)
        except KeyError:
            return defer.fail( KeyError("Set '%s' not found" % s) )
        return defer.succeed(0)

