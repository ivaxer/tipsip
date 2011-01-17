# -*- coding: utf-8 -*-

from random import choice
from string import ascii_letters, digits

def random_string(len):
    return "".join(choice(ascii_letters + digits) for _ in xrange(len))

