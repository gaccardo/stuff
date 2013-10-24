#!/usr/bin/env python

import feedparser
from time import mktime
from datetime import datetime

aws_feed_url = 'http://status.aws.amazon.com/rss/ec2-us-east-1.rss'
feed = feedparser.parse( aws_feed_url )

print feed['items'][0].keys()

for post in feed['items']:
	time = post.published_parsed

	time = datetime.fromtimestamp(mktime(time))
	hoy = datetime.today()

	print time < hoy

	print "-------"
	print post.title
	print post.summary
	print "-------"


#datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')