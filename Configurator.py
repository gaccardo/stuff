import ConfigParser


class Configurator( object ):

   def __init__(self, file, section):
      self.file    = file
      self.config  = ConfigParser.RawConfigParser()
      self.section = section
      self.config.read(file)

   def getValue(self, parameter):
      return self.config.get(self.section, parameter)
