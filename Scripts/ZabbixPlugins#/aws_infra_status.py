#!/usr/bin/env python

import feedparser
import sys

from time import mktime
from datetime import datetime


class AWSStatus( object ):

	def __init__(self, url):
		self.feed = feedparser.parse( url )
		self.feed = self.feed['items']
		self.stored_file = "/tmp/last_aws_post.date"
		self.stored_feed = "/tmp/aws_log.txt"

	def __get_last_date_posted(self):
		return self.feed[0].published_parsed

	def __get_stored_last_date(self):
		try:
			stored_fd = open(self.stored_file)
		except IOError:
			return None

		stored_buff = stored_fd.readlines()
		stored_fd.close()

		return stored_buff[0]

	def __store_new_date(self, date):
		stored_fd = open(self.stored_file, 'w')
		stored_fd.write(date.__str__())
		stored_fd.close()

	def __write_posts(self, feed):
		fd_pointer = open(self.stored_feed, 'w')

		for post in feed:
			line = "## %s ##\n" % post.title
			line += "%s\n" % post.summary
			line += "---------------------\n"
			fd_pointer.write(line)			

	def update(self):
		hoy = datetime.today()
		last_post_now = datetime.fromtimestamp(mktime(self.__get_last_date_posted()))
		last_post_stored = datetime.strptime(self.__get_stored_last_date(), '%Y-%m-%d %H:%M:%S')

		if last_post_stored is None:
			self.__store_new_date(time)
		else:
			if last_post_now < last_post_stored:
				self.__store_new_date(last_post_now)
			else:
				pass
				#sys.exit(0)

		self.__write_posts(self.feed)
		


if __name__ == '__main__':
	AWS = AWSStatus(url='http://status.aws.amazon.com/rss/ec2-us-east-1.rss')
	AWS.update()