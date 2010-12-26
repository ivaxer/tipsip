from twisted.trial import unittest
from twisted.internet import defer

from tipsip import MemoryStorage, RedisStorage

class StorageTestCase(object):
    @defer.inlineCallbacks
    def test_hsetget(self):
        yield self.storage.hset("table", "field", "value")
        res = yield self.storage.hget("table", "field")
        self.assertEqual(res, "value")

    @defer.inlineCallbacks
    def test_hget_unknown(self):
        yield self.storage.hset("table", "test", "1")
        d1 = self.storage.hget("table", "cadabra")
        d2 = self.storage.hget("cadabra", "cadabra")
        d1.addErrback(lambda f: f.trap(KeyError))
        d2.addErrback(lambda f: f.trap(KeyError))
        yield d1
        yield d2

    @defer.inlineCallbacks
    def test_hsetngetall(self):
        yield self.storage.hsetn("table", [("field1", "value1"), ("field2", "value2")])
        r = yield self.storage.hgetall("table")
        ex = {'field1': 'value1', 'field2': 'value2'}
        self.assertEqual(ex, r)

    def test_hgetall_unknown(self):
        d = self.storage.hgetall("cadabra")
        d.addErrback(lambda f: f.trap(KeyError))
        yield d

    @defer.inlineCallbacks
    def test_hdel(self):
        yield self.storage.hset("table", "field", "value")
        yield self.storage.hdel("table", "field")

    @defer.inlineCallbacks
    def test_hdel_unknown(self):
        yield self.storage.hset("table", "field", "1")
        d1 = self.storage.hdel("table", "cadabra")
        d2 = self.storage.hdel("cadabra", "cadabra")
        d1.addErrback(lambda f: f.trap(KeyError))
        d2.addErrback(lambda f: f.trap(KeyError))
        yield d1
        yield d2

    @defer.inlineCallbacks
    def test_saddgetall(self):
        yield self.storage.sadd("set", "item1")
        yield self.storage.sadd("set", "item2")
        yield self.storage.sadd("set", "item1")
        yield self.storage.srem("set", "item1")
        r = yield self.storage.sgetall("set")
        self.assertEqual(r, set(['item2']))

    @defer.inlineCallbacks
    def test_srem_unknown(self):
        yield self.storage.sadd("set", "item")
        d = self.storage.srem("set", "cadabra")
        d.addErrback(lambda f: f.trap(KeyError))
        yield d

    def test_sgetall_unknown(self):
        d = self.storage.sgetall("cadabra")
        d.addErrback(lambda f: f.trap(KeyError))
        yield d

class MemoryStorageTest(StorageTestCase, unittest.TestCase):
    def setUp(self):
        self.storage = MemoryStorage()


class RedisStorageTest(StorageTestCase, unittest.TestCase):
    @defer.inlineCallbacks
    def setUp(self):
        self.storage = RedisStorage('localhost', 6379)
        yield self.storage.connect()
        yield self.storage.redis.flush()

    def tearDown(self):
        self.storage.disconnect()

