from twisted.application import service, internet
from twisted.web import resource, server

from tipsip import PresenceService
from tipsip import MemoryStorage
from tipsip.sip import Address, UDPTransport

from tipsip.http import HTTPStats, HTTPPresence

presence_service = PresenceService(MemoryStorage())

root = resource.Resource()
root.putChild("stats", HTTPStats())
root.putChild("presence", HTTPPresence(presence_service))

http_site = server.Site(root)

application = service.Application("TipSIP PresenceServer")
http_service = internet.TCPServer(18082, http_site)
http_service.setServiceParent(application)

def print_debug(msg):
    print "%s: %s" % (msg, str(msg))

udp_transport = UDPTransport(Address('127.0.0.1', 5060, 'UDP'), print_debug)
sip_service = internet.UDPServer(5060, udp_transport)
sip_service.setServiceParent(application)
