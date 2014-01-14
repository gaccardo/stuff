from pybles import pybles

class ServersCommand(object):

	def list(self, servers):
		table = pybles.Pyble()

		table.add_column('Name')
		table.add_column('IP')
		table.add_column('Username')
		table.add_column('Port')

		for server in servers:
			table.add_line([server.get_name(), server.get_ip(), 
				              server.get_username(), server.get_port()])

		table.show_table()


class ServerinfoCommand(object):

	def __process_users(self, homes):
		users = list()
		for home in homes['stdin']:
			users.append(home.strip())

		return users

	def __user_groups(self, users, server):
		table = pybles.Pyble()

		table.add_column('User')
		table.add_column('Has Root permissions?')

		for user in users:
			out = server.cmd('id %s' % user)
			table.add_line([user, 'sudo' in out['stdin'][0] or 'adm' in out['stdin'][0]])

		table.show_table()

	def get_info(self, name, config, sshconnector):
		server = config.get_server_by_name(name)

		if server is None:
			print "Server not found"
			return None

		print server
		sshconnector.connect(server)

		try:
			users = sshconnector.cmd('ls /home/')
			print "Server status: [ ONLINE ]"
		except:
			print "Server status: [ OFFLINE ]"
			return None

		print sshconnector.cmd('uname -a')['stdin'][0].strip()
		print "NOT system users: %s" % self.__process_users(users)

		self.__user_groups(self.__process_users(users), sshconnector)