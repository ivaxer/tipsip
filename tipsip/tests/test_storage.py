from twisted.trial import unittest
from twisted.internet import defer, reactor

from tipsip.storage import MemoryStorage, RedisStorage

class StorageTestCase(object):
    @defer.inlineCallbacks
    def test_hsetget(self):
        yield self.storage.hset("table", "field", "value")
        res = yield self.storage.hget("table", "field")
        self.assertEqual(res, "value")

    @defer.inlineCallbacks
    def test_hget_unknown(self):
        yield self.storage.hset("table", "test", "1")
        try:
            yield self.storage.hget("table", "cadabra")
        except KeyError:
            pass
        else:
            self.fail("KeyError not raised")

        try:
            yield self.storage.hget("cadabra", "cadabra")
        except KeyError:
            pass
        else:
            self.fail("KeyError not raised")

    @defer.inlineCallbacks
    def test_hsetngetall(self):
        yield self.storage.hsetn("table", {"field1": "value1", "field2": "value2"})
        r = yield self.storage.hgetall("table")
        ex = {'field1': 'value1', 'field2': 'value2'}
        self.assertEqual(ex, r)

    @defer.inlineCallbacks
    def test_hgetall_unknown(self):
        try:
            yield self.storage.hgetall("cadabra")
        except KeyError:
            pass
        else:
            self.fail("KeyError not raised")

    @defer.inlineCallbacks
    def test_hdel(self):
        yield self.storage.hset("table", "field", "value")
        yield self.storage.hdel("table", "field")

    @defer.inlineCallbacks
    def test_hdel_unknown(self):
        yield self.storage.hset("table", "field", "1")
        try:
            yield self.storage.hdel("table", "cadabra")
        except KeyError:
            pass
        else:
            self.fail("KeyError not raised")

        try:
            yield self.storage.hdel("cadabra", "cadabra")
        except KeyError:
            pass
        else:
            self.fail("KeyError not raised")

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
        try:
            yield self.storage.srem("set", "cadabra")
        except KeyError:
            pass
        else:
            self.fail("KeyError not raised")

    @defer.inlineCallbacks
    def test_sgetall_unknown(self):
        try:
            yield self.storage.sgetall("cadabra")
        except KeyError:
            pass

    # XXX: implement
    def test_hincr(self):
        pass

    # XXX: implement
    def test_hincr_unknown(self):
        pass

    # XXX: implement
    def test_drop(self):
        pass

    # XXX: implement
    def test_drop_unknown(self):
        pass

class MemoryStorageTest(StorageTestCase, unittest.TestCase):
    def setUp(self):
        self.storage = MemoryStorage()


class RedisStorageTest(StorageTestCase, unittest.TestCase):
    @defer.inlineCallbacks
    def setUp(self):
        d = defer.Deferred()
        storage = RedisStorage()
        storage.addCallbackOnConnected(d.callback, None)
        self.connector = reactor.connectTCP('localhost', 6379, storage)
        yield d
        yield storage.redis.flush()
        self.storage = storage

    def tearDown(self):
        self.connector.disconnect()
        self.storage.stopTrying()

