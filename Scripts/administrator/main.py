#!/usr/bin/env python

from pybles import pybles
from commands import servers, deploy, users_management, vpn_management
from includes import config
from sshconnector import sshconnector

import cmd
import sys

class AdministratorConsole( cmd.Cmd ):

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.servers_config = config.AdministratorConfig()
		self.servers = self.servers_config.get_servers()
		self.connected = None

	def do_quit(self, args):
		sys.exit(0)

	def do_exit(self, args):
		sys.exit(0)

	def do_servers(self, args):
		if len(args) > 0:
			args = args.split(' ')[0]
		else:
			args = None

		servers_cmd = servers.ServersCommand()
		servers_cmd.list(self.servers, args)

	def help_servers(self):
		print "servers [[GROUP]]"
		print "	[[GROUP]] - If passed as argument, only list servers belonging the given group"
 
	def do_serverinfo(self, args):
		ssh = sshconnector.SSHConnector()
		name = args.split(' ')[0]
		servers_cmd = servers.ServerinfoCommand()
		servers_cmd.get_info(name, self.servers_config, ssh)
		self.connected = ssh.server

	def help_serverinfo(self):
		print "serverinfo [SERVERNAME]"
		print "	[SERVERNAME] - Get info of the given server"

	def do_adduser(self, args):
		username = str(raw_input('username: '))
		groups = str(raw_input('Which server groups this user should be added? (comma separated): '))
		sudo = str(raw_input('This user needs root permissions? <y/N>: '))
		ssh = sshconnector.SSHConnector()
		management = users_management.UsersCommands()
		management.add(username, groups, sudo, self.servers_config, ssh, servers.SearchuserCommand())

	def do_createvpnprofile(self, args):
		username = str(raw_input('username: '))
		ssh = sshconnector.SSHConnector()
		management = vpn_management.VPNCommands()
		management.create_profile()

	def do_userhasvpn(self, args):
		username = str(raw_input('username: '))
		ssh = sshconnector.SSHConnector()
		management = vpn_management.VPNCommands()
		management.profile_exists()		

	def do_deluser(self, args):
		username = str(raw_input('username: '))
		groups = str(raw_input('Which server groups this user should be deleted? (comma separated): '))
		ssh = sshconnector.SSHConnector()
		management = users_management.UsersCommands()
		management.delete(username, groups, self.servers_config, ssh)

	def do_addusertogroup(self, args):
		username = str(raw_input('username: '))
		groups = str(raw_input('Which usergroup this user should be added? (comma separated): '))
		ssh = sshconnector.SSHConnector()
		management = users_management.UsersCommands()
		management.add_user_to_groups(username, groups, self.servers_config, ssh)
		
	def do_deluserfromgroup(self, args):
		username = str(raw_input('username: '))
		groups = str(raw_input('Which usergroup this user should be added? (comma separated): '))
		ssh = sshconnector.SSHConnector()
		management = users_management.UsersCommands()
		management.delete_user_from_groups(username, groups, self.servers_config, ssh)

	def do_searchuser(self, args):
		ssh = sshconnector.SSHConnector()
		name = args.split(' ')[0]
		servers_cmd = servers.SearchuserCommand()
		servers_cmd.search(name, self.servers, ssh)

	def help_searchuser(self, args):
		print "searchuser [USERNAME]"
		print "	[USERNAME] - Search in all servers if user is created"

	def do_deploy(self, args):
		pass


if __name__ == '__main__':
	cl = AdministratorConsole()
	cl.ruler = "$ "
	cl.prompt = "$ "

	while 1:
		try:
			cl.cmdloop()
		except (KeyboardInterrupt):
			print ":)"
			continue
		except (SystemExit):
			print ""
			sys.exit()