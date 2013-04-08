#!/usr/bin/env python 

import sys
sys.path.append('/etc/core/lib/')
import re

from Logger       import Logger
from Configurator import Configurator


class LoroReceiver( object ):

   def __init__(self):
      self.c = Configurator('/etc/core/cfg/lororeceiver.cfg', 'lororeceiver')
      self.l = Logger(self.c.getValue('FILELOG'), self.c.getValue('SYSTEM'), self.c.getValue('DEBUG'))

   def __searchKeyword(self, standardinput):
      self.l.addInfoLine("El cuerpo del email es el correcto?")
      process = standardinput.split(' ')

      for line in process:
         if re.search('Good_Auto_Response', line):
            return True

      return False

   def __isFromGranted(self, standardinput):
      self.l.addInfoLine('Es de un sender permitido?')
      process = standardinput.split('|')
      FROM    = None

      for line in process:
         if re.search('From ', line):
            FROM = line.split('From ')[1]
            FROM = FROM.split('  ')[0]
            break

      accepted_from = self.c.getValue('ACCEPTEDFROM').split('|')

      for user_from in accepted_from:
         if FROM == user_from:
            self.l.addInfoLine('Si lo es')
            return True

      self.l.addInfoLine('No lo es')
      return False

   def __storeValue(self, value):
      file_pointer = open(self.c.getValue('STATEFILE'),'w')
      self.l.addInfoLine('Valor storeado: %s' % value)
      file_pointer.write(value)
      file_pointer.close()

   def main(self):
      self.l.addInfoLine('--------------')
      self.__storeValue("0")
      EMAIL_buffer = sys.stdin.read()
      self.l.addInfoLine('Email Received')

      self.addInfoLine(EMAIL_buffer)

      if self.__isFromGranted(EMAIL_buffer):
         self.l.addInfoLine("Sender accepted")
         if self.__searchKeyword(EMAIL_buffer):
            self.l.addInfoLine("El cuerpo es correcto")
            self.__storeValue("1")
         else:
            self.l.addWarningLine("El cuerpo incorrecto")
            self.__storeValue("0")

      self.l.addInfoLine('--------------')


if __name__ == '__main__':
   lr = LoroReceiver()
   sys.exit( lr.main() )
