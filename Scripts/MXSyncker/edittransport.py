#!/usr/bin/env python

import sshconnector
import os
import sys
import time

from synctransport import SyncTransport

VERDE = '\033[92m'
AZUL  = '\033[94m'
FAIL  = '\033[91m'
END   = '\033[0m'
BOLD  = '\033[1m'

class EditTransport( object ):
   
   def __init__( self, servers ):
      self.conn        = sshconnector.SSHConnector()
      self.servers_map = list()    
      count            = 0
      
      for serv in servers:
          self.servers_map.append( { 'index'  : count, 
                                     'server' : serv }
                                 )
          count += 1
                     
      for serv in self.servers_map:
          print serv['index'], serv['server'].getName()
      
      selection  = int( raw_input(': INDEX :> ') )
      cur_server = self.__getSelectedServer( selection )

      
      if cur_server is not None:
         self.conn.getFile( cur_server, '/etc/postfix/transport', 'transport-%s' % cur_server.getName() )
         os.system( 'vim tmp/transport-%s' % cur_server.getName() )
      else:
         print "Selection Error: The index %s server is not configured" % selection

      syncro = str( raw_input('Do you want to sync transport now? <y/n>: ') )

      if syncro == 'y':
         sys.stdout.write("Autosync for %s \n" % cur_server.getName())
         sys.stdout.write("Copying remote transport ... ")
         sys.stdout.write("\t%s[ OK ]%s\n" % (VERDE, END))
         st = SyncTransport( cur_server, 'tmp/transport-%s' % cur_server.getName(), '/tmp/' )
         st.doAutoSync()
         sys.stdout.write("\t[ OK ]\n")

         sys.stdout.write("Backuping remote transport ... ")
         std_in, std_err = self.conn.executeCommand( cur_server, "/usr/bin/sudo /bin/cp /etc/postfix/transport /tmp/transport-%s" % time.strftime('%d%m%Y_%H%M%S') )
         sys.stdout.write("\t%s[ OK ]%s\n" % (VERDE, END))

         sys.stdout.write("Remaping remote transport ... ")
         self.conn.executeCommand( cur_server, "/usr/bin/sudo /bin/cp /tmp/transport-%s /etc/postfix/transport" % cur_server.getName() )
         self.conn.executeCommand( cur_server, "/usr/bin/sudo /usr/local/sbin/postmap /etc/postfix/transport" )
         sys.stdout.write("\t%s[ OK ]%s\n" % (VERDE, END))

         sys.stdout.write("Reloading remote postfix ... ")

         if cur_server.getOs() == 'centos':
            self.conn.executeCommand( cur_server, "/usr/bin/sudo /sbin/service postfix stop" )
            self.conn.executeCommand( cur_server, "/usr/bin/sudo /sbin/service postfix start" )
         elif cur_server.getOs() == 'openbsd':
            self.conn.executeCommand( cur_server, "/usr/bin/sudo /usr/local/sbin/postfix stop" )
            self.conn.executeCommand( cur_server, "/usr/bin/sudo /usr/local/sbin/postfix start" )

         sys.stdout.write("\t%s[ OK ]%s\n" % (VERDE, END))
      else:
         print "* Remember that you can manually sync transports any time you want by using manualtransportsync *"
      
   def __getSelectedServer( self, index ):
      try:
         return [serv for serv in self.servers_map if serv['index'] == index][0]['server']
      except IndexError:
          return None
