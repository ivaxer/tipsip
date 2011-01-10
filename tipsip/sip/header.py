# -*- coding: utf-8 -*-

from random import choice
from string import ascii_letters

from uri import URI

# http://www.iana.org/assignments/sip-parameters
name_to_compact = {
        'accept-contact': 'a',
        'allow-events': 'u',
        'call-id':  'i',
        'contact':  'm',
        'content-encoding': 'e',
        'content-length':   'l',
        'content-type': 'c',
        'event':    'o',
        'from': 'f',
        'identity': 'y',
        'identify-info':    'n',
        'refer-to': 'r',
        'referred-by':  'b',
        'reject-contact':   'j',
        'request-disposition':  'd',
        'session-expires':  'x',
        'subject':  's',
        'supported':    'k',
        'to':   't',
        'via':  'v',
        }
compact_to_name = dict(zip(name_to_compact.values(), name_to_compact.keys()))

top_headers = ('via', 'route', 'record-route', 'proxy-require', 'max-forwards',
        'proxy-authorization', 'to', 'from', 'contact')

request_mandatory_headers = ('to', 'from', 'cseq', 'call-id', 'max-forwards', 'via')

name_addr_headers = ('to', 'from', 'contact', 'reply-to', 'record-route', 'route')

exceptions_multiheaders = ('www-authenticate', 'authorization', 'proxy-authenticate',
        'proxy-authorization')

exceptions_normal_form = {
        'www-authenticate': 'WWW-Authenticate',
        'cseq': 'CSeq',
        'call-id': 'Call-ID',
        'mime-version': 'MIME-Version',
        'sip-etag': 'SIP-ETag'
        }


def name2intern(name):
    return compact_to_name.get(name.lower(), name.lower())

def name2norm(name):
    n = name2intern(name)
    if n in exceptions_normal_form:
        return exceptions_normal_form[n]
    return '-'.join(x.capitalize() for x in n.split('-'))

def name2compact(name):
    n = name2intern(name)
    if n in name_to_compact:
        return name_to_compact[n]
    return name2norm(name)

def generate_tag():
    return "".join(choice(ascii_letters) for _ in xrange(7))


class Header(object):
    def __init__(self, value, params=None):
        self.value = value
        self.params = params or {}

    def __str__(self):
        r = []
        r.append(value)
        p = self._renderParams()
        r.append(p)
        return ''.join(r)

    def _renderParams(self):
        return ';'.join('='.join(p) for p in self.params.items())

    @staticmethod
    def _parse_params(s):
        params = {}
        for p in s.split(';'):
            k, v = p.split('=')
            k = k.strip().lower()
            v = v.strip()
            params[k] = v
        return params


class AddressHeader(Header):
    def __init__(self, display_name=None, uri=None, params=None):
        self.display_name = display_name
        self.uri = uri
        self.params = params or {}

    def __str__(self):
        # XXX: check '?', ';' and ',' in uri
        if self.display_name is None:
            return self._renderAddrSpec()
        else:
            return self._renderNameAddr()

    def _renderAddrSpec(self):
        r = []
        r.append(str(self.uri))
        params = self._renderParams()
        if params:
            r.append(';' + params)
        return ' '.join(r)

    def _renderNameAddr(self):
        r = []
        r.append(self.display_name)
        r.append('<' + str(self.uri) + '>')
        params = self._renderParams()
        if params:
            r.append(';' + params)
        return ' '.join(r)

    @classmethod
    def parse(cls, s):
        display_name, uri, rest = cls._parse_nameaddr(s)
        if rest:
            params = cls._parse_params(rest)
        else:
            params = None
        uri = URI.parse(uri)
        return cls(display_name, uri, params)

    @staticmethod
    def _parse_nameaddr(s):
        # XXX: handle quoted chars
        if '<' not in s:
            dn = None
            if ';' in s:
                uri, rest = s.split(';', 1)
            else:
                uri = s
                rest = None
        else:
            dn, rest = s.split('<')
            dn = dn.strip()
            uri, rest = rest.split('>')
            if ';' in rest:
                _, rest = rest.split(';')
                rest = rest.strip()
        uri = uri.strip()
        return dn, uri, rest



class ViaHeader(Header):
    version = 'SIP/2.0'

    def __init__(self, transport, host, port=None, params=None, version='SIP/2.0'):
        self.transport = transport
        self.host = host
        self.port = port
        self.params = params or {}

    def __str__(self):
        r = []
        r.append(self.version + '/' + self.transport)
        addr = self.host
        if self.port:
            addr += ':' + str(self.port)
        r.append(addr)
        p = self._renderParams()
        if p:
            r.append(';' + p)
        return ' '.join(r)

    @classmethod
    def parse(cls, s):
        version, transport, rest = cls._parse_proto(s)
        host, port, rest = cls._parse_hostport(rest)
        if rest:
            params = cls._parse_params(rest)
        return cls(version=version, transport=transport, host=host, port=port, params=params)

    @staticmethod
    def _parse_proto(s):
        sent_by, rest = s.split(None, 1)
        version, transport = sent_by.rsplit('/', 1)
        return version, transport, rest

    @staticmethod
    def _parse_hostport(s):
        if ';' in s:
            s, rest = s.split(';', 1)
        else:
            rest = None
        s = s.strip()
        if ':' in s:
            host, port = s.split(':')
            port = port.strip()
        else:
            host = s
            port = None
        host = host.strip()
        return host, port, rest


class HeaderValueList(list):
    def __str__(self):
        return ', '.join(self)


class Headers(dict):
    compact = False

    def __init__(self, *arg, **kw):
        dict.__init__(self)
        self.update(*arg, **kw)

    def __setitem__(self, key, value):
        k = name2intern(key)
        dict.__setitem__(self, k, value)

    def __getitem__(self, key):
        k = name2intern(key)
        return dict.__getitem__(self, k)

    def __delitem__(self, key):
        k = name2intern(key)
        dict.__delitem__(self, k)

    def __contains__(self, key):
        k = name2intern(key)
        return dict.__contains__(self, k)

    def __str__(self):
        if self.compact:
            f = name2compact
        else:
            f = name2norm
        r = []
        for k, v in self.items():
            r.append('%s: %s' % (f(k), str(v)))
        return '\r\n'.join(r)

    def get(self, key, d=None):
        k = name2intern(key)
        return dict.get(self, k, d)

    def update(self, *arg, **kw):
        for k, v in dict(*arg, **kw).iteritems():
            self[k] = v

    def has_key(self, key):
        k = name2intern(key)
        return dict.has_key(self, k)

    def pop(self, key, d=None):
        k = name2intern(key)
        return dict.pop(self, k)

