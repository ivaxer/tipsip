# -*- coding: utf-8 -*-

from collections import namedtuple

from twisted.internet.protocol import DatagramProtocol
from twisted.python import log

from message import Message


Address = namedtuple('Address', ('host', 'port', 'transport'))


class UDPTransport(DatagramProtocol):
    def __init__(self, listen_interface):
        self.messageReceivedCallback = lambda x: None
        self.listen_interface = listen_interface

    def datagramReceived(self, data, (host, port)):
        if not data.strip():
            return
        log.msg("RECEIVED:\n" + data)
        msg = Message.parse(data)
        msg.received = Address(host, port, "UDP")
        msg.from_interface = self.listen_interface
        self.messageReceivedCallback(msg)

    def sendMessage(self, message, host, port):
        # XXX: do it for requests only
        self._fillVia(message)
        data = str(message)
        log.msg("SENT:\n" + data)
        self.transport.write(data, (host, port))

    def _fillVia(self, msg):
        via = msg.headers['via'][0]
        if via.transport:
            return
        via.transport = 'UDP'
        via.host = self.listen_interface.host
        via.port = self.listen_interface.port

