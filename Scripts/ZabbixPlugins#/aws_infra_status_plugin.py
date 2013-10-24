#!/usr/bin/env python

import feedparser
import sys
from time import mktime
from datetime import datetime
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


class AWSStatus( object ):

	def __init__(self, url):
		self.feed = feedparser.parse( url )
		self.feed = self.feed['items']

		self.stored_id_file = "/tmp/last_aws_post.id"
		self.stored_feed = "/tmp/aws_log.txt"

	def __get_last_post(self):
		return self.feed[0]

	def __store_last_post_id(self, id):
		try:
			file_stored_id_pointer = open(self.stored_id_file, 'w')
			file_stored_id_pointer.write(id)
			file_stored_id_pointer.close()
			return True
		except IOError:
			return False

	def __get_last_stored_post_id(self):
		try:
			file_stored_id_pointer = open(self.stored_id_file, 'r')
			file_stored_id_buffer = file_stored_id_pointer.readlines()
			file_stored_id_pointer.close()
			return file_stored_id_buffer[0].strip()
		except IOError:
			print "No existe"
			return None
		except IndexError:
			return False

	def run(self):
		last_id = self.__get_last_stored_post_id()
		last_post = self.__get_last_post()

		print "Subject: %s" % last_post.title
		print "Body"
		print last_post.summary

		if last_id is False:
			self.__store_last_post_id(last_post.id)
			print last_post.id

		elif last_id is None:
			print "No existe el archivo"

		else:
			if last_post.id != last_id:
				self.__store_last_post_id(last_post.id)


if __name__ == '__main__':
	AWS = AWSStatus(url='http://status.aws.amazon.com/rss/ec2-us-east-1.rss')
	AWS.run()