# -*- coding: utf-8 -*-

from copy import deepcopy

from twisted.internet import defer

from uri import URI
from header import Headers, generate_tag
from header import request_mandatory_headers


class MessageParsingError(Exception):
    pass


class Message(object):
    version = 'SIP/2.0'

    def __init__(self):
        self.received = None
        self.from_interface = None
        self.headers = Headers()
        self.content = None

    @classmethod
    def parse(cls, s):
        r = s.split('\r\n', 1)
        if len(r) != 2:
            raise MessageParsingError("Bad message (no CRLF found): '%s'" % (s,))
        first_line = r[0]
        r = first_line.split()
        if len(r) != 3:
            raise MessageParsingError("Bad first line: " + first_line)
        if r[0] == cls.version:
            return Response.parse(s)
        elif r[2] == cls.version:
            return Request.parse(s)
        else:
            raise MessageParsingError("Bad first line: " + first_line)


class Response(Message):
    def __init__(self, code, reason):
        Message.__init__(self)
        self.code = code
        self.reason = reason

    def __str__(self):
        r = []
        r.append('%s %s %s' % (self.version, self.code, self.reason))
        hdrs = str(self.headers)
        if hdrs:
            r.append(hdrs)
        r.append('\r\n')
        return '\r\n'.join(r)

    @staticmethod
    def parse(s):
        raise NotImplementedError("Response.parse not implemented")


class Request(Message):
    _dialog_store = None

    def __init__(self, method, ruri, headers=None, content=None):
        Message.__init__(self)
        self.method = method
        self.ruri = ruri
        self.headers = headers or Headers()
        self.content = content
        self.dialog = None
        self._has_totag = None
        self._response_totag = None

    def createResponse(self, code=None, reason=None):
        response = Response(code, reason)
        for x in ('from', 'to', 'call-id', 'cseq', 'via'):
            response.headers[x] = deepcopy(self.headers[x])
        if not self.has_totag:
            response.headers['to'].params['tag'] = self.response_totag
        # XXX: check that it's in-dialog responce
        return response

    @defer.inlineCallbacks
    def createDialog(self):
        d = Dialog()
        d.local_tag = self.response_totag
        d.remote_tag = self.headers['from'].params['tag']
        d.callid = self.headers['call-id']
        d.local_cseq = 0
        d.remote_cseq = int(self.headers['cseq'])
        d.local_uri = str(self.headers['to'].uri)
        d.remote_uri = str(self.headers['from'].uri)
        iface = self.from_interface
        d.local_target_uri = ''.join(['sip:', iface.host, ':', str(iface.port), ';transport=', iface.transport])
        d.remote_target_uri = str(self.headers['contact'].uri)
        self.dialog = d
        yield self._dialog_store.add(d)

    @property
    def has_totag(self):
        if self._has_totag is None:
            self._has_totag = 'tag' in self.headers['to'].params
        return self._has_totag

    @property
    def response_totag(self):
        if self._response_totag is None:
            self._response_totag = generate_tag()
        return self._response_totag

    def isValid(self):
        for x in request_mandatory_headers:
            if x not in self.headers:
                return False
        if 'tag' not in self.headers['from'].params:
            return False
        return True

    @classmethod
    def parse(cls, s):
        if '\r\n\r\n' not in s:
            raise MessageParsingError("Bad message (no CRLFCRLF found)")
        head, content = s.split('\r\n\r\n', 1)
        if not content:
            content = None
        r = head.split('\r\n', 1)
        if len(r) == 1:
            headers = None
        else:
            headers = Headers.parse(r[1])
        request_line = r[0]
        method, uri, version = request_line.split()
        uri = URI.parse(uri)
        return cls(method, uri, headers, content)


    def __str__(self):
        r = []
        r.append('%s %s %s' % (self.method, self.ruri, self.version))
        hdrs = str(self.headers)
        if hdrs:
            r.append(hdrs)
        r.append('\r\n')
        msg = '\r\n'.join(r)
        if self.content:
            msg += self.content
        return msg

