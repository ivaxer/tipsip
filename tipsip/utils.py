# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.python import log

def seconds():
    return reactor.seconds()

def msg(*args, **kw):
    return log.msg(*args, **kw)

warn = msg
