from twisted.application import service, internet
from twisted.web import resource, server
from twisted.internet import defer

from tipsip import PresenceService
from tipsip import MemoryStorage
from tipsip.sip import Address, UDPTransport
from tipsip.sip.presence import SIPPresence
from tipsip.sip import DialogStore, Dialog

from tipsip.http import HTTPStats, HTTPPresence

storage = MemoryStorage()

presence_service = PresenceService(storage)

root = resource.Resource()
root.putChild("stats", HTTPStats())
root.putChild("presence", HTTPPresence(presence_service))

http_site = server.Site(root)

application = service.Application("TipSIP PresenceServer")
http_service = internet.TCPServer(18082, http_site)
http_service.setServiceParent(application)

dialog_store = DialogStore(storage)

udp_transport = UDPTransport(Address('127.0.0.1', 5060, 'UDP'))
sip_ua = SIPPresence(dialog_store, udp_transport, presence_service)

sip_service = internet.UDPServer(5060, udp_transport)
sip_service.setServiceParent(application)

