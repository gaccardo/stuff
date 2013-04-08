#!/usr/bin/env python

import smtplib

from time import sleep

class Spammer( object ):

   def __init__(self, relay, sender, destination, frequency, amount):
      self.relay       = relay
      self.sender      = sender
      self.destination = destination
      self.frequency   = frequency
      self.amount      = amount

   def __sendEmails(self):

      counter = 0

      while counter < self.amount:

         message = """From: %s
                      To: %s
                      Subject: %s \n\n\n""" % (self.sender, self.destination,
                                               'Informe de Ventas')

         smtpObj = smtplib.SMTP(self.relay)
         smtpObj.sendmail(self.sender, self.destination, message)

         counter += 1

         sleep(self.frequency)

   def playball(self):
      self.__sendEmails()


spr = Spammer("172.18.8.7", "test@coresecurity.com", \
              "jariznabarreta@test.coresecurity.com", 0.3, 10)
spr.playball()

# 172.18.8.7 SOLO
# 172.20.8.7 CARP
# 172.20.8.5
# 172.20.8.6
# 
#
# jariznabarreta@test.coresecurity.com
