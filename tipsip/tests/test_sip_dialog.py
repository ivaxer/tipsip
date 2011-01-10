from twisted.trial import unittest
from twisted.internet import defer

from tipsip.sip import Dialog, DialogStore
from tipsip import MemoryStorage

class DialogStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = DialogStore(MemoryStorage())

    @defer.inlineCallbacks
    def test_general(self):
        aq = self.assertEqual
        d = Dialog()
        d.local_tag = "321egvba"
        d.remote_tag = "abvge123"
        d.callid = "abacaba@localhost"
        yield self.store.add(d)
        rd = yield self.store.find(d.id)
        aq(d.local_tag, rd.local_tag)
        aq(d.remote_tag, rd.remote_tag)
        aq(d.callid, rd.callid)
        yield self.store.remove(rd.id)
        rd = yield self.store.find(d.id)
        aq(rd, None)


class DialogTest(unittest.TestCase):
    def test_serialization(self):
        aq = self.assertEqual
        d = Dialog()
        d.local_tag = "321egvba"
        d.remote_tag = "abvge123"
        d.callid = "abacaba@localhost"
        d.local_cseq = 10
        d.remote_cseq = 256
        d.local_uri = "john@example.com"
        d.remote_uri = "carol@example.org"
        d.local_target_uri = "sip:john@192.168.1.1"
        d.remote_target_uri = "sip:carol@10.10.10.10"
        rd = Dialog.parse(d.serialize())
        aq(d.local_tag, rd.local_tag)
        aq(d.remote_tag, rd.remote_tag)
        aq(d.callid, rd.callid)
        aq(d.local_cseq, rd.local_cseq)
        aq(d.remote_cseq, rd.remote_cseq)
        aq(d.local_uri, rd.local_uri)
        aq(d.remote_uri, rd.remote_uri)
        aq(d.local_target_uri, rd.local_target_uri)
        aq(d.remote_target_uri, rd.remote_target_uri)

