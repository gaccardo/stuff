#!/usr/bin/evn python

import sys 

from Mailer import Mailer


class MainException( Exception ):

   def __init__( self, msg, args, trace ):
      self.MAILFROM = ''
      self.MAILTO   = ''
      self.RELAY    = ''
      self.CODES    = [ 
                       {'name': 'OutOfRange',            'code': 100},
                       {'name': 'ZeroDivision',          'code': 200},
                       {'name': 'UserNotAuthenticated',  'code': 300},
                       {'name': 'SMTPRecipientsRefused', 'code': 400},
                     ]   

      self.__sendEmailException( msg, args, trace )

   def __sendEmailException( self, msg, args, trace ):
      code    = self.__getCodeByException()
      mailer  = Mailer( self.MAILFROM, self.MAILTO, self.RELAY )
      text    = "An exception has occured in %s\n\n" % sys.argv[0]
      text   += "MESSAGE: %s\n" % msg 
      text   += "WHERE: %s [ %s ]\n" % ( sys.argv[0], args )
      text   += "CODE: %s\n\n" % code
      text   += "** STACK TRACE **\n"

      for line in trace:
         text += "%s" % line

      subject = "Exception [ %s ]" % code

      mailer.sendMail( subject, text )

   def __getCodeByException( self ):
      classname = self.__repr__().split('()')[0]

      for code in self.CODES:
         if classname == code['name']:
            return code['code']

      return "Unknown Exception"


## This are exception examples, should be replaced by users Custom Exception ##
class OutOfRange( MainException ):            pass
class ZeroDivision( MainException ):          pass
class UserNotAuthenticated( MainException ):  pass
class SMTPRecipientsRefused( MainException ): pass
