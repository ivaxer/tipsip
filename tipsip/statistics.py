# -*- coding: utf-8 -*-

from datetime import datetime

class Statistics(dict):
    def __init__(self):
        self.start_datetime = datetime.now()
        self.setUp()

    def setUp(self):
        self['start_at'] = str(self.start_datetime)
        self['http_received_requests'] = 0
        self['presence_put_statuses'] = 0
        self['presence_gotten_statuses'] = 0
        self['presence_dumped_statuses'] = 0
        self['presence_removed_statuses'] = 0
        self['presence_updated_statuses'] = 0
        self['presence_active_timers'] = 0

    def update_uptime(self):
        uptime = datetime.now() - self.start_datetime
        self['uptime'] = str(uptime)

    def dump(self):
        self.update()
        return self

    def update(self):
        self.update_uptime()

