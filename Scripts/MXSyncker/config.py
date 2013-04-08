#!/usr/bin/env python

import ConfigParser
import Server


class SyncConfig( object ):

   def __init__( self ):
      config_file = 'sync.cfg'
      self.config = ConfigParser.RawConfigParser()
      self.config.read( config_file )

   def getNames( self ):
      return self.config.sections()
 
   def getServers( self ):
      names   = self.getNames()
      servers = list()

      for name in names:
         tmp_server = Server.Server( name, self.config.get( name, 'ip' ), self.config.get( name, 'username' ), self.config.get( name, 'os'), self.config.get( name, 'network' ) )
         servers.append( tmp_server )

      return servers
