#!/usr/bin/env python

import cmd
import sys

from config        import SyncConfig
from editaliases   import EditAliases
from edittransport import EditTransport

class CLI( cmd.Cmd ):

   def __init__( self ):
      cmd.Cmd.__init__(self)
      self.config = SyncConfig()

   def do_editaliases( self, arg ):
      edit = EditAliases( self.config.getServers() )

   def help_editaliases( self ):
      print "This method allow user to edit aliases for email circuit"

   def do_edittransport( self, arg ):
      edit = EditTransport( self.config.getServers() )

   def help_edittransport( self ):
      print "This method allow user to edit transport in a given server for email circuit"

   def do_syncaliases( self, arg ):
      print "Sync Aliases"

   def do_synctransport( self, arg ):
      print "Sync Transport"

   def do_createuser( self, arg ):
      print "Create User, NOT IMPLEMENTED"

   def do_listservers( self, arg ):
      print "Servers Configured"

      print "| NAME\t\t| IP\t\t\t| USERNAME\t|"

      for serv in self.config.getServers():
         print "| %s\t| %s\t| %s\t\t|" % ( serv.getName(), serv.getIP(), serv.getUsername() )

   def do_quit( self, arg ):
      sys.exit(0)


c = CLI()
c.ruler = "#"


while 1:
   try:
      c.cmdloop()
   except ( KeyboardInterrupt ):
      print ""
      continue
   except ( SystemExit ):
      confirm = str( raw_input('Are you sure you want to exit <y/n>: ') )

      if confirm == 'y':
         sys.exit()
      else:
         pass 

