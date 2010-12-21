from twisted.trial import unittest

from tipsip import MemoryStorage

class StorageTestCase(object):
    def test_hsetget(self):
        self.storage.hset("table", "field", "value")
        res = self.storage.hget("table", "field")
        self.assertEqual(res, "value")


    def test_hget_unknown(self):
        self.storage.hset("table", "test", "1")
        self.assertRaises(KeyError, self.storage.hget, "table", "cadabra")
        self.assertRaises(KeyError, self.storage.hget, "cadabra", "cadabra")

    def test_hsetngetall(self):
        self.storage.hsetn("table", [("field1", "value1"), ("field2", "value2")])
        items = self.storage.hgetall("table")
        self.assertTrue(("field1", "value1") in items)
        self.assertTrue(("field1", "value1") in items)
        self.assertEqual(len(items), 2)

    def test_hgetall_unknown(self):
        self.assertRaises(KeyError, self.storage.hgetall, "cadabra")

    def test_hdel(self):
        self.storage.hset("table", "field", "value")
        self.storage.hdel("table", "field")

    def test_hdel_unknown(self):
        self.storage.hset("table", "field", "1")
        self.assertRaises(KeyError, self.storage.hdel, "table", "cadabra")
        self.assertRaises(KeyError, self.storage.hdel, "cadabra", "cadabra")

    def test_saddgetall(self):
        self.storage.sadd("set", "item1")
        self.storage.sadd("set", "item2")
        self.storage.sadd("set", "item1")
        self.storage.srem("set", "item1")
        r = self.storage.sgetall("set")
        self.assertEqual(r, ['item2'])

    def test_srem_unknown(self):
        self.storage.sadd("set", "item")
        self.assertRaises(KeyError, self.storage.srem, "set", "cadabra")

    def test_sgetall_unknown(self):
        self.assertRaises(KeyError, self.storage.sgetall, "cadabra")

class MemoryStorageTest(StorageTestCase, unittest.TestCase):
    def setUp(self):
        self.storage = MemoryStorage()
