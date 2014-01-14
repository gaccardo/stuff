#!/usr/bin/env python

from pybles import pybles
from commands import servers, deploy
from includes import config
from sshconnector import sshconnector

import cmd
import sys

class AdministratorConsole( cmd.Cmd ):

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.servers_config = config.AdministratorConfig()
		self.servers = self.servers_config.get_servers()

	def do_quit(self, args):
		sys.exit(0)

	def do_exit(self, args):
		sys.exit(0)

	def do_servers(self, args):
		servers_cmd = servers.ServersCommand()
		servers_cmd.list(self.servers)

	def do_serverinfo(self, args):
		ssh = sshconnector.SSHConnector()
		name = args.split(' ')[0]
		servers_cmd = servers.ServerinfoCommand()
		servers_cmd.get_info(name, self.servers_config, ssh)

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