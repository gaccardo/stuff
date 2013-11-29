#!/usr/bin/env python

import time
import random

IPS = ['10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4', '10.0.0.5']
CODES = ['TCP_MISS/200', 'TCP_MISS/204', 'TCP_HIT/200']
METHODS = ['GET', 'POST']

class LogGenerator( object ):

	def __init__(self):
		self.file = 'access_generated.log'

	def run(self):
		f_p = open(self.file, 'w')
		LINES = 335000

		while LINES > 0:
			f_p.write("%.10f\t %s %s %s %s %s %s %s %s %s\n" % ( time.time(),
			                                                random.randint(50, 2000),
			                                                random.choice(IPS),
			                                                random.choice(CODES),
			                                                random.randint(50, 2000),
			                                                random.choice(METHODS),
			                                                'http://www.google.com',
			                                                '-',
			                                                'DIRECT/125.23.216.203',
			                                                'text/html'))
			LINES -= 1
		
		f_p.close()

if __name__ == '__main__':
	LG = LogGenerator()
	LG.run()
