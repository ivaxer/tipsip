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


def name2intern(name):
    return compact_to_name.get(name.lower(), name.lower())

def generate_tag():
    return "".join(choice(ascii_letters) for _ in xrange(7))


class HeaderValue(object):
    def __init__(self, value, params=None):
        self.value = value
        self.params = params or {}

    def __str__(self):
        params = ';'.join('='.join(p) for p in self.params.items())
        r = []
        r.append(self.value)
        if params:
            r.append(' ;' + params)
        return ''.join(r)

    @classmethod
    def parse(cls, s):
        raise NotImplementedError


class HeaderValueList(list):
    def __str__(self):
        return ', '.join(self)


class Headers(dict):
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

    def get(self, key, d=None):
        k = name2intern(key)
        return dict.get(self, k, d)

    def update(self, *arg, **kw):
        for k, v in dict(*arg, **kw).iteritems():
            self[k] = v

