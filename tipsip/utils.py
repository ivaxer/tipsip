# -*- coding: utf-8 -*-

from random import choice
from string import ascii_letters

from twisted.internet import reactor
from twisted.python import log

def seconds():
    return reactor.seconds()

def random_str(len):
    return "".join(choice(ascii_letters) for x in xrange(len))

msg = log.msg
warn = msg
dbg = msg
