from twisted.trial import unittest
from twisted.internet import defer

from tipsip.sip import URI


class URITest(unittest.TestCase):
    def test_parsing(self):
        aq = self.assertEqual
        uri = URI.parse('sip:alice@atlanta.com')
        aq(uri.scheme, 'sip')
        aq(uri.user, 'alice')
        aq(uri.host, 'atlanta.com')
        uri = URI.parse('sip:alice:secretword@atlanta.com;transport=tcp')
        aq(uri.scheme, 'sip')
        aq(uri.user, 'alice:secretword')
        aq(uri.params['transport'], 'tcp')
        uri = URI.parse('sips:alice@atlanta.com?subject=project%20x&priority=urgent')
        aq(uri.scheme, 'sips')
        aq(uri.user, 'alice')
        aq(uri.host, 'atlanta.com')
        aq(uri.headers['subject'], 'project%20x')
        aq(uri.headers['priority'], 'urgent')
        uri = URI.parse('sip:+1-212-555-1212:1234@gateway.com;user=phone')
        aq(uri.scheme, 'sip')
        aq(uri.user, '+1-212-555-1212:1234')
        aq(uri.host, 'gateway.com')
        aq(uri.params['user'], 'phone')
        uri = URI.parse('sips:1212@gateway.com')
        aq(uri.scheme, 'sips')
        aq(uri.user, '1212')
        aq(uri.host, 'gateway.com')
        uri = URI.parse('sip:alice@192.0.2.4')
        aq(uri.scheme, 'sip')
        aq(uri.user, 'alice')
        aq(uri.host, '192.0.2.4')
        uri = URI.parse('sip:atlanta.com;method=REGISTER?to=alice%40atlanta.com')
        aq(uri.scheme, 'sip')
        aq(uri.user, None)
        aq(uri.host, 'atlanta.com')
        aq(uri.params['method'], 'REGISTER')
        aq(uri.headers['to'], 'alice%40atlanta.com')
        uri = URI.parse('sip:alice;day=tuesday@atlanta.com')
        aq(uri.scheme, 'sip')
        aq(uri.user, 'alice;day=tuesday')
        aq(uri.host, 'atlanta.com')
        uri = URI.parse('sips:example.com:5060')
        aq(uri.scheme, 'sips')
        aq(uri.host, 'example.com')
        aq(uri.port, 5060)

    def test_constructing(self):
        aq = self.assertEqual
        at = self.assertTrue
        af = self.assertFalse
        uri = URI(scheme='sip', user='alice', host='atlanta.com')
        aq(str(uri), 'sip:alice@atlanta.com')
        uri = URI(scheme='sip', user='alice:secretword', host='atlanta.com', params={'transport': 'tcp'})
        aq(str(uri), 'sip:alice:secretword@atlanta.com;transport=tcp')
        uri = URI(scheme='sips', user='alice', host='atlanta.com', headers={'subject': 'project%20x', 'priority': 'urgent'})
        at(str(uri) == 'sips:alice@atlanta.com?subject=project%20x&priority=urgent' or str(uri) == 'sips:alice@atlanta.com?priority=urgent&subject=project%20x')
        uri = URI(scheme='sip', user='+1-212-555-1212:1234', host='gateway.com', params={'user': 'phone'})
        aq(str(uri), 'sip:+1-212-555-1212:1234@gateway.com;user=phone')
        uri = URI(scheme='sip', host='atlanta.com', params={'method': 'REGISTER'}, headers={'to': 'alice%40atlanta.com'})
        aq(str(uri), 'sip:atlanta.com;method=REGISTER?to=alice%40atlanta.com')
        uri = URI(scheme='sip', user='alice;day=tuesday', host='atlanta.com')
        aq(str(uri), 'sip:alice;day=tuesday@atlanta.com')
        uri = URI(scheme='sip', host='example.com:5060')
        aq(str(uri), 'sip:example.com:5060')
        uri = URI(scheme='sip', host='server10.biloxi.com', lr=True)
        aq(str(uri), 'sip:server10.biloxi.com;lr')

    def test_invalid(self):
        ar = self.assertRaises
        ar(ValueError, URI.parse, "")
        ar(ValueError, URI.parse, "tel:tipmeet.com")
        ar(ValueError, URI.parse, "tipmeet.com")
        ar(ValueError, URI.parse, "sip:tipmeet.com?test")
        ar(ValueError, URI.parse, "sip:tipmeet.com;test")

