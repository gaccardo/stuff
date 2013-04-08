#!/usr/bin/env python

import sshconnector
import sys

from config import SyncConfig

class SyncTransport( object ):

   def __init__( self, server, local_file=None, remote_file=None ):
      self.conn        = sshconnector.SSHConnector()
      self.server      = server
      self.local_file  = local_file
      self.remote_file = remote_file
      self.config      = SyncConfig()
      self.servers_map = list()

   def doAutoSync( self ):
      self.conn.pushFile( self.server, self.local_file, self.remote_file )

   def doInteractiveSync( self ):
      count = 0

      for serv in self.config.getServers():
         self.servers_map.append( { 'index'  : count,
                                    'server' : serv }
                                )
         count += 1

      for serv in self.servers_map:
          print serv['index'], serv['server'].getName()

      selection  = int( raw_input(': INDEX :> ') )
      cur_server = self.__getSelectedServer( selection )

      self.conn( cur_server, 'tmp/transport-%s' % cur_server.getName(), '/tmp/transport-%s' % cur_server.getName() )

   def __getSelectedServer( self, index ):
      try:
         return [serv for serv in self.servers_map if serv['index'] == index][0]['server']
      except IndexError:
          return None
