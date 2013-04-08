import os, sys
import paramiko
import config
import StringIO
import difflib

__version__   = "0.1"
__author__    = "Guido Accardo <gaccardo@gmail.com>"
__package__   = "SSHConnector 0.1"
__docformat__ = "restructuredtext"

VERDE = '\033[92m'
AZUL  = '\033[94m'
FAIL  = '\033[91m'
END   = '\033[0m'
BOLD  = '\033[1m'

class SSHConnector(object):
    """
    Remote administration throught ssh connections.

    ===================
    This class provides
    ===================

    * Add users to the system

    * Sincronize users

    * Sincronize rules of Packet Filter

    * Manage types of vpn users

    Configuration
    -------------


        groups = list()

        Have a list of lists. Any of this list is a dictionary of the form

        *{host:URL, username:allowed user, group:name of server group}*	  

    """

    def __init__(self):
	"""
	:version: 0.1 Development
	:status: development
	:contact: Guido Accardo gaccardo@gmail.com
	"""
	pass

    def executeCommand(self, server, username, cmd):
	"""
	Using server url and username allowed to login, execute cmd
	and return the stdout

	:param server: URL or IP of the **server**
	:param username: Username allowed to login in the **server**
	:param cmd: Command to run in the client, usually a call to authpf client

	:type server: String
	:type username: String
	:type cmd: String

	:return: The stdout of the server
	"""
        store = StringIO.StringIO()
        ssh = paramiko.SSHClient()
        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        ssh.connect(server, username=username, password=None)

        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.flush()

        return stdout.readlines(), stderr.readlines()

    def UserExists(self, where, username):
	"""
	Check if user exists in the system. That means if the user exists in all server
	of the group

	:param username: Username to test if exists in the system

	:type username: String

	:return: 
	   
	    * If user doesn't exists in any server, return *False*

	    * If user exists in all servers, return *True*

	    * If user only exists in some servers, return a dict with server info
	"""
	mal     = []
	total   = 0
        listado = ''
        if where in ['vpn', 'noc']:
            if where == 'vpn':
                listado = config.groups
            if where == 'noc':
                listado = config.groups_noc

	for group in listado:
	    for server in group:
		result, errors = self.executeCommand(server['host'], server['username'], "./authpf -U %s" % username)

		if result[0].rstrip() != "OK":
		    mal.append({'server':server['host'],'user':username,'group':server['group']})

		total += 1

	if total == len(mal):
	    return False

	if len(mal) > 0:
	    return mal
	else:
	    return True

    def GetUsernameByServer(self, server):
	"""
	Return username allowed to connect to the server


	:param server: URL or IP of a server of a group

	:type server: String

	:return: Username

	:rtype: String
	"""
        config.groups.append(config.groups_noc)
	for group in config.groups:
	    for server in group:
		return server['username']

    def AddUser(self, username, kind, where, server=None, auth=None):
	"""
	Add a new user in the system... if server and auth are passed as arguments,
	AddUser only add it in the specified server

	:param username: Username to add in the system
	:param kind: Base in the diferents types of rules
	:param server: **May be none** If present, only add *username* in *server*
	:param auth: *DEPRECATED*

	:type username: String
	:type kind: Int
	:type server: String 'OR' None
	:type auth: String 'OR' None

	:return: 
	
	    * If user was created succesfully, return *True*
	    * if user can't be created, return "Error"

	:rtype: Bool 'OR' String
	"""
        print username, kind, where
	if server is None:
	    print "Adding the user"
            if where == 'noc':
                listado = config.groups_noc
            elif where == 'vpn':
                listado = config.groups
            else:
                return False

	    for group in listado:
		for server in group:
		    result, errors = self.executeCommand(server['host'], server['username'], "./authpf -A %s %s %s" % (username, kind, where))

	return True

    def SyncUser(self, username, where):
	"""
	Get if username exists in all servers, if not add in remaining server.
	If usersname doesn't exists in any server, do nothing

	:param username: Username to be check if syncronized

	:type username: String

        :return: Text showing the result

	:rtype: String
	"""
	print "Sincronizando: %s para %s" % (username, where)

	result = self.UserExists(where, username)

	if result is True:
	    return "The user doesn't need sincronization" 

	if result is False:
	    return "The user doesn't exists in any server"

	for fault in result:
            print "Choose type for user %s in %s:" % (username, fault['server'])

	    response = int(raw_input('Choose Type: '))

	    este_result = self.AddUser( username=username, server=fault['server'], kind=response )
	    if este_result == True:
		print "User sincronized succesfully in %s" % fault['server']
	    else:
		print "There were errors synchronizing the user"

    def helper_delete(self, username, where):
	"""
	This is a helper method, where Deluser finished to get enough information, helper_delete connect to the server a do the final delete

	:param username: User to be deleted

	:type username: String

	:return:
	    * If were errors, return the error string
	    * If not, return True

	:rtype: Boolean 'OR' String
	"""
        listado = list()
        if where == 'noc':
            listado = config.groups_noc
        elif where == 'vpn':
            listado = config.groups

	for group in listado:
	    for server in group:
	        result, errors = self.executeCommand(server['host'], server['username'], "./authpf -D %s " % username)

    def DelUser(self, username, where):
	"""
	Given a username, delete it in the system

	:param username: User to be deleted

	:type username: String

	:return: 
            * If user was deleted, return True
	    * If not, return False

	:rtype: Boolean
	"""
    	result = self.UserExists(where, username)

	if result is False:
	    print "User doesn't exists"

	if result is not False and result is not True:
	    print "User is not sincronized, before delete, sync it"

	    choice = str(raw_input('Do you want sync %s <y|n>' % username))

	    if choice == 'y':
		sync = self.SyncUser(username)
		delete = self.helper_delete(username)
	    elif choice == 'n':
		print "Sync not accepted, user wont be deleted"
	    else:
		print "Option no recognised, user wont be deleted"

	if result is True:
	    delete = self.helper_delete(username, where)
	    print "User Deleted"

    def CheckConnections(self):
    	"""
	Check connection to all configured servers.

	:return: A message with the result of the check

	:rtype: String
	"""
        listado = [config.groups, config.groups_noc]
        for the_group in listado:
	    for group in the_group:
	        for server in group:
                    try:
		        self.executeCommand(server['host'], server['username'], "ls -l")
		        #print "%s [ ONLINE ]" % server['host']
		        print server['host'] + " \t\t[ " + BOLD + VERDE + "ONLINE" + END + " ]"
		    except:
		        #print "%s [ OFFLINE ]" % server['host']
		        print server['host'] + " \t\t[ " + BOLD + FAIL + "OFFLINE" + END + " ]"

    def SyncGroup(self, search_group):
	"""
	Given a group name, compares master and slave rules, if these are diferent, overwrite slave with master rules

	:param search_group: Name of group to be sincronized

	:type search_group: String

	:return: False if were errors

	:rtype: Boolean
	"""
	if search_group is "":
	    print FAIL + "Must supply a group name" + END
	    return False

	check = []
	for group in config.rules_groups:
	    for server in group:
		if server['group'] == search_group:
		    check.append(server)

	os.system("scp temp/%s.conf %s@%s:" % (check[0]['host'], check[1]['username'], check[1]['host']))
	result, errors = self.executeCommand(check[1]['host'], check[1]['username'], "./authpf -GP")

	print "Rules sincronized"

    def CheckSync(self):
	"""
	Check if two servers of the same group are syncronized

	:return: A message with the result of the check

	:rtype: String
	"""
	for group in config.rules_groups:

	    grupo = []
	    os.system("rm -rf temp/*")

	    result, errors = self.executeCommand(group[0]['host'], group[0]['username'], "./authpf -SR")
	    os.system("scp %s@%s:~/pf.conf temp/%s.conf" % (group[0]['username'], group[0]['host'], group[0]['host']))

	    result, errors = self.executeCommand(group[1]['host'], group[1]['username'], "./authpf -SR")
	    os.system("scp %s@%s:~/pf.conf temp/%s.conf" % (group[1]['username'], group[1]['host'], group[1]['host']))

	    buff1 = open("temp/%s.conf" % group[0]['host'], "r")
	    content1 = buff1.readlines()
	    buff1.close()

	    buff2 = open("temp/%s.conf" % group[1]['host'], "r")
	    content2 = buff2.readlines()
	    buff2.close()

	    count = 0
	    for i in difflib.context_diff(content1, content2):
		count += 1

	    if count > 0:
		print "This are the diferences between files"

		for line in difflib.context_diff(content1, content2):
		    print line
	    else:
		print "Files are sincronized"


    def GetFile(self, server, user, ffrom, to):
        os.system("scp %s@%s:%s %s" % (user, server, ffrom, to)) 

    def PushFile(self, server, user, ffrom, to):
        os.system("scp %s %s@%s:%s" % (ffrom, user, server, to)) 
