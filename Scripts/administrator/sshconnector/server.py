class Server(object):

	def __init__(self, name, ip, username, port=None):
		self.name = name
		self.ip = ip
		self.username = username
		self.port = port

		if port is None:
			self.port = 22

	def get_ip(self):
		return self.ip

	def get_name(self):
		return self.name

	def get_username(self):
		return self.username

	def get_port(self):
		return self.port

	def set_ip(self, ip):
		self.ip = ip

	def set_name(self, name):
		self.name = name

	def set_username(self, username):
		self.username = username

	def set_port(self, port):
		self.port = port

	def __str__(self):
		return "<Server(name='%s', ip='%s', username='%s', port='%s')>" % (self.name, 
			                                                                 self.ip,
			                                                                 self.username,
			                                                                 self.port)