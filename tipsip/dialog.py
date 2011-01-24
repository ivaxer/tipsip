# -*- coding: utf-8 -*-

import json

from twisted.internet import defer

from message import Request
from header import AddressHeader, CSeqHeader
from uri import URI


class Dialog(object):
    def __init__(self, local_tag=None, remote_tag=None, callid=None, local_cseq=None,
            remote_cseq=None, local_uri=None, remote_uri=None, local_target_uri=None,
            remote_target_uri=None, secure=False, route_set=None):
        self.local_tag = local_tag
        self.remote_tag = remote_tag
        self.callid = callid
        self.local_cseq = local_cseq or 0
        self.remote_cseq = remote_cseq
        self.local_uri = local_uri
        self.remote_uri = remote_uri
        self.local_target_uri = local_target_uri
        self.remote_target_uri = remote_target_uri
        self.secure = secure
        self.route_set = route_set

    def todict(self):
        d = self.__dict__.copy()
        if d['route_set']:
            d['route_set'] = json.dumps(d['route_set'])
        return d

    @classmethod
    def fromdict(cls, d):
        if d['route_set']:
            d['route_set'] = json.loads(d['route_set'])
        dialog = cls()
        dialog.__dict__ = d.copy()
        return dialog

    @property
    def id(self):
        return self.callid, self.local_tag, self.remote_tag

    def createRequest(self, method):
        if self.route_set:
            route = self.route_set[:]
            first_route = AddressHeader.parse(self.route_set[0])
            if not first_route.uri.lr:
                ruri = first_route.uri
                route.append(self.remote_target_uri)
            else:
                ruri = URI.parse(self.remote_target_uri)
        else:
            ruri = URI.parse(self.remote_target_uri)
            route = None
        request = Request(method, ruri)
        request.dialog = self
        h = request.headers
        if route:
            h['route'] = [AddressHeader.parse(s) for s in route]
        h['to'] = AddressHeader(uri=URI.parse(self.remote_uri), params={'tag': self.remote_tag})
        h['from'] = AddressHeader(uri=URI.parse(self.local_uri), params={'tag': self.local_tag})
        h['call-id'] = self.callid
        h['cseq'] = CSeqHeader(self.local_cseq, method)
        # XXX: follow 12.2.1.1 from rfc3261
        h['contact'] = AddressHeader.parse(self.local_target_uri)
        return request


class DialogStore(object):
    def __init__(self, storage):
        self.storage = storage

    @defer.inlineCallbacks
    def get(self, id):
        table = self._table(id)
        try:
            d = yield self.storage.hgetall(table)
        except KeyError:
            defer.returnValue(None)
        defer.returnValue(Dialog.fromdict(d))

    @defer.inlineCallbacks
    def put(self, dialog):
        table = self._table(dialog.id)
        d = dialog.todict()
        yield self.storage.hsetn(table, d)

    @defer.inlineCallbacks
    def remove(self, id):
        table = self._table(id)
        yield self.storage.hdrop(table)

    @defer.inlineCallbacks
    def incr_lcseq(self, id):
        table = self._table(id)
        yield self.storage.hincr(table, 'local_cseq', 1)

    @defer.inlineCallbacks
    def incr_rcseq(self, id):
        table = self._table(id)
        yield self.storage.hincr(table, 'remote_cseq', 1)

    def _table(self, id):
        return 'sys:dialogs:' + ':'.join(id)

