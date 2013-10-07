#!/usr/bin/env python
#-*- conding: utf-8 -*-
import ConfigParser

class Config( object ):

    def __init__( self, configfile ):
        self.configfile = configfile
        self.config     = ConfigParser.ConfigParser()
        self.config.read( configfile )

    def get_servers( self ):
        server = list()

        for section in self.config.sections():
            server.append( { 'hostname': self.config.get( section, 'hostname' ),
                             'username': self.config.get( section, 'username' ),
                             'ip'      : self.config.get( section, 'ip' ),
                             'tunnel'  : self.config.get( section, 'tunnel'),
                             'port'    : self.config.get( section, 'port'),
                           }
                          )

        return server

