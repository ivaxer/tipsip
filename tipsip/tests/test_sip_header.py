from twisted.trial import unittest

from tipsip.sip import Headers, HeaderValue


class HeadersTest(unittest.TestCase):
    def test_construct(self):
        aq = self.assertEqual
        h = Headers({'Subject': 'lunch'}, f='John', to='abacaba')
        h['TO'] = 'Carol'
        aq(h['Subject'], ['lunch'])
        aq(str(h['from']), 'John')
        aq(str(h['t']), 'Carol')

    def test_multiheaders(self):
        aq = self.assertEqual
        h1 = Headers()
        h1['Route'] = '<sip:alice@atlanta.com>'
        h1['Route'].append('<sip:bob@biloxi.com>')
        h1['Route'].append('<sip:carol@chicago.com>')
        aq(str(h1['Route']), '<sip:alice@atlanta.com>, <sip:bob@biloxi.com>, <sip:carol@chicago.com>')
        h2 = Headers()
        h2['Route'] = ['<sip:alice@atlanta.com>', '<sip:bob@biloxi.com>']
        h2['Route'].append('<sip:carol@chicago.com>')
        aq(h1, h2)
        aq(str(h2['Route']), '<sip:alice@atlanta.com>, <sip:bob@biloxi.com>, <sip:carol@chicago.com>')


class HeaderValueTest(unittest.TestCase):
    def test_construct(self):
        aq = self.assertEqual
        at = self.assertTrue
        v = HeaderValue('SIP/2.0/UDP server10.biloxi.com', {'branch': 'z9hG4bKnashds8'})
        v.params['received'] = '192.0.2.3'
        r1 = 'SIP/2.0/UDP server10.biloxi.com ;branch=z9hG4bKnashds8;received=192.0.2.3'
        r2 = 'SIP/2.0/UDP server10.biloxi.com ;received=192.0.2.3;branch=z9hG4bKnashds8'
        at(str(v) == r1 or str(v) == r2)
        v = HeaderValue('314159 INVITE')
        aq(str(v), '314159 INVITE')

