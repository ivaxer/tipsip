from twisted.trial import unittest
from twisted.internet import defer


from tipsip.sip import Message, Request, Response
from tipsip.sip import AddressHeader, ViaHeader
from tipsip.sip import URI


class RequestTest(unittest.TestCase):
    def test_constructRequest(self):
        aq = self.assertEqual
        r = Request('NOTIFY', 'sip:echo@tipmeet.com')
        s = str(r).split('\r\n', 1)
        aq(s[0], 'NOTIFY sip:echo@tipmeet.com SIP/2.0')
        aq(s[1], '\r\n')

    def test_createResponse(self):
        aq = self.assertEqual
        at = self.assertTrue
        req = Request('NOTIFY', 'sip:echo@tipmeet.com')
        req.headers['f'] = AddressHeader.parse('Carol <sip:carol@example.com> ;tag=abvgde123')
        req.headers['t'] = AddressHeader.parse("Echo <sip:echo@tipmeet.com>")
        req.headers['via'] = ViaHeader.parse("SIP/2.0/TCP 193.168.0.1:5061; received=10.10.10.10")
        req.headers['call-id'] = '1234@localhost'
        req.headers['cseq'] = '1'
        r = req.createResponse('180', 'Ringing')
        aq(str(r.headers['from']), 'Carol <sip:carol@example.com> ;tag=abvgde123')
        aq(str(r.headers['To'].uri), 'sip:echo@tipmeet.com')
        aq(r.headers['To'].display_name, 'Echo')
        aq(str(r.headers['Via']), 'SIP/2.0/TCP 193.168.0.1:5061 ;received=10.10.10.10')
        aq(r.headers['Call-Id'], '1234@localhost')
        aq(r.headers['CSeq'], '1')
        at('tag' in r.headers['To'].params)
        t1 = r.headers['to'].params['tag']
        at(isinstance(t1, basestring))
        r = req.createResponse('200', 'OK')
        t2 = r.headers['t'].params['tag']
        aq(t1, t2)

    def test_isValid(self):
        at = self.assertTrue
        af = self.assertFalse
        r = Request('NOTIFY', 'sip:echo@tipmeet.com')
        h = r.headers
        af(r.isValid())
        h['f'] = AddressHeader.parse('sip:echo@tipmeet.com')
        af(r.isValid())
        h['To'] = 'sip:echo@tipmeet.com'
        af(r.isValid())
        h['v'] = 'via'
        af(r.isValid())
        h['call-id'] = 'abracadabra'
        af(r.isValid())
        h['CSEQ'] = '1'
        af(r.isValid())
        h['Max-Forwards'] = '30'
        af(r.isValid())
        r.headers['from'].params['tag'] = 'cadabra'
        at(r.isValid())

