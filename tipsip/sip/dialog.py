# -*- coding: utf-8 -*-

import json

from twisted.internet import defer

from message import Request


class Dialog(object):
    def __init__(self, local_tag=None, remote_tag=None, callid=None, local_cseq=None,
            remote_cseq=None, local_uri=None, remote_uri=None, local_target_uri=None,
            remote_target_uri=None):
        self.local_tag = local_tag
        self.remote_tag = remote_tag
        self.callid = callid
        self.local_cseq = local_cseq or 0
        self.remote_cseq = remote_cseq
        self.local_uri = local_uri
        self.remote_uri = remote_uri
        self.local_target_uri = local_target_uri
        self.remote_target_uri = remote_target_uri

    def createRequest(self, method):
        raise NotImplementedError

    def serialize(self):
        r = {}
        r['local_tag'] = self.local_tag
        r['remote_tag'] = self.remote_tag
        r['callid'] = self.callid
        r['local_cseq'] = self.local_cseq
        r['remote_cseq'] = self.remote_cseq
        r['local_uri'] = self.local_uri
        r['remote_uri'] = self.remote_uri
        r['local_target_uri'] = self.local_target_uri
        r['remote_target_uri'] = self.remote_target_uri
        return json.dumps(r)

    @staticmethod
    def parse(s):
        r = json.loads(s)
        d = Dialog()
        d.local_tag = r['local_tag']
        d.remote_tag = r['remote_tag']
        d.callid = r['callid']
        d.local_cseq = r['local_cseq']
        d.remote_cseq = r['remote_cseq']
        d.local_uri = r['local_uri']
        d.remote_uri = r['remote_uri']
        d.local_target_uri = r['local_target_uri']
        d.remote_target_uri = r['remote_target_uri']
        return d

    @property
    def id(self):
        return self.callid, self.local_tag, self.remote_tag


class DialogStore(object):
    dialogs_table = 'sys:dialogs'

    def __init__(self, storage):
        self.storage = storage

    @defer.inlineCallbacks
    def find(self, id):
        key = self._tokey(id)
        try:
            d = yield self.storage.hget(self.dialogs_table, key)
        except KeyError:
            defer.returnValue(None)
        defer.returnValue(Dialog.parse(d))

    @defer.inlineCallbacks
    def add(self, dialog):
        key = self._tokey(dialog.id)
        yield self.storage.hset(self.dialogs_table, key, dialog.serialize())

    @defer.inlineCallbacks
    def remove(self, id):
        key = self._tokey(id)
        try:
            yield self.storage.hdel(self.dialogs_table, key)
        except KeyError:
            pass

    def _tokey(self, id):
        return ':'.join(id)

