import os
import paramiko

class SSHConnector(object):

	def __init__(self):
		self.connection = None
		self.server = None
		self.username = None

	def connect(self, server):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(server.ip, username=server.username, password=None, port=int(server.port))
		except Exception, e:
			return None

		self.connection = ssh
		self.server = server

		return True

	def cmd(self, cmd):
		try:
			stdin, stdout, stderr = self.connection.exec_command(cmd)
		except AttributeError:
			self.connect(self.server)
			stdin, stdout, stderr = self.connection.exec_command(cmd)

		stdin.flush()

		return {'stdin': stdout.readlines(),
		        'stderr': stderr.readlines()}

	def disconnect(self):
		self.connection.close()