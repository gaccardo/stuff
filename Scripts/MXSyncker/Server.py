#!/usr/bin/env python


class Server( object ):

   def __init__( self, name, ip, username, os, network ):
      self.name     = name
      self.ip       = ip
      self.username = username
      self.os       = os
      self.network  = network

   def getName( self ):
      return self.name

   def getIP( self ):
      return self.ip

   def getUsername( self ):
      return self.username

   def getOs( self ):
      return self.os

   def getNetwork( self ):
      return self.network

   def setName( self, name ):
      self.name = name

   def setIP( self, ip ):
      self.ip = ip

   def setUsername( self, username ):
      self.username = username

   def setOs( self, os ):
      self.os = os

   def setNetwork( self, network ):
      self.network = network
