#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sshconector import SSHConnector

import cmd
import string, sys
import getpass
import config
import os

"""
User management for vpn connections
"""

__version__   = "0.1"
__author__    = "Guido Accardo <gaccardo@gmail.com>"


VERDE = '\033[92m'
AZUL  = '\033[94m'
FAIL  = '\033[91m'
END   = '\033[0m'
BOLD  = '\033[1m'

class CLI(cmd.Cmd):

    def __init__(self):
	cmd.Cmd.__init__(self)
	self.sshconnector = SSHConnector()

	print AZUL + "##################" + END
	print AZUL + "#" + VERDE + " AUTHPF HANDLER " + END + AZUL + "#" + END
	print AZUL + "##################" + END

	self.prompt = VERDE + "|authpf|$ " + END

        self.active = None
        self.slave  = None

    def do_quit(self, arg):
	sys.exit(0)

    def do_exit(self, arg):
        sys.exit(0)

    def do_deployclients(self, args):
        print AZUL + "Deploying authpf clientes" + END
        os.system("./deploy_clients.sh")

    def help_deployclients(self):
        print VERDE + "  :: deployclients ::" + END
        print "     send client to all configured firewalls"

    def help_quit(self):
	print VERDE + "  :: quit ::" + END
	print "     Close the program"

    def helper_where(self):
        db_file = open('profiles/db')
        db      = db_file.readlines()
        db_file.close()

        print FAIL + "  WHERE" + END

        for prof in db:
            print FAIL + "    %s - check if user exists in %s" % (prof.split('\n')[0].split('.')[0], prof.split('\n')[0].split('.')[0]) + END

        print " "
       
    def do_userexists(self, arg):
	arguments = arg.split(' ')

        if len(arguments) == 2:
            if arguments[0] == '' or arguments[1] == '':
                print FAIL + "userexists WHERE USERNAME" + END
                print " "

                self.helper_where()

                print FAIL + "  USERNAME" + END
                print FAIL + "    username to check"
                return False
        else:
            print FAIL + "userexists WHERE USERNAME" + END
            print " "

            self.helper_where()

            print FAIL + "  USERNAME" + END
            print FAIL + "    username to check"
            return False

        if len(arguments) == 2:
	    if self.sshconnector.UserExists(arguments[0], arguments[1]) is not True:
	        if self.sshconnector.UserExists(arguments[0], arguments[1]) is False:
		    print "The user doesn't exists in the system"
	        else:
		    print "The user doesn't exists in the following servers:"
		    print " [SERVER] [GROUP]"
		    for ns in self.sshconnector.UserExists(arguments[1], arguments[0]):
		        print "* %s %s" % (ns['server'], ns['group'])
	    else:
	        print "The user %s exists in the system %s" % (arguments[1], arguments[0])

    def help_userexists(self):
	print VERDE + "  :: userexists (where) (usuario)::" + END
	print "     Check if (user) exists in the system"
	print " "

    def do_adduser(self, arg):
        where    = ""
        username = ""

        if len(arg.split()) == 2:
            where    = arg.split(' ')[1]
            username = arg.split(' ')[0]
        else:
            print FAIL + "adduser USERNAME WHERE" + END
            print " "
            print FAIL + "  USERNAME" + END
            print FAIL + "    username to add" + END
            print " "

            self.helper_where()

            return False

        if self.helper_isValidDB(where):
            file_pro = open('profiles/%s.profile' % where)
            buffer   = file_pro.readlines()
            file_pro.close()
            counter  = 0

            print VERDE + where.upper() + END

            for conn in buffer:
               print FAIL + str(counter) + END, conn.split('/')[-1].split('\n')[0].split('/')[-1].split('.')[0]
               counter += 1
        else:
            print FAIL + "adduser USERNAME WHERE" + END
            print " "
            print FAIL + "  USERNAME" + END
            print FAIL + "    username to add" + END
            print " "

            self.helper_where()

            return False

	kind = int(raw_input('Choose type: '))
	result = self.sshconnector.AddUser(username, kind, where)

    def help_adduser(self):
	print VERDE + "  :: adduser ::" + END
	print "     Interactive proccess to add a new user in the system"
	print " "

    def do_addprofile(self, arg):

        if len(arg.split()) == 1:
            profile_name = arg.split(' ')[0]
        else:
            print FAIL + "addprofile PROFILENAME" + END
            print " "
            print FAIL + "  PROFILENAME" + END
            print FAIL + "    profile name to add"
            print " "

            return False

        file_pro = open('profiles/%s.profile' % profile_name, 'a')
        file_pro.close()
        file_db  = open('profiles/db', 'a')
        file_db.write('%s.profile' % profile_name)
        file_db.close()

        self.do_deployclients(0)

    def do_delprofile(self, arg):
        if len(arg.split()) == 1:
            profile_name = arg.split(' ')[0]
        else:
            print FAIL + "delprofile PROFILENAME" + END
            print " "
            print FAIL + "  PROFILENAME" + END
            print FAIL + "    profile name to delete"
            print " "

            return False

        if self.helper_isValidDB(profile_name):
            os.system("rm -rf profiles/%s.profile" % profile_name)

            file_db = open('profiles/db')
            db      = file_db.readlines()
            file_db.close()

            temp_db = open('/tmp/db','w')

            for line in db:
                if not '%s.profile' % profile_name == line.split('\n')[0]:
                    temp_db.write('%s.profile\n' % profile_name)

            temp_db.close()

            os.system('rm -f profiles/db')
            os.system('mv /tmp/db profiles/db')

    def do_addruleset(self, arg):

        if len(arg.split()) == 2:
            where   = arg.split()[1]
            ruleset = arg.split()[0]
        else:
            print FAIL + "addruleset RULESET WHERE" + END
            print " "
            print FAIL + "  RULESET" + END
            print FAIL + "    profile name to add"
            print " "

            self.helper_where()

            return False

        if self.helper_isValidDB(where):
            file_pro = open('profiles/%s.profile' % where)
            file_buf = file_pro.readlines()
            file_pro.close()
            if ("/u/etc/authpf-rules/%s.rules\n" % ruleset) not in file_buf:
                file_pro = open('profiles/%s.profile' % where, 'a')
                file_pro.write("/u/etc/authpf-rules/%s.rules\n" % ruleset)
                file_pro.close()

    def helper_isValidDB(self, name):
        db_file = open('profiles/db')
        db      = db_file.readlines()
        db_file.close()

        for entry in db:
           if name == entry.split('\n')[0] or "%s.profile" % name == entry.split('\n')[0]:
              return True

        return False

    def do_listprofiles(self, args):
        path = 'profiles/'

        for file in os.listdir(path):
            this_file = os.path.join(path, file)

            if self.helper_isValidDB(file):
                if this_file.split('.')[-1] == 'profile':
                    print VERDE + this_file.split('/')[-1].split('.')[0].upper() + END

                    file_pro = open(this_file)
                    buffer   = file_pro.readlines()
                    kinds    = buffer
                    file_pro.close()
                    ccc = 0

                    for ttt in buffer:
                        print FAIL + str(ccc) + END, ttt.split('\n')[0].split('/')[-1].split('.')[0]
                        ccc += 1

    def help_listprofiles(self):
        print VERDE + "  :: listprofiles ::" + END
        print "     Interactive proccess lists availables profiles divided in VPN and NOC"
        print " "

    def help_addprofile(self):
        print VERDE + "  :: addprofile <profilename> <where> ::" + END
        print "     Interactive proccess to add a new vpn profile in the system"
        print " "

    def do_syncuser(self, arg):
	username = arg.split(' ')[0]

	if username == '':
	    print FAIL + "Must supply username" + END
	    return False

	result = self.sshconnector.SyncUser(username)
	print result

    def help_syncuser(self):
	print VERDE + "  :: syncuser ::" + END
	print "       If user exists in some servers but no in all, this command"
	print "     create this user in remaining servers"

    def do_editclient(self, args):
        print "Edit client configuration"
        os.system("vim authpf")

    def help_editclient(self):
        print VERDE + " :: editclient ::" + END
        print "    edit client source code"

    def do_showconfig(self, args):
	print AZUL + "####################################" + END
	print AZUL + "#" + END + VERDE  + "         AUTHPF Servers           " + END + AZUL + "#" + END
	print AZUL + "####################################" + END
        for the_group in [config.groups, config.groups_noc]:
	    for group in config.groups:
	        for server in group:
	    	    print FAIL + "####################################" + END
		    print FAIL + "#"+END+" Server: %s" % server['host']
		    print FAIL + "#"+END+" User: %s" % server['username']
		    print FAIL + "#"+END+" Group: %s" % server['group']
		    print FAIL + "####################################" + END

	print AZUL + "####################################" + END
	print AZUL + "#" + END + VERDE + "            PF Servers            " + END + AZUL + "#" + END
	print AZUL + "####################################" + END
	for group in config.rules_groups:
	    for server in group:
		print FAIL + "####################################" + END
		print FAIL + "#"+END+" Server: %s" % server['host']
		print FAIL + "#"+END+" User: %s" % server['username']
		print FAIL + "#"+END+" Group: %s" % server['group']
		print FAIL + "####################################" + END
	
    def help_showconfig(self):
	print VERDE + "  :: showconfig ::" + END
	print "     Show all servers configured in the system"

    def do_deluser(self, arg):
        if len(arg.split(' ')) == 2:
    	    username = arg.split(' ')[0]
            where    = arg.split(' ')[1]
        else:
            print FAIL + "deluser USERNAME WHERE" + END
            print " "
            print FAIL + "  USERNAME" + END
            print FAIL + "    username to add" + END
            print " "
            print FAIL + "  WHERE" + END
            print FAIL + "    vpn - del username from vpn system"
            print FAIL + "    noc - del username from noc system"
            return False

	result = self.sshconnector.DelUser(username, where)

    def help_deluser(self):
	print VERDE + "  :: deluser [username] ::" + END
	print "     Delete user in the system"

    def do_checkconnections(self, arg):
	print "Checking connections to the servers"

	result = self.sshconnector.CheckConnections()

    def help_checkconnections(self):
	print VERDE + " :: checkconnections ::" + END
	print "    Check connections to all configured servers"

    def helper_getgroup(self, given_group):
        for group in config.rules_groups[0]:
            if group[0] == given_group:
                return group

        return false

    def helper_getactive(self, group):
        floating_ip  = group[3]
        stoud, sterr = self.sshconnector.executeCommand(floating_ip, "syncker", "hostname")
        only_name    = stoud[0].split('.')[0]
        f_only_name  = group[1]['host'].split('.')[0].upper()

        if   only_name == f_only_name:
            self.active = group[1]
            self.slave  = group[2]
            return group[1]['host']
        elif only_name == f_only_name:
            self.active = group[2]
            self.slave  = group[1]
            return group[2]['host']
        else:
            return None

    def helper_getpf(self, data):
        self.sshconnector.executeCommand(data['host'], data['username'], "./authpf -SR")
        self.sshconnector.GetFile(data['host'], data['username'], "~/pf.conf", "/tmp/pf.tmp")
        os.system("vim /tmp/pf.tmp")

    def helper_pushpf(self, data):
        self.sshconnector.PushFile(data['host'], data['username'], "/tmp/pf.tmp", "~/pf.conf")
        self.sshconnector.executeCommand(data['host'], data['username'], "./authpf -GP")
        stdout, stderr = self.sshconnector.executeCommand(data['host'], data['username'], "./authpf --FakeLoad")

        try:
            if stderr[0].split('\n')[0] == "":
                return True
            else:
                print stderr[0]
                return False
        except IndexError, e:
            return True

    def helper_restorepf(self, data):
        self.sshconnector.executeCommand(data['host'], data['username'], "./authpf --Restore")

    def helper_backuppf(self, data):
        self.sshconnector.executeCommand(data['host'], data['username'], "./authpf --Backup")

    def helper_loadpf(self, active, slave):
        self.sshconnector.executeCommand(active['host'], active['username'], "./authpf --LoadRules")

        try:
            self.sshconnector.PushFile(slave['host'], slave['username'], "/tmp/pf.tmp", "~/pf.conf")
            self.sshconnector.executeCommand(slave['host'], slave['username'], "./authpf -GP")
            self.sshconnector.executeCommand(slave['host'], slave['username'], "./authpf --LoadRules")
        except:
            print BOLD + AZUL + " El servidor secundario esta apagado, solo se hicieron cambios en el primario"

    def do_editrules(self, arg):
        """
              ('BUE1FWX31',
               {'host':'bue1fw031.core.sec','username':'syncker','group':'rules_bue'},
               {'host':'bue1fw131.core.sec','username':'syncker','group':'rules_bue'},
               '10.2.0.26'
              ),
        """

        print VERDE + "Edit Rules" + END

        if len(arg) == 0:
            print VERDE + " Firewalls " + END
            for group in config.rules_groups[0]:
                print "  " + group[0] + " [" + FAIL + group[3]  + END + "] "
                print "   " + group[1]['host']
                print "   " + group[2]['host']
        else:
            server = str(arg.split(" ")[0])
            data   = self.helper_getgroup(server)

            if data is not False:
                print VERDE + " Grupo " + END + server
                active = self.helper_getactive(data)
                self.helper_backuppf(self.active)
                print VERDE + " Activo " + END + active
                pf     = self.helper_getpf(self.active)

                if not self.helper_pushpf(self.active):
                    print FAIL + " ERROR EN EL ARCHIVO PF. NO SE APLICARON LOS CAMBIOS " + END
                    self.helper_restorepf(self.active)
                    return False
                else:
                    print VERDE + " No hay errors en el archivo, se procede a la carga " + END
                    self.helper_loadpf(self.active, self.slave)

                    self.helper_commit()

    def helper_commit(self):
        os.system("cp -rf /tmp/pf.tmp repos/configuraciones/firewalls/%s/" % server)
        os.system("svn ci repos/ -m %s" % server)
        print "Commit realizado con exito"
        

    def help_help(self):
	print VERDE + "  :: help ::" + END
	print "     Show documented and uncommented commands"
	print " "
	print "  :: help [command] ::"
	print "     Show help of [command]"

cl = CLI()
cl.ruler = "#"

while 1:
    try:
	cl.cmdloop()
    except (KeyboardInterrupt):
	print ""
        continue
    except (SystemExit):
        print "Best Regards"
        sys.exit()
