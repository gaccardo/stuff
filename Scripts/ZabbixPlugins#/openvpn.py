#!/usr/bin/env python

from pybles import pybles

import sys

class OpenvpnMonitor(object):

	def __init__(self, status_file):
		self.status_file = status_file

	def __process_status_file(self):

		status_file_pointer = open(self.status_file, 'r')
		status_file_buffer = status_file_pointer.readlines()
		status_file_pointer.close()

		return status_file_buffer

	def __get_clients(self, status_process):
		clients_start = 0
		clients = list()

		for line in status_process:
			if line.startswith('ROUTING'):
				clients_start = 0

			if clients_start == 1:
				clients.append(line)

			if line.startswith('Common'):
				clients_start = 1

		return clients

	def __show_data(self, raw_clients):
		table = pybles.Pyble()

		table.add_column('user')
		table.add_column('remote')
		table.add_column('bytes transfer')
		table.add_column('??')
		table.add_column('connected since')

		for i in range(len(raw_clients)):
			raw_clients[i] = raw_clients[i].strip('\n')
			table.add_line(raw_clients[i].split(','))

		print "Connected clients: %s" % len(raw_clients)

		table.show_table()

	def run(self):
		self.__show_data(self.__get_clients(self.__process_status_file()))

	def count(self):
		return len(self.__get_clients(self.__process_status_file()))

if __name__ == '__main__':
	OvpnM = OpenvpnMonitor('/etc/openvpn/openvpn-status.log')
	exit_code = OvpnM.count()
	print exit_code
	sys.exit(exit_code)
