#!/usr/bin/env python
#-*- coding: utf-8 -*-

from snmpdevice import SNMPDevice
from Mailer     import Mailer

class ACSwitcher( object ):

   def __init__( self, acs, last ):
      self.acs  = acs
      self.last = last
      #self.mail = Mailer( 'zabbix@coresecurity.com', 'itnetworking@coresecurity.com', '192.168.13.5' )
      self.mail = Mailer( 'zabbix@coresecurity.com', 'gaccardo@coresecurity.com', '192.168.13.5' )
      self.mall = Mailer( 'zabbix@coresecurity.com', 'mcampos@coresecurity.com', '192.168.13.5' )

   def __changeAC( self, new_ac ):
      f_pointer = open(self.last, 'w')
      f_pointer.write(new_ac)
      f_pointer.close()

   def __lastAC( self ):
      f_pointer = open(self.last, 'r')
      f_buffer  = f_pointer.read()
      f_pointer.close()

      last_ac = f_buffer.strip()

      for ac in self.acs:
         if ac.getHost() == last_ac:
            return last_ac

   def __newAC( self, last_ac ):
      for ac in self.acs:
         if ac.getHost() != last_ac:
            return ac.getHost()

   def __getName( self, host ):
      for ac in self.acs:
         if ac.getDeviceByHost( host ) is not None:
            return ac.getDeviceByHost( host )

   def __sendMail( self, result, last_ac, new_ac, errors ):
      subject = ""
      body    = ""

      if result == 0:
         subject = "AC Switch: Succesfull"
         body     = "###########################\n"
         body    += "#        AC Switch        #\n"
         body    += "###########################\n"
         body    += " * Result: Successfull\n"
         body    += " * Last AC: %s\n" % self.__getName(last_ac)
         body    += " * New AC: %s\n" % self.__getName(new_ac)
         body    += "###########################\n"
      else:
         subject = "AC Switch: Failed"
         body     = "###########################\n"
         body    += "#        AC Switch        #\n"
         body    += "###########################\n"
         body    += " * Result: Failed\n"
         body    += " * Last AC: %s\n" % self.__getName(last_ac)
         body    += " * New AC: %s\n" % self.__getName(new_ac)
         body    += "###########################\n"

         print 'ERRORS:' if len(errors) > 0 else ''
         for error in errors:
            body += " * %s\n" % error


      print subject
      print body

      self.mail.sendMail( subject, body )
      self.mall.sendMail( subject, body )

   def runCheck( self ):
      last_ac = self.__lastAC()
      new_ac  = self.__newAC( last_ac )
      bad     = 0
      errors  = list()

      for ac in self.acs:
         comp1 = True if ac.processOID(".1.3.6.1.4.1.9839.2.1.1.3.0")[0] == '1' else False
         comp2 = True if ac.processOID(".1.3.6.1.4.1.9839.2.1.1.2.0")[0] == '1' else False

         if ac.getHost() == last_ac:
            if comp1 == True or comp2 == True:
               bad += 1
               errors.append( "Prev AC shouldn't have any compressors working, but it have" )

         if ac.getHost() != last_ac:
            if not (comp1 == True or comp2 == True):
               errors.append( "New AC should have at least one of its compressors working, but it haven't" )
               bad += 1

      self.__sendMail( bad, last_ac, new_ac, errors )
      self.__changeAC( new_ac )


if __name__ == '__main__':
  ACS = ACSwitcher( [ SNMPDevice( '10.2.10.6', 1, 'noc-core-sec-new', 'AC01 Buenos Aires' ),
                      SNMPDevice( '10.2.10.22', 2, 'public', 'AC02 Buenos Aires' )
                    ], 'last'
                  )

  ACS.runCheck()
