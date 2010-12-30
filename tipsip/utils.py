# -*- coding: utf-8 -*-

from random import choice
from string import ascii_letters

from twisted.internet import reactor
from twisted.python import log

def seconds():
    return reactor.seconds()

def random_str(len):
    return "".join(choice(ascii_letters) for x in xrange(len))

def aggregated_presence(statuses):
    max_priority = None
    aggr_presence = {'status': 'offline'}
    for tag, status in statuses:
        cur_priority = status['priority']
        if cur_priority > max_priority:
            max_priority = cur_priority
            aggr_presence = status['presence']
        elif max_priority == cur_priority and aggr_presence and aggr_presence['status'] == 'offline' and status['presence']['status'] == 'online':
            aggr_presence = status['presence']
    return aggr_presence

msg = log.msg
warn = msg
dbg = msg
