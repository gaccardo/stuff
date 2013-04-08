#!/usr/bin/env python

from allowedrecipients import AllowedRecipients

import sshconnector
import time
import sys
import os

VERDE = '\033[92m'
AZUL  = '\033[94m'
FAIL  = '\033[91m'
END   = '\033[0m'
BOLD  = '\033[1m'

class EditAliases( object ):
   
   def __init__( self, servers ):
      self.conn        = sshconnector.SSHConnector()
      self.servers_map = list()    
      
      sys.stdout.write("Copying local aliases")
      os.system('cp /etc/aliases tmp/aliases')
      sys.stdout.write("\t%s[ OK  ]%s\n" % (VERDE, END))

      os.system('vim tmp/aliases')

      alw = AllowedRecipients( 'tmp/aliases', 'tmp/allowed' )
      alw.run()

      syncro = str( raw_input('Do you want to sync aliases now? <y/n>: ') )

      if syncro == 'y':

         for serv in servers:
         
            print ".............................."
            print "Syncing %s" % serv.getName()
            print ".............................."

            sys.stdout.write(" * Pushing aliases")
            self.conn.pushFile( serv, 'tmp/aliases', '/tmp/aliases' )
            sys.stdout.write("\t\t\t%s[ OK  ]%s\n" % (VERDE, END))

            sys.stdout.write(" * Configuring remote aliases")
            self.conn.executeCommand( serv, '/usr/bin/sudo /bin/cp /tmp/aliases /etc/aliases' )
            sys.stdout.write("\t\t%s[ OK  ]%s\n" % (VERDE, END))

            sys.stdout.write(" * Determining server network")
            sys.stdout.write("   \t%s[ %s ]%s\n" % (AZUL, serv.getNetwork().upper(), END) )

            if serv.getNetwork() == 'int':
               sys.stdout.write(" * Performing newaliases")
               self.conn.executeCommand( serv, '/usr/bin/sudo /usr/bin/newaliases' )
               sys.stdout.write("\t\t%s[ OK  ]%s\n" % (VERDE, END))
            if serv.getNetwork() == 'ext':
               sys.stdout.write(" * Performing allowed recipients")

               sys.stdout.write("\t%s[ OK  ]%s\n" % (VERDE, END))
         
            sys.stdout.write(" * Restating postfix")
            if serv.getOs() == 'centos':
               self.conn.executeCommand( serv, '/usr/bin/sudo /sbin/service postfix stop' )
               self.conn.executeCommand( serv, '/usr/bin/sudo /sbin/service postfix start' )
            elif serv.getOs() == 'openbsd':
               self.conn.executeCommand( serv, '/usr/bin/sudo /usr/local/sbin/postfix stop' )
               self.conn.executeCommand( serv, '/usr/bin/sudo /usr/local/sbin/postfix start' )

            sys.stdout.write("\t\t\t%s[ OK  ]%s\n" % (VERDE, END))
            

   def __getSelectedServer( self, index ):
      try:
         return [serv for serv in self.servers_map if serv['index'] == index][0]['server']
      except IndexError:
          return None

