import smtplib

class Mailer( object ):

   def __init__(self, email_sender, email_to, relay, logger=None):
      self.email_sender = email_sender
      self.email_to     = email_to
      self.relay        = relay
      self.logger       = logger

   def __logThis(self, msg):
      if self.logger is not None:
         self.logger.addInfoLine(mgs)

   def sendMail(self, subject, message):
      try:
         message = """From: %s
To: %s
Subject: %s \n\n\n%s""" % (self.email_sender, self.email_to, subject, message)

         smtpObj = smtplib.SMTP(self.relay)
         self.__logThis(smtpObj)
         smtpObj.sendmail(self.email_sender, self.email_to, message)
         return True
      except smtplib.SMTPException, e:
         self.__logThis(e)
         return "Exception sending email -> %s" % e
      except SMTPRecipientsRefused, e:
         self.__logThis(e)
         return "Rejected by destination -> %s" % e
