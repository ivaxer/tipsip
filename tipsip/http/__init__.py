from twisted.web import resource, server

from stats import HTTPStats
from presence import HTTPPresence

from tipsip import statistics, presence_service

root = resource.Resource()
root.putChild("stats", HTTPStats())
root.putChild("presence", HTTPPresence(presence_service))

http_site = server.Site(root)

