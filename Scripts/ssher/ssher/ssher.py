#!/usr/bin/env python
#-*- conding: utf-8 -*-
import sys
import os
import getpass


from ssher import Config, Server
Config = Config.Config
Server = Server.Server
from pybles import pybles
Pyble  = pybles.Pyble


class SSHER( object ):

    def __init__( self ):

        try:
            f = open('/home/%s/.ssher.cfg' % getpass.getuser(), 'r')
        except:
            print "Please, before use configure ~/.ssher.cfg"
            sys.exit(-1)

        self.config  = Config('/home/%s/.ssher.cfg' % getpass.getuser())
        self.servers = list()

    def __generateHosts( self ):
        index = 0
        for server in self.config.get_servers():
            self.servers.append( Server( index,
                                         server['username'], 
                                         server['hostname'],
                                         server['ip'],
                                         server['tunnel'],
                                         server['port'],
                                       ))

            index += 1

        return index

    def __showServersList( self, pro=False ):
	PB = Pyble()

	PB.add_column('ID')
	PB.add_column('HOSTNAME')
	PB.add_column('IP')
	PB.add_column('USERNAME')
	PB.add_column('TUNNEL')
	PB.add_column('PORT')

	for server in self.servers:
	    PB.add_line([server.get_id(), server.get_hostname(), server.get_ip(),
                         server.get_username(), server.get_tunnel(), server.get_port()])

	PB.show_table()

    def __getServerById( self, id ):
        for server in self.servers:
            if server.id == id:
                return server

    def __sshConnect( self, server ):
        if server.get_tunnel() == 'None':
            if server.get_port() != 'None':
                os.system( "ssh %s@%s -p %s" % ( server.get_username(), server.get_ip(), server.get_port() ) )

        else:
            print "ssh %s@%s -L %s" % ( server.get_username(), 
                                        server.get_ip(),
                                        server.get_tunnel()
                                      )
            if server.get_port() != 'None':
                os.system( "ssh %s@%s -L %s" % ( server.get_username(), 
                                                 server.get_ip(),
                                                 server.get_tunnel() ) )
            else:
                os.system( "ssh %s@%s -L %s -p %s" % ( server.get_username(), 
                                                 server.get_ip(),
                                                 server.get_tunnel(),
                                                 server.get_port() ) )

    def main( self, args ):
        count = self.__generateHosts()

        try:
            if args[1]   == '-l':
                self.__showServersList()
                return 0
            if args[1]   == '-L':
                self.__showServersList(pro=True)
                return 0
            elif args[1] == '-h':
                print "SSHer"
                print "  -h - Show this help"
                print "  -l - List available servers"
                print "  -L - List available servers (special still in devel)"
                print "NONE - List available servers"
                print "  id - Start connection number id"
                return 0
            else:
                try:
                    if int( args[1] ) >= count:
                        print "Server not found"
                        return -1
                    else:
                        server = self.__getServerById( int( args[1] ) )
                        print "establishing connection to: %s" % server
                        self.__sshConnect( server )
                except ValueError:
                    print "Invalid option"
                    return -1
        except IndexError:
            self.__showServersList()


if __name__ == '__main__':
    ssher = SSHER()

    sys.exit( ssher.main( sys.argv ) )
