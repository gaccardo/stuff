#!/usr/bin/env python

import httplib
import re
import sys

from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


h1 = httplib.HTTPConnection('10.0.0.227')
h1.request('GET', '/lb_status')
r1 = h1.getresponse()
out = r1.read()
s = MLStripper()
s.feed(out)

out = s.get_data()
out = out.split('\n')
out = [i for i in out if i]
out = [i for i in out if i]
out = [i.split(' ') for i in out if i]

exit = 0

if out[16][4] != 'up':
    exit += 1

if out[25][4] != 'up':
    exit += 1

sys.exit(exit)
