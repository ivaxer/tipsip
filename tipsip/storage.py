# -*- coding: utf-8 -*-

from collections import defaultdict

class MemoryStorage(object):
    def __init__(self):
        self.htables = defaultdict(dict)
        self.sets = defaultdict(set)

    def hset(self, table, field, value):
        self.htables[table][field] = value

    def hsetn(self, table, items):
        self.htables[table].update(items)

    def hget(self, table, field):
        if table in self.htables:
            return self.htables[table][field]
        else:
            raise KeyError("Unknown table '%s'" % (table,))

    def hgetall(self, table):
        if table in self.htables:
            return self.htables[table].items()
        else:
            raise KeyError("Unknown table '%s'" % (table,))

    def hdel(self, table, field):
        if table in self.htables:
            del self.htables[table][field]
        else:
            raise KeyError("Unknown table '%s'" % (table,))

    def sadd(self, s, item):
        self.sets[s].add(item)

    def saddn(self, s, items):
        self.sets[s].update(items)

    def srem(self, s, item):
        if s in self.sets:
            self.sets[s].remove(item)
        else:
            raise KeyError("Unknown set '%s'" % (s,))

    def sgetall(self, s):
        if s in self.sets:
            return list(self.sets[s])
        else:
            raise KeyError("Unknown set '%s'" % (s,))

