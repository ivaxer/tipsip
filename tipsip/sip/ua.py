# -*- coding: utf-8 -*-

from twisted.internet import defer
from twisted.python import log

from message import Request, Response
from header import AddressHeader, ViaHeader
from uri import URI
from utils import random_string
from dialog import Dialog


def generate_branch():
    return "z9hG4bK" + random_string(7)


class SIPError(Exception):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason


class SIPUA(object):
    DEFAULT_UDP_PORT = 5060

    def __init__(self, dialog_store, transport):
        self.dialog_store = dialog_store
        self.transport = transport
        transport.messageReceivedCallback = self.messageReceived
        self._pending_requests = {}
        self._pending_finally = {}

    def messageReceived(self, message):
        if type(message) == Request:
            self.requestReceived(message)
        elif type(message) == Response:
            self.responseReceived(message)
        else:
            raise TypeError("Expected Request or Response")

    @defer.inlineCallbacks
    def requestReceived(self, request):
        if not request.isValid():
            raise SIPError("400", "Bad Request")
        try:
            yield self.handleRequest(request)
        except SIPError, e:
            self.sendResponse(request.createResponse(e.code, e.reason))
        except:
            self.sendResponse(request.createResponse(500, 'Server Internal Error'))
            raise

    def responseReceived(self, response):
        branch = response.headers['via'][0].params['branch']
        is_finally = response.code >= 200
        if branch in self._pending_requests:
            d = self._pending_requests[branch]
            wait_finally = self._pending_finally[branch]
            if is_finally or not wait_finally:
                d.callback(response)
                del self._pending_requests[branch]
                del self._pending_finally[branch]

    @defer.inlineCallbacks
    def handleRequest(self, request):
        yield self._matchDialog(request)
        method = request.method
        handler = getattr(self, "handle_%s" % method, self.handle_DEFAULT)
        yield handler(request)

    def handle_DEFAULT(self, request):
        raise SIPError(405, 'Method Not Allowed')

    def sendRequest(self, request, addr=None, wait_finally=True):
        self._createVia(request)
        route = request.headers.get('route')
        if route:
            route = route[0]
            host, port = route.uri.host, route.uri.port
        else:
            host, port = request.ruri.host, request.ruri.port
        if not port:
            port = DEFAULT_UDP_PORT
        if request.dialog:
            d = self.dialog_store.incr_lcseq(request.dialog.id)
        d = defer.Deferred()
        branch = request.headers['via'][0].params['branch']
        self._pending_requests[branch] = d
        self._pending_finally[branch] = wait_finally
        self.transport.sendMessage(request, host, port)
        return d

    def waitResponse(self, request, wait_finally=False):
        d = defer.Deferred()
        self._pending_requests[branch] = d
        self._pending_finally[branch] = wait_finally
        return d

    def sendResponse(self, response):
        via = response.headers['via'][0]
        # XXX: resolv domain name
        host = via.host
        if not via.port:
            port = self.DEFAULT_UDP_PORT
        else:
            port = int(via.port)
        self.transport.sendMessage(response, host, port)

    @defer.inlineCallbacks
    def createDialog(self, request):
        d = Dialog()
        r = request
        d.local_tag = r.response_totag
        d.remote_tag = r.headers['from'].params['tag']
        d.callid = r.headers['call-id']
        d.local_cseq = 0
        d.remote_cseq = int(r.headers['cseq'].number)
        d.local_uri = str(r.headers['to'].uri)
        d.remote_uri = str(r.headers['from'].uri)
        ifc = r.from_interface
        d.local_target_uri = ''.join(['sip:', ifc.host, ':', str(ifc.port), ' ;transport=', ifc.transport])
        d.remote_target_uri = str(r.headers['contact'][0].uri)
        yield self.dialog_store.put(d)
        r.dialog = d
        defer.returnValue(d)

    def _createVia(self, req):
        h = req.headers
        if 'via' not in h:
            h['via'] = []
        if len(h['via']):
            via = h['via'][0]
        else:
            via = ViaHeader()
            h['via'].append(via)
        via.params['branch'] = generate_branch()

    @defer.inlineCallbacks
    def _matchDialog(self, request):
        hdrs = request.headers
        if 'tag' in hdrs['t'].params:
            dialog_id = hdrs['call-id'], hdrs['to'].params['tag'], hdrs['from'].params['tag']
            dialog = yield self.dialog_store.get(dialog_id)
            if dialog:
                if hdrs['cseq'].number != dialog.remote_cseq + 1:
                    log.msg("Request CSeq mismatch with dialog.remote_cseq. Request call-id: %s, dialog: %s" % \
                            (hdrs['call-id'], dialog.todict()))
                else:
                    yield self.dialog_store.incr_rcseq(dialog.id)
                    request.dialog = dialog

