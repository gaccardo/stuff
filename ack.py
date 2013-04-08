#!/usr/bin/env python

import sys
import re
sys.path.append('/etc/core/lib/')

from Logger       import Logger
from Configurator import Configurator
from ZabbixDB     import ZabbixDB
from Mailer       import Mailer


FROM    = ""
SUBJECT = ""
PIN     = ""
KEY     = None


class ACK( object ):

   def __init__(self):
      self.c = Configurator('/etc/core/cfg/ack.conf', 'ack')
      self.l = Logger(self.c.getValue('FILE_LOG'), self.c.getValue('NAME'), self.c.getValue('DEBUG'))
      self.z = ZabbixDB(self.l, self.c.getValue('DB_HOST'), self.c.getValue('DB_USER'), self.c.getValue('DB_PASS'), self.c.getValue('DB_NAME'))

   def __checkUserPIN(self, pin, ffrom):
      users_raw = self.c.getValue('USERS')
      users_lines = users_raw.split(',')

      for user in users_lines:
         self.l.addInfoLine("%s :: %s" % ( user.split('|')[0], user.split('|')[1] ))
         if user.split('|')[0] == ffrom and user.split('|')[1] == pin:
             return True

      return False

   def __clearSubject(self, subject, pipes):
      if pipes:
          self.l.addInfoLine(subject)

          try:
             filtered = subject.split('|')
             self.l.addInfoLine(filtered[0])

             return filtered[1]
          except:
             self.l.addWarningLine('El subject esta mal formado')
         
          return "Mal formed subject"
      else:
          return subject

   def __sendEmail(self, user, subject, type):
      self.m = Mailer('zabbix@coresecurity.com', self.c.getValue('MAIL_TO'), self.c.getValue('RELAY'))
      self.m.sendMail("ACK: %s" % self.__clearSubject(subject, type), "ACK Message: %s" % self.__clearSubject(subject, type))
      self.l.addInfoLine('Email Sended to itnetworking')

      self.m = Mailer('zabbix@coresecurity.com', user, self.c.getValue('RELAY'))
      self.m.sendMail("ACK: %s" % self.__clearSubject(subject, type), "ACK Message: %s" % self.__clearSubject(subject, type))
      self.l.addInfoLine('Email Sended to %s' % user)

   def __isException(self, e_from):
      filtered = e_from.split('|')

      for email in filtered:
         if email == e_from:
            return True

      return False
      
   def main(self):
      stdin_raw   = sys.stdin.read()
      stdin_lines = stdin_raw.split('\n')
      KEY         = None
      PIN         = ""
      FROM        = ""
      ACK         = False

      self.l.addInfoLine('---------------------------------')
      for line in stdin_lines:

         if re.search('From ', line):
             FROM = line.split('From ')[1]
             FROM = FROM.split('  ')[0]
             self.l.addInfoLine("From: %s" % FROM)

         if re.search('Subject: ', line):
             SUBJECT = line.split('Subject: ')[1]
             self.l.addInfoLine("Subject: %s" % SUBJECT)
             ack_key = SUBJECT.split(' ')[0]

             if ack_key == 'ACK':
                PIN = SUBJECT.split(' ')[1]
                self.l.addInfoLine("ACK PIN: %s" % PIN)
                ACK = True

         if re.search('KEY: ', line):
             if KEY is None:
                 KEY = line.split('KEY: ')[1]
                 self.l.addInfoLine('KEY: %s' % KEY)

      if ACK:
         if not self.__checkUserPIN(PIN, FROM):
            self.l.addWarningLine('Invalid PIN/USER combination')
            self.l.addWarningLine('User %s has given an incorrect PIN %s' % (FROM, PIN))
            self.__sendEmail(FROM, "USER %s has given an incorrect PIN %s" % (FROM, PIN), False)
         else:
            self.l.addInfoLine('PIN/USER ACCEPTED')

            if self.z.ACK( KEY ):
               self.l.addInfoLine('ACK OK')
               self.__sendEmail(FROM, "ACK! %s" % SUBJECT, True)
            else:
               self.l.addErrorLine('ACK ERROR')

      else:
            if not self.__isException(FROM):
               self.__sendEmail(FROM, "WARNING USER %s MALFORMED EMAIL" % FROM, False)
         
      self.l.addInfoLine('---------------------------------')

if __name__ == '__main__':
   a = ACK()
   sys.exit( a.main() )
