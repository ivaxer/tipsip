# -*- coding: utf-8 -*-

class URI(object):
    DEFAULT_SCHEME = 'sip'

    def __init__(self, scheme=None, user=None, host=None, port=None, lr=None, params=None, headers=None):
        if not scheme:
            scheme = self.DEFAULT_SCHEME
        self.scheme = scheme
        self.user = user
        self.host = host
        self.port = port
        self.lr = lr
        self.params = params or {}
        self.headers = headers or {}

    def __repr__(self):
        return "<URI scheme=%r, user=%r, host=%r, port=%r, lr=%r, params=%r, headers=%r>" % \
                (self.scheme, self.user, self.host, self.port, self.lr, self.params, self.headers)

    def __str__(self):
        p = ['='.join(p) for p in self.params.items()]
        if self.lr:
            p.append('lr')
        parameters = ';'.join(p)
        headers = '&'.join('='.join(h) for h in self.headers.items())

        uri = []
        uri.append(self.scheme + ':')
        if self.user:
            uri.append(self.user + '@')
        uri.append(self.host)
        if self.port:
            uri.append(':' + str(self.port))
        if parameters:
            uri.append(';' + parameters)
        if headers:
            uri.append('?' + headers)
        return ''.join(uri)

    @staticmethod
    def parse(s):
        if s.startswith('sip:'):
            scheme = 'sip'
            s = s[4:]
        elif s.startswith('sips:'):
            scheme = 'sips'
            s = s[5:]
        else:
            raise ValueError("Unsupported scheme: " + s.split(':', 1)[0])

        if '@' in s:
            user, s = s.split('@', 1)
        else:
            user = None

        if ';' in s:
            hostport, s = s.split(';', 1)
            if '?' in s:
                parameters, hdrs = s.split('?', 1)
            else:
                hdrs = None
                parameters = s
        elif '?' in s:
            hostport, hdrs = s.split('?', 1)
            parameters = None
        else:
            hostport = s
            parameters = None
            hdrs = None

        if ':' in hostport:
            host, port = hostport.split(':', 1)
            port = int(port)
        else:
            host = hostport
            port = None

        params = {}
        lr = None
        if parameters:
            lr = None
            for param in parameters.split(';'):
                if param == 'lr' or param.startswith('lr='):
                    lr = True
                    continue
                if '=' not in param:
                    raise ValueError("Invalid uri-paramenter: " + param)
                pname, pvalue = param.split('=', 1)
                params[pname] = pvalue

        headers = {}
        if hdrs:
            for header in hdrs.split('&'):
                if '=' not in header:
                    raise ValueError("Invalid header: " + header)
                hname, hvalue = header.split('=', 1)
                headers[hname] = hvalue
        return URI(scheme, user, host, port, lr, params, headers)

