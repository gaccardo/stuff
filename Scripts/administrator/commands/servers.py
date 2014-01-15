from pybles import pybles

class ServersCommand(object):

	def list(self, servers, group=None):
		table = pybles.Pyble()

		table.add_column('Name')
		table.add_column('IP')
		table.add_column('Username')
		table.add_column('Port')
		table.add_column('Groups')

		for server in servers:
			if group is None or group in server.get_groups():
				table.add_line([server.get_name(), server.get_ip(), 
					              server.get_username(), server.get_port(),
					              ', '.join(server.get_groups())])

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

class SearchuserCommand(object):

	def __process_users(self, homes):
		users = list()
		for home in homes['stdin']:
			users.append(home.strip())

		return users

	def search(self, user, servers, sshconnector):
		for server in servers:
			tmp_conn = sshconnector.connect(server)

			try:
				users = sshconnector.cmd('ls /home/')
				if user in self.__process_users(users):
					print "%s has been found in %s" % (user, server.get_name())
			except:
				print "Server status: [ OFFLINE ]"

	def raw_search(self, user, servers, sshconnector):
		found = list()
		notfound = list()
		for server in servers:
			tmp_conn = sshconnector.connect(server)

			try:
				users = sshconnector.cmd('ls /home/')
				if user in self.__process_users(users):
					found.append(server)
				else:
					notfound.append(server)
			except:
				notfound.append(server)

		return {'found': found, 'notfound': notfound}