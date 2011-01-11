# -*- coding: utf-8 -*-

from copy import deepcopy

from twisted.internet import defer

from uri import URI
from header import Headers, generate_tag
from header import request_mandatory_headers


class Message(object):
    version = 'SIP/2.0'

    def __init__(self):
        self.received_addr = None
        self.received_iface = None
        self.content = None
        self.headers = Headers()


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


class Request(Message):
    _dialog_store = None

    def __init__(self, method, ruri):
        Message.__init__(self)
        self.method = method
        if isinstance(ruri, basestring):
            self.ruri = URI.parse(ruri)
        else:
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
        d.local_target_uri = str(self.received_iface)
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

    def __str__(self):
        r = []
        r.append('%s %s %s' % (self.method, self.ruri, self.version))
        hdrs = str(self.headers)
        if hdrs:
            r.append(hdrs)
        r.append('\r\n')
        return '\r\n'.join(r)

