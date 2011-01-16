# -*- coding: utf-8 -*-

from collections import defaultdict

from twisted.internet import reactor, defer

from tipsip import aggregate_status
from ua import SIPUA, SIPError
from header import Header


s2p = {
        'online':   'open',
        'offline':  'closed',
        }

def status2pidf(resource, statuses):
    pidf = []
    a = pidf.append
    status = aggregate_status(statuses)
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a('<presence xmlns="urn:ietf:params:xml:ns:pidf" entity="pres:%s">' % resource)
    s = s2p[status['presence']['status']]
    a('\t<tuple id="%s">' % resource)
    a('\t\t<status>')
    a('\t\t\t<basic>%s</basic>' % s)
    a('\t\t</status>')
    a('\t\t<contact>sip:%s</contact>' % resource)
    a('\t</tuple>')
    a('</presence>')
    return '\n'.join(pidf)


class SIPPresence(SIPUA):
    def __init__(self, dialog_store, transport, presence_service):
        SIPUA.__init__(self, dialog_store, transport)
        presence_service.watch(self.statusChangedCallback)
        self.presence_service = presence_service
        self.watchers_by_resource = defaultdict(list)
        self.resource_by_watcher = {}
        self.watcher_expires_tid = {}

    def handle_PUBLISH(self, publish):
        raise NotImplementedError

    def handle_REGISTER(self, register):
        r = register.createResponse(200, 'OK')
        r.headers['expires'] = '3600'
        self.sendResponse(r)

    @defer.inlineCallbacks
    def handle_SUBSCRIBE(self, subscribe):
        if subscribe.headers.get('Event') != 'presence':
            response = subscribe.createResponse(489, 'Bad Event')
            response.headers['allow-event'] = 'presence'
            self.sendResponse(response)
        elif not subscribe.dialog and subscribe.has_totag:
            raise SIPError(404, 'Not Here')
        else:
            yield self.processSubscription(subscribe)

    def statusChangedCallback(self, resource, status):
        if resource not in self.watchers_by_resource:
            return
        for watcher in self.watchers_by_resource[resource]:
            self.notifyWatcher(watcher)

    @defer.inlineCallbacks
    def processSubscription(self, subscribe):
        expires = int(subscribe.headers['Expires'])
        if not expires and subscribe.dialog:
            watcher = subscribe.dialog.id
            yield self.notifyWatcher(watcher, status='terminated', expires=0)
            self.removeWatcher(watcher)
        elif subscribe.dialog:
            watcher = subscribe.dialog.id
            self.updateWatcher(watcher, expires)
            self.notifyWatcher(watcher, status='active', expires=expires, dialog=subscribe.dialog)
        else:
            if not subscribe.ruri.user:
                raise SIPError(404, 'Bad resource URI')
            resource = subscribe.ruri.user + '@' + subscribe.ruri.host
            yield self.createDialog(subscribe)
            watcher = subscribe.dialog.id
            self.addWatcher(watcher, resource, expires)
            self.notifyWatcher(watcher, status='active', expires=expires, dialog=subscribe.dialog)
        response = subscribe.createResponse(200, 'OK')
        response.headers['Expires'] = str(expires)
        self.sendResponse(response)

    def addWatcher(self, watcher, resource, expires):
        self.watchers_by_resource[resource].append(watcher)
        self.resource_by_watcher[watcher] = resource
        self.watcher_expires_tid[watcher] = reactor.callLater(expires, self.removeWatcher, watcher)

    def updateWatcher(self, watcher, expires):
        tid = self.watcher_expires_tid.get(watcher)
        if not tid:
            raise SIPError(404, "Not Found")
        tid.reset(expires)

    def removeWatcher(self, watcher):
        tid = self.watcher_expires_tid.get(watcher)
        if not tid:
            raise SIPError(404, 'Not Found')
        resource = self.resource_by_watcher.pop(watcher)
        self.watchers_by_resource[resource].remove(watcher)
        self.watcher_expires_tid.pop(watcher)
        if tid.active():
            tid.cancel()

    @defer.inlineCallbacks
    def notifyWatcher(self, watcher, pidf=None, dialog=None, status='active', expires=None):
        if pidf is None:
            resource = self.resource_by_watcher[watcher]
            statuses = yield self.presence_service.getStatus(resource)
            pidf = status2pidf(resource, statuses)
        if dialog is None:
            dialog = yield self.dialog_store.get(watcher)
            if not dialog:
                raise SIPError(500, "Server Internal Error")
        if expires is None:
            expires = self.watcher_expires_tid[watcher].getTime() - reactor.seconds()
            expires = int(expires)
        yield self.sendNotify(dialog, pidf, status, expires)

    @defer.inlineCallbacks
    def sendNotify(self, dialog, pidf, status, expires):
        notify = dialog.createRequest('NOTIFY')
        h = notify.headers
        h['subscription-state'] = Header(status, {'expires': str(expires)})
        h['content-type'] = 'application/pidf+xml'
        h['Event'] = 'presence'
        notify.content = pidf
        yield self.sendRequest(notify)

