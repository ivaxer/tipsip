# -*- coding: utf-8 -*-

from collections import namedtuple

from twisted.internet.protocol import DatagramProtocol

from message import Message


Address = namedtuple('Address', ('host', 'port', 'transport'))


class UDPTransport(DatagramProtocol):
    def __init__(self, listen_interface, messageReceivedCallback):
        self.messageReceivedCallback = messageReceivedCallback
        self.listen_interface = listen_interface

    def datagramReceived(self, data, (host, port)):
        if not data.strip():
            return
        msg = Message.parse(data)
        msg.received = Address(host, port, "UDP")
        msg.from_interface = self.listen_interface
        self.messageReceivedCallback(msg)

    def sendMessage(self, message, host, port):
        data = str(message)
        self.transport.write(data, host, port)

