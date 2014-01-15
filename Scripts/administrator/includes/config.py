from ConfigParser import ConfigParser
from sshconnector import server

class AdministratorConfig(object):

	def __init__(self):
		config = ConfigParser()
		config.read('/home/guido/Documents/Developments/stuff/Scripts/administrator/servers.cfg')
		self.servers = list()

		for serv in config.sections():
			self.servers.append(server.Server(serv,
			                                  config.get(serv, 'ip'),
			                                  config.get(serv, 'username'),
			                                  config.get(serv, 'port'),
			                                  config.get(serv, 'groups')))

	def get_server_by_name(self, name):
		for server in self.servers:
			if name == server.get_name():
				return server

		return None

	def get_servers_by_group(self, group):
		servers = list()
		for server in self.servers:
			if group in server.get_groups():
				servers.append(server)

		return servers

	def get_servers(self):
		return self.servers