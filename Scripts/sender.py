#!/usr/bin/env python

from Logger import Logger
from Mailer import Mailer

import sys
import time
import base64

###########################################
#                  CONF                   #
###########################################
FILE_LOG  = '/tmp/sender.log'             #
MAIL_TO   = 'core.mail.checker@gmail.com' #
MAIL_FROM = 'zabbix@coresecurity.com'     #
RELAY     = 'armail.core.sec'             #
HASH_FILE = '/tmp/hash.it'                #
###########################################


class Sender( object ):

   def __init__(self):
      self.logger = Logger(FILE_LOG)
      self.mailer = Mailer(MAIL_FROM, MAIL_TO, RELAY)

   def __hashDate(self):
      return base64.b64encode( time.asctime() )

   def __storeHashedDate(self, hash):
      file_pointer = open(HASH_FILE,'w')
      file_pointer.write(hash)
      file_pointer.close()

      self.logger.addLine('HASH: %s' % hash)

   def __sendEmail(self, hash):
      body = 'HASH: %s\n' % hash

      if self.mailer.sendMail('[CHECKER]', body):
         self.logger.addLine('Email sent')
      else:
         self.logger.addLine('Unable to sent email')

   def main(self):
      hash = self.__hashDate()
      self.__storeHashedDate(hash)
      self.__sendEmail(hash)


if __name__ == '__main__':
   ss = Sender()
   sys.exit( ss.main() )
