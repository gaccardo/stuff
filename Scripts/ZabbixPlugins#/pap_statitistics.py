#!/usr/bin/env python

import sys
import json
import urllib

class PAPStats(object):

	def __init__(self, couchserver, port, mode):
		self.couchserver = couchserver
		self.port = port
		self.mode = mode

	def __get_clicks(self):
		url = "http://%s:%s/default/_design/clicks/_view/sum?connection_timeout=60000" % (self.couchserver, self.port)
		out = json.load(urllib.urlopen(url))

		return out['rows'][0]['value']

	def __get_prints(self):
		url = "http://%s:%s/default/_design/impressions_by_date/_view/count?stale=update_after&connection_timeout=60000" % (self.couchserver, self.port)
		out = json.load(urllib.urlopen(url))

		return out['rows'][0]['value']

	def run(self):
		if self.mode == 'clicks':
		  print self.__get_clicks()
		  sys.exit(self.__get_clicks())
		elif self.mode == 'prints':
		  print self.__get_prints()
		  sys.exit(self.__get_prints())


if __name__ == '__main__':
	#PS = PAPStats('10.0.0.54', '8092', 'clicks')
	PS = PAPStats('10.0.0.54', '8092', 'prints')
	PS.run()