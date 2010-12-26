from twisted.trial import unittest
from twisted.internet import reactor, defer

import json

from tipsip import PresenceService, MemoryStorage

class PresenceServerTest(unittest.TestCase):
    def setUp(self):
        self.presence = PresenceService(MemoryStorage())

    @defer.inlineCallbacks
    def test_removeStatus(self):
        yield self.presence.putStatus('ivaxer@tipmeet.com', 'forwarding', {"status": "online"},  expires=3600, priority=10)
        yield self.presence.putStatus('john@tipmeet.com', 'rand', {"status": "online"},  expires=3600)
        yield self.presence.removeStatus('john@tipmeet.com', 'rand')
        yield self.presence.removeStatus('ivaxer@tipmeet.com', 'forwarding')
        s1 = yield self.presence.getStatus('ivaxer@tipmeet.com')
        s2 = yield self.presence.getStatus('john@tipmeet.com')
        self.assertEqual(s1, [])
        self.assertEqual(s2, [])

    @defer.inlineCallbacks
    def test_statusExpires(self):
        yield self.presence.putStatus('ivaxer@tipmeet.com', 'forwarding', '', expires=0.01)
        yield self.presence.putStatus('ivaxer@tipmeet.com', 'calendar', '', expires=0.01)
        yield self.presence.putStatus('ivaxer@tipmeet.com', 'rand', '', expires=0.01)
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
        yield self.presence.putStatus('ivaxer@tipmeet.com', 'forwarding', {"status": "online"},  expires=3600, priority=10)
        yield self.presence.removeStatus('ivaxer@tipmeet.com', 'forwarding')

    @defer.inlineCallbacks
    def test_statusLoadStore(self):
        d = defer.Deferred()
        yield self.presence._storeStatusTimer('ivaxer@tipmeet.com', 'tag', 0.01)
        yield self.presence._loadStatusTimers()
        self.assertTrue(self.presence._status_timers['ivaxer@tipmeet.com', 'tag'].active())
        reactor.callLater(0.02, lambda: d.callback(len(self.presence._status_timers)))
        d.addCallback(self.assertEqual, 0)
        yield d

