#!/usr/bin/env python
#-*- conding: utf-8 -*-


class Server( object ):

    def __init__( self, id, username, hostname, ip, tunnel=None ):
        self.id       = id
        self.username = username
        self.hostname = hostname
        self.ip       = ip
        self.tunnel   = tunnel

    def __str__( self ):
        if self.tunnel == 'None':
            return "%s %s@%s" % (self.id, self.username, self.hostname)
        else:
            return "%s %s@%s -L %s" % (self.id, self.username, self.hostname, self.tunnel)

    def getUsername( self ):
        return self.username

    def getHostname( self ):
        return self.hostname

    def getIp( self ):
        return self.ip

    def getId( self ):
        return self.id

    def getTunnel( self ):
        """
        (localport, remoteip, remoteport)
        """
        return self.tunnel

    def setTunnel( self, tunnel ):
        self.tunnel = tunnel

    
