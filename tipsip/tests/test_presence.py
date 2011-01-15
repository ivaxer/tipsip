from twisted.trial import unittest
from twisted.internet import reactor, defer

import json

from tipsip import PresenceService, MemoryStorage

class PresenceServerTest(unittest.TestCase):
    def setUp(self):
        self.presence = PresenceService(MemoryStorage())

    @defer.inlineCallbacks
    def test_removeStatus(self):
        tag1 = yield self.presence.putStatus('ivaxer@tipmeet.com', {"status": "online"},  expires=3600, tag='forwarding', priority=10)
        tag2 = yield self.presence.putStatus('john@tipmeet.com', {"status": "online"},  expires=3600)
        self.assertEqual('forwarding', tag1)
        yield self.presence.removeStatus('john@tipmeet.com', tag2)
        yield self.presence.removeStatus('ivaxer@tipmeet.com', 'forwarding')
        s1 = yield self.presence.getStatus('ivaxer@tipmeet.com')
        s2 = yield self.presence.getStatus('john@tipmeet.com')
        self.assertEqual(s1, [])
        self.assertEqual(s2, [])

    @defer.inlineCallbacks
    def test_statusExpires(self):
        yield self.presence.putStatus('ivaxer@tipmeet.com', '', tag='forwarding', expires=0.01)
        yield self.presence.putStatus('ivaxer@tipmeet.com', '', tag='calendar', expires=0.01)
        yield self.presence.putStatus('ivaxer@tipmeet.com', '', tag='rand', expires=0.01)
        d = defer.Deferred()
        reactor.callLater(0.02, d.callback, None)
        yield d
        s = yield self.presence.getStatus('ivaxer@tipmeet.com')
        self.assertEqual(s, [])


    @defer.inlineCallbacks
    def test_removeUnknownStatus(self):
        yield self.presence.removeStatus('cadabra@tipmeet.com', 'cadabra')

    @defer.inlineCallbacks
    def test_getStatus(self):
        aq = self.assertEqual
        yield self.presence.putStatus('ivaxer@tipmeet.com', {"status": "online"},  expires=3600, tag='forwarding', priority=10)
        r = yield self.presence.getStatus('ivaxer@tipmeet.com')
        aq(len(r), 1)
        tag, status = r[0]
        aq(tag, 'forwarding')
        aq(status['presence'], {'status': 'online'})
        yield self.presence.removeStatus('ivaxer@tipmeet.com', 'forwarding')

    @defer.inlineCallbacks
    def test_getUnknownStatus(self):
        aq = self.assertEqual
        r = yield self.presence.getStatus('ivaxer@tipmeet.com')
        aq(r, [])

    @defer.inlineCallbacks
    def test_statusLoadStore(self):
        d = defer.Deferred()
        yield self.presence._storeStatusTimer('ivaxer@tipmeet.com', 'tag', 0.01)
        yield self.presence._loadStatusTimers()
        self.assertTrue(self.presence._status_timers['ivaxer@tipmeet.com', 'tag'].active())
        reactor.callLater(0.02, lambda: d.callback(len(self.presence._status_timers)))
        d.addCallback(self.assertEqual, 0)
        yield d

