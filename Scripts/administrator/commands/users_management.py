from pybles import pybles

class UsersCommands(object):

	def add(self, username, groups, sudo, config, ssh, search):
		servers = list()

		if sudo == 'y' or sudo == 'Y' or sudo == 'yes':
			sudo = True
		else:
			sudo = False

		for group in groups.split(','):
			for server in config.get_servers_by_group(group):
				servers.append(server)

		table = pybles.Pyble()
		table.add_column('Server')
		table.add_column('Group')

		for server in servers:
			table.add_line([server.get_name(), ', '.join(server.get_groups())])

		print "You're about to add %s to the following servers in the groups: %s" % (username, groups)
		if sudo:
			print "* You will create %s with root permissions" % username

		table.show_table()
		contin = str(raw_input('Are you sure you want to continue? <y/N>: '))

		servers = search.raw_search(username, servers, ssh)

		for server in servers['found']:
			print "User %s already exists in %s" % (username, server.get_name())

		for server in servers['notfound']:
			print "Adding %s in %s" % (username, server.get_name())

	def delete(self, username, groups, config, ssh):
		pass

	def add_user_to_groups(self, username, groups, config, ssh):
		pass

	def delete_user_from_groups(self, username, group, config, ssh):
		pass