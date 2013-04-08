#!/usr/bin/env python

class AllowedRecipients( object ):

   def __init__(self, aliases, recipients):
      self.aliases    = aliases
      self.recipients = recipients

   def run(self):
      f_pointer = open(self.aliases, 'r')
      f_buffer  = f_pointer.readlines()
      f_pointer.close()
      n_pointer = open(self.recipients, 'w')

      for line in f_buffer:
         if not line.startswith('#') and line != '\n':
            n_pointer.write( "%s:\t\t\tACCEPT\n" % line.split(':')[0] )

      n_pointer.close()

      
