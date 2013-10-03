#!/usr/bin/env python
#-*- conding: utf-8 -*-


class Server( object ):

    def __init__( self, id, username, hostname, ip, tunnel=None, port=None ):
        self.id       = id
        self.username = username
        self.hostname = hostname
        self.ip       = ip
        self.tunnel   = tunnel
        self.port     = port

    def __str__( self ):
        if self.tunnel == 'None':
            return "%s %s@%s" % (self.id, self.username, self.hostname)
        else:
            return "%s %s@%s -L %s" % (self.id, self.username, self.hostname, self.tunnel)

    def get_username( self ):
        return self.username

    def get_hostname( self ):
        return self.hostname

    def get_ip( self ):
        return self.ip

    def get_id( self ):
        return self.id

    def get_tunnel( self ):
        """
        (localport, remoteip, remoteport)
        """
        return self.tunnel

    def get_port( self ):
        return self.port

    def set_tunnel( self, tunnel ):
        self.tunnel = tunnel

    
