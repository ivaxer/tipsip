# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.python import log

def debug(msg):
    if __debug__:
        log.msg(msg)

class ServerTransaction(object):
    def __init__(self, request):
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


class TransactionLayer(object):
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

    def _nonInviteRequestRecieved(self, request):
        transaction = self._matchRequest(request)
        if not transaction:
            debug("Create new non-INVITE server transaction")
            self._createServerTransaction(request)
            self.requestReceivedCallback(request)
        else:
            debug("NOT IMPLEMENTED. DROP RETRANSMITTED REQUEST NOW")

    def _matchRequest(self, request):
        transaction = ServerTransaction(request)
        return self._server_transactions.get(transaction.id)

    def _createServerTransaction(self, request):
        transaction = ServerTransaction(request)
        self._server_transactions[transaction.id] = transaction
        # XXX:
        reactor.callLater(3600, self._server_transactions.pop, transaction.id)
        debug("Transaction id: %s" % str(transaction.id))
        return transaction

