#!/usr/bin/env python
#-*- coding: utf-8-*-

import sys 
sys.path.append('/etc//lib/')

from sshconnector import SSHConnector
from Server       import Server
from Configurator import Configurator
from Mailer       import Mailer


class CertChecker( object ):

   def __init__( self ):
      self.ssh  = SSHConnector( )
      self.conf = Configurator( '/etc//cfg/cert-checker.cfg', 'cert-checker' )
      mailto    = self.conf.getValue('MAILTO').split(',')
      self.mail = Mailer( self.conf.getValue('MAILFROM'), mailto, self.conf.getValue('SMTPRELAY') )

   def __processDays( self ):
      files    = self.conf.getValue('REMOTE_FILES')
      files    = files.split(',')
      server   = self.conf.getValue('SERVER')
      server   = server.split(',')
      server   = Server( server[0], server[1], server[2], server[3], server[4] )
      tmp      = self.conf.getValue('TMP')
      contents = list()

      for file in files:
         self.ssh.getFile( server, file, "%s/" % tmp )
         cont_tmp = open("%s" % file, 'r' )
         expiring = list()

         for line in cont_tmp:
            line = line.strip()
            line = line.split( '|' )
            if int( line[1] ) < int( self.conf.getValue('DAYS') ):
               expiring.append( {'name':line[0], 'days':line[1]} )

         contents.append( { '%s' % (file): expiring } ) 

      return contents

   def startCheck( self ):
      expiring = self.__processDays()
      subject  = "Certificates expiration report"
      body     = "This is an automatic report of certificates that are about to expire\n\n"

      for exp in expiring:
         if len( exp[ exp.keys()[0] ] ) > 0:
            title = exp.keys()[0].split('-')[3].split('.')[0]
            body += "%s\n" % title
            for cert in exp[ exp.keys()[0] ]:
               if int( cert['days'] ) < 0:
                  body += " !! CERTIFICATE EXPIRED %s\n\n" % cert['name']
               else:
                  body += " W CERTIFICATE %s EXPIRES IN %s DAYS\n\n" % ( cert['name'], cert['days'] )

      body += "\n\n\n\nThis email will be sent every Monday at morning\n\n"
      body += "Recipients: %s\n" % self.conf.getValue('MAILTO')

      self.mail.sendMail( subject, body )


if __name__ == '__main__':
   CC = CertChecker()
   CC.startCheck()

