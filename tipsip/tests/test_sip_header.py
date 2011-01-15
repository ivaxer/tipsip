from twisted.trial import unittest

from tipsip.sip import Headers
from tipsip.sip import Header, AddressHeader, ViaHeader


class HeadersTest(unittest.TestCase):
    def test_construct(self):
        aq = self.assertEqual
        at = self.assertTrue
        h = Headers({'Subject': 'lunch'}, f='John', to='abacaba')
        h['TO'] = 'Carol'
        aq(h['Subject'], 'lunch')
        aq(h['from'], 'John')
        aq(h['t'], 'Carol')
        r = str(h)
        for line in r.split('\r\n'):
            at(line in ['Subject: lunch', 'From: John', 'To: Carol'])

    def test_manipulation(self):
        aq = self.assertEqual
        at = self.assertTrue
        h = Headers()
        h['f'] = "from header"
        h['to'] = "to header"
        at('FROM' in h)
        at('To' in h)
        to = h.pop('t')
        aq(to, "to header")
        at(h.has_key('From'))


class HeaderTest(unittest.TestCase):
    def test_construct(self):
        aq = self.assertEqual
        at = self.assertTrue
        h = Header('active', params={'expires': '3600'})
        aq(str(h), 'active ;expires=3600')

class AddressHeaderTest(unittest.TestCase):
    def test_parsing(self):
        aq = self.assertEqual
        v = AddressHeader.parse('<sips:bob@192.0.2.4>;expires=60')
        aq(str(v.uri), 'sips:bob@192.0.2.4')
        aq(v.params['expires'], '60')
        aq(v.display_name, '')
        v = AddressHeader.parse('<sip:server10.biloxi.com;lr>')
        aq(str(v.uri), 'sip:server10.biloxi.com;lr')
        aq(v.params, {})
        aq(v.display_name, '')
        v = AddressHeader.parse('The Operator <sip:operator@cs.columbia.edu>;tag=287447')
        aq(str(v.uri), 'sip:operator@cs.columbia.edu')
        aq(v.display_name, 'The Operator')
        aq(v.params, {'tag': '287447'})
        v = AddressHeader.parse('sip:echo@example.com')
        aq(str(v.uri), 'sip:echo@example.com')


class ViaHeaderTest(unittest.TestCase):
    def test_construct(self):
        aq = self.assertEqual
        v = ViaHeader(transport='UDP', host='192.168.0.1', port='5060', params={'received': '8.8.8.8'})
        aq(str(v), 'SIP/2.0/UDP 192.168.0.1:5060 ;received=8.8.8.8')

    def test_parsing(self):
        aq = self.assertEqual
        at = self.assertTrue
        v = ViaHeader.parse('SIP/2.0/UDP 127.0.0.1:21375;branch=z9hG4bK-d8754z-2f9c4f090fc81b1f-1---d8754z-;rport')
        aq(v.version, 'SIP/2.0')
        aq(v.transport, 'UDP')
        aq(v.host, '127.0.0.1')
        aq(v.port, '21375')
        aq(v.params['branch'], 'z9hG4bK-d8754z-2f9c4f090fc81b1f-1---d8754z-')
        at('rport' in v.params)
        v = ViaHeader.parse('SIP/2.0/UDP pc33.atlanta.com:5066;branch=z9hG4bK776asdhds')
        aq(v.port, '5066')

    def test_serialize(self):
        aq = self.assertEqual
        v = ViaHeader.parse('SIP/2.0/UDP 127.0.0.1:21375;rport')
        aq(str(v), 'SIP/2.0/UDP 127.0.0.1:21375 ;rport')

