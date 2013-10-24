import time

ERROR   = ('ERROR',  1)
WARNING = ('WARNING',2)
INFO    = ('INFO',   3)
LEVELS  = [ERROR, WARNING, INFO]


class DebugLevelIncorrect( Exception ):

   def __str__(self):
      print " :: The given debug level doesn't exists"


class Logger( object ):

   def __init__(self, file, system, level):
      self.file     = file
      self.__system = system
      self.__level  = self.__translateLevel(level)

   def __translateLevel(self, level):
      for lev in LEVELS:
         if level == lev[0]:
            return lev[1]

      return False

   def __translateCode(self, level):
      for lev in LEVELS:
         if level == lev[1]:
            return lev[0]

      return False

   def __addLine(self, msg, level):
      if self.__translateLevel(level) <= self.__level:
         file_pointer = open(self.file, 'a')
         file_pointer.write('%s -> %s [ %s ]:: %s\n' % (time.asctime(), 
                                                        self.__system, 
                                                        level, msg))
         file_pointer.close()

   def addErrorLine(self, msg):
      self.__addLine(msg, 'ERROR')

   def addInfoLine(self, msg):
      self.__addLine(msg, 'INFO')

   def addWarningLine(self, msg):
      self.__addLine(msg, 'WARNING')

   def getDebugLevel(self):
      return self.__translateCode(self.__level)

   def changeDebugLevel(self, level):
      if self.__translateLevel(level) is not False:
         self.__level = self.__translateLevel(level)
      else:
         raise DebugLevelIncorrect