# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.python import log

def debug(msg):
    if __debug__:
        log.msg(msg)

class ServerTransaction(object):
    def __init__(self, request, transport_layer):
        self.state = "trying"
        self.transport_layer = transport_layer
        self.last_response = None
        self.method = request.method
        via = request.headers['via'][0]
        self.sent_by = via.sent_by
        self.branch = via.params['branch']

    @property
    def id(self):
        if self.method == 'ACK':
            method = 'INVITE'
        else:
            method = self.method
        return method, self.sent_by, self.branch

    def responseReceived(self, response):
        if response.code < 200:
            self.state = "proceeding"
        else:
            self.state = "completed"
        self.last_response = response
        self.sendResponse(response)

    def sendResponse(self, response):
        via = response.headers['via'][0]
        # XXX: resolv domain name
        host = via.host
        if not via.port:
            port = 5060
        else:
            port = int(via.port)
        self.transport_layer.sendMessage(response, host, port)

    def requestReceived(self, request):
        debug("Transaction %s: Received request" % str(self.id))
        if self.state == "trying":
            debug("Transaction %s: State trying. Discard request." % str(self.id))
        else:
            debug("Transaction %s: State %s. Resend last response (%s %s)." % (str(self.id), self.state, self.last_response.code, self.last_response.reason))
            self.sendResponse(self.last_response)


class TransactionLayer(object):
    T1 = 0.5
    timerJ = 64 * T1

    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.requestReceivedCallback = lambda x: None
        self._server_transactions = {}

    def requestReceived(self, request):
        if request.method not in ['ACK', 'INVITE']:
            self._nonInviteRequestRecieved(request)
        else:
            debug("NOT IMPLEMENTED: Invite server transaction not implemented")
            self.requestReceivedCallback(request)

    def sendResponse(self, response):
        transaction = response.transaction
        transaction.responseReceived(response)
        if transaction.state == "completed":
            reactor.callLater(self.timerJ, self.discardTransaction, transaction.id)

    def discardTransaction(self, id):
        self._server_transactions.pop(id)
        debug("Transaction %s: Discarded." % str(id))

    def _nonInviteRequestRecieved(self, request):
        transaction = self._matchRequest(request)
        if not transaction:
            debug("Create new non-INVITE server transaction")
            self._createServerTransaction(request)
            self.requestReceivedCallback(request)
        else:
            transaction.requestReceived(request)

    def _matchRequest(self, request):
        transaction = ServerTransaction(request, self.transport_layer)
        return self._server_transactions.get(transaction.id)

    def _createServerTransaction(self, request):
        transaction = ServerTransaction(request, self.transport_layer)
        request.transaction = transaction
        self._server_transactions[transaction.id] = transaction
        debug("Transaction: %s: Created." % str(transaction.id))
        return transaction

