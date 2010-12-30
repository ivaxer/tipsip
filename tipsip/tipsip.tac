# -*- coding: utf-8 -*-

from twisted.application import service, internet

from tipsip.http import http_site

application = service.Application("TipSIP service")
http_service = internet.TCPServer(18082, http_site)
http_service.setServiceParent(application)

