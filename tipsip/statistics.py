# -*- coding: utf-8 -*-

from datetime import datetime
from collections import defaultdict

class Statistics(defaultdict):
    def __init__(self):
        defaultdict.__init__(self, int)
        self.start_datetime = datetime.now()
        self.set_start_time()

    def set_start_time(self):
        self['start_at'] = str(self.start_datetime)

    def update_uptime(self):
        uptime = datetime.now() - self.start_datetime
        self['uptime'] = str(uptime)

    def dump(self):
        self.update()
        return self

    def update(self):
        self.update_uptime()

