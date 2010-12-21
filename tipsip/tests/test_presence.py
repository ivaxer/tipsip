from twisted.trial import unittest
from twisted.internet import reactor, defer

import json

from tipsip import PresenceService, MemoryStorage

class PresenceServerTest(unittest.TestCase):
    def setUp(self):
        self.presence = PresenceService(MemoryStorage())

    def test_removeStatus(self):
        self.presence.putStatus('ivaxer@tipmeet.com', 'forwarding', {"status": "online"},  expires=3600, priority=10)
        self.presence.putStatus('john@tipmeet.com', 'rand', {"status": "online"},  expires=3600)
        self.presence.removeStatus('john@tipmeet.com', 'rand')
        self.presence.removeStatus('ivaxer@tipmeet.com', 'forwarding')
        self.assertEqual(self.presence.getStatus('ivaxer@tipmeet.com'), [])
        self.assertEqual(self.presence.getStatus('john@tipmeet.com'), [])

    def test_statusExpires(self):
        d = defer.Deferred()
        self.presence.putStatus('ivaxer@tipmeet.com', 'forwarding', '', expires=0.01)
        self.presence.putStatus('ivaxer@tipmeet.com', 'calendar', '', expires=0.01)
        self.presence.putStatus('ivaxer@tipmeet.com', 'rand', '', expires=0.01)
        reactor.callLater(0.02, lambda: d.callback(self.presence.getStatus('ivaxer@tipmeet.com')))
        d.addCallback(self.assertEqual, [])
        return d

    def test_removeUnknownStatus(self):
        self.presence.removeStatus('cadabra@tipmeet.com', 'cadabra')

    def test_getStatus(self):
        self.presence.putStatus('ivaxer@tipmeet.com', 'forwarding', {"status": "online"},  expires=3600, priority=10)
        self.presence.removeStatus('ivaxer@tipmeet.com', 'forwarding')

    def test_getAggrPodc(self):
        d = defer.Deferred()
        self.presence.putStatus('ivaxer@tipmeet.com', 'calendar', {'status': 'online'}, expires=0.01)
        self.presence.putStatus('ivaxer@tipmeet.com', 'rand', {'status': 'offline'}, expires=0.01, priority=10)
        self.presence.putStatus('john@tipmeet.com', 'calendar', {'status': 'online'}, expires=0.01)
        self.presence.putStatus('john@tipmeet.com', 'rand', {'status': 'offline'}, expires=0.01, priority=10)
        self.presence.putStatus('john@tipmeet.com', 'chuck', {'status': 'online'}, expires=0.01, priority=10)
        pdoc = self.presence.getAggrPdoc('ivaxer@tipmeet.com')
        self.assertEqual(pdoc['status'], 'offline')
        pdoc = self.presence.getAggrPdoc('john@tipmeet.com')
        self.assertEqual(pdoc['status'], 'online')
        reactor.callLater(0.02, d.callback, None)
        return d
