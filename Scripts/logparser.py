#!/usr/bin/env python

import sys 

VERDE = '\033[92m'
WARNI = '\033[93m'
AZUL  = '\033[94m'
FAIL  = '\033[91m'
END   = '\033[0m'
BOLD  = '\033[1m'
BGRED = '\033[41m'


class LogParser( object ):

   def __init__(self, logfile):
      try:
         f_pointer     = open(logfile, 'r')
         self.f_buffer = f_pointer.readlines()
         f_pointer.close()
      except IOError:
         print "%sEl archivo ingresado no existe %s" % (FAIL, END)

   def __removeLineBreak(self, line):
      line = line.split('\n')[0]

      return line

   def __getPackageName(self, line):
      try:
         line_process = line.split('-> ')[1]
         line_process = line_process.split(' ')[0]
         line         = line.replace(line_process, '%s %s %s' % (VERDE, line_process, END))
      except:
         pass

      return line

   def __highLightDebug(self, line):
      line_process = None
      try:
         line_process = line.split('[')[3]
         line_process = line_process.split(' ')[1]

         if   line_process == 'INFO':
            line = line.replace(line_process, '%s %s %s' % (AZUL, line_process, END))
         elif line_process == 'WARNING':
            line = line.replace(line_process, '%s %s %s' % (WARNI, line_process, END))
         elif line_process == 'ERROR':
            line = line.replace(line_process, '%s %s %s %s' % (BGRED, WARNI, line_process, END))
      except:
         pass

      return (line, line_process)

   def __setBoldMSG(self, line, debug):
      try:
         line_process = line.split('::')[-1]
         if debug == 'ERROR':
            line = line.replace(line_process, '%s %s %s %s' % (BGRED, BOLD, line_process, END))
         else:
            line = line.replace(line_process, '%s %s %s' % (BOLD, line_process, END))
      except:
         pass

      return line

   def getLines(self):
      for line in self.f_buffer:
         line        = self.__removeLineBreak(line)
         line        = self.__getPackageName(line)
         line, debug = self.__highLightDebug(line)
         line        = self.__setBoldMSG(line, debug)
         print line


if __name__ == '__main__':
   try:
      l = LogParser(sys.argv[1])
      l.getLines()
   except IndexError:
      print "%sDebe ingregar el archivo log %s" % (FAIL, END)
