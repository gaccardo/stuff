#!/usr/bin/env python

from Logger       import Logger
from Configurator import Configurator

import sys

################################################
#                  CONF                        #
################################################
FILE_LOG       = '/tmp/cotorra.log'            #
ALLOWED_SENDER = 'core.mail.checker@gmail.com' #
################################################


class Cotorra( object ):

   def __init__(self):
      self.config = Configurator('/etc/core/etc/cotorra.cfg')
      self.logger = Logger(FILE_LOG)

   def main(self):
      stdin = sys.stdin.readlines()
      self.logger.addLine('Veo el correo')


if __name__ == '__main__':
   cc = Cotorra()
   sys.exit( cc.main() )
