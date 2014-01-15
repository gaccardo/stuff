import os, sys
import paramiko
import StringIO

class SSHConnector(object):


	def connect(self):
		store = StringIO.StringIO()
		ssh = paramiko.SSHClient()
		ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
		ssh.connect(server, username=username, password=None)

		#stdin, stdout, stderr = ssh.exec_command(cmd)
		#stdin.flush()

		#return stdout.readlines(), stderr.readlines()

		return ssh
