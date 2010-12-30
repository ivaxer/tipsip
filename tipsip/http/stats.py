# -*- coding: utf-8 -*-

import json

from twisted.internet import defer
from twisted.web import resource

from tipsip import statistics

class HTTPStats(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        statistics['http_received_requests'] += 1
        return json.dumps(statistics.dump())

