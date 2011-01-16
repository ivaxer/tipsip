# -*- coding: utf-8 -*-

import json

from twisted.internet import defer
from twisted.web import resource

from tipsip import stats

class HTTPStats(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        stats['http_received_requests'] += 1
        return json.dumps(stats.dump(), indent=4)

