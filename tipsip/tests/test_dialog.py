from twisted.trial import unittest
from twisted.internet import defer

from tipsip.dialog import Dialog, DialogStore
from tipsip.storage import MemoryStorage

class DialogStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = DialogStore(MemoryStorage())

    @defer.inlineCallbacks
    def test_putget(self):
        aq = self.assertEqual
        at = self.assertTrue
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
        d.secure = True
        d.route_set = ['<sip:proxy1>', '<sip:proxy2>']
        yield self.store.put(d)
        rd = yield self.store.get(d.id)
        aq(d.local_tag, rd.local_tag)
        aq(d.remote_tag, rd.remote_tag)
        aq(d.callid, rd.callid)
        aq(d.local_cseq, rd.local_cseq)
        aq(d.remote_cseq, rd.remote_cseq)
        aq(d.local_uri, rd.local_uri)
        aq(d.remote_uri, rd.remote_uri)
        aq(d.local_target_uri, rd.local_target_uri)
        aq(d.remote_target_uri, rd.remote_target_uri)
        at(d.secure)
        aq(d.route_set, ['<sip:proxy1>', '<sip:proxy2>'])

    # XXX: implement
    def test_incr_cseq(self):
        pass

