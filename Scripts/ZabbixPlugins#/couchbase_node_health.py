#!/usr/bin/env python
import sys
import subprocess

COUCHBASE_PATH_CLI = '/opt/couchbase/bin/couchbase-cli'

COUCHBASE_RETURN_CODES = {'status': {'active': 0, 
                                     'inactive': 1},
                          'health': {'healthy': 2,
                                     'unhealty': 3}}

class CouchNodeHealth(object):

	def __init__(self, ip, port, mode, user, passwd):
		self.ip = ip
		self.port = port
		self.mode = mode
		self.user = user
		self.passwd = passwd

	def __get_couchbase_info(self):
		stdout = subprocess.check_output([COUCHBASE_PATH_CLI, 
			                                'server-list', 
                                                        '-c', '%s:%s' % (self.ip, self.port),
			                                '-u', self.user,
			                                '-p', self.passwd])
		
		stdout = stdout.split('\n')
		stdout.pop()

		return stdout

	def __process_mode(self, servers):
		for server in servers:
			parts = server.split(' ')
			if self.ip == parts[1].split(':')[0]:
				if self.mode == 'status':
					return parts[3]
				elif self.mode == 'health':
					return parts[2]
				else:
					return None

	def __zabbix_return_code(self, code, mode):
		return COUCHBASE_RETURN_CODES[mode][code]	

	def run(self):
		code = self.__zabbix_return_code(self.__process_mode(self.__get_couchbase_info()), self.mode)
		print code
		sys.exit(code)


if __name__ == '__main__':
	"""
	MODE:
	 * health
	 * status
	"""
	CNH = CouchNodeHealth(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
	CNH.run()

