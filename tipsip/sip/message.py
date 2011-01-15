# -*- coding: utf-8 -*-

from copy import deepcopy

from twisted.internet import defer

from uri import URI
from header import Headers, AddressHeader
from header import generate_tag, request_mandatory_headers


class MessageParsingError(Exception):
    pass


class Message(object):
    version = 'SIP/2.0'

    def __init__(self, headers=None, content=None):
        self.received = None
        self.from_interface = None
        self.headers = headers or Headers()
        self.content = content

    @classmethod
    def parse(cls, s):
        if '\r\n\r\n' not in s:
            raise MessageParsingError("Bad message (no CRLFCRLF found)")
        head, content = s.split('\r\n\r\n', 1)
        if not content:
            content = None
        if '\r\n' not in head:
            first_line = head
            hdrs = ''
        else:
            first_line, hdrs = head.split('\r\n', 1)
        headers = Headers.parse(hdrs)
        r = first_line.split(None, 2)
        if len(r) != 3:
            raise MessageParsingError("Bad first line: " + first_line)
        if r[0] == cls.version:
            code = int(r[1])
            reason = r[2]
            return Response(code, reason, headers, content)
        elif r[2] == cls.version:
            method = r[0]
            uri = URI.parse(r[1])
            return Request(method, uri, headers, content)
        else:
            raise MessageParsingError("Bad first line: " + first_line)


class Response(Message):
    def __init__(self, code, reason, headers=None, content=None):
        Message.__init__(self, headers, content)
        self.code = code
        self.reason = reason

    def __str__(self):
        r = []
        r.append('%s %s %s' % (self.version, self.code, self.reason))
        hdrs = str(self.headers)
        if hdrs:
            r.append(hdrs)
        r.append('\r\n')
        msg = '\r\n'.join(r)
        if self.content:
            msg += self.content
        return msg


class Request(Message):
    def __init__(self, method, ruri, headers=None, content=None):
        Message.__init__(self, headers, content)
        self.method = method
        self.ruri = ruri
        self.dialog = None
        self._has_totag = None
        self._response_totag = None

    def createResponse(self, code=None, reason=None):
        response = Response(code, reason)
        for x in ('from', 'to', 'call-id', 'cseq', 'via'):
            response.headers[x] = deepcopy(self.headers[x])
        if not self.has_totag:
            response.headers['to'].params['tag'] = self.response_totag
        if self.dialog:
            if 'record-route' in self.headers:
                response.headers['record-route'] = self.headers['record-route']
            contact_uri = URI.parse(self.dialog.local_target_uri)
            response.headers['contact'] = AddressHeader(uri=contact_uri)
        return response

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

