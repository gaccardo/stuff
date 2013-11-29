#!/usr/bin/env python

import os
import sys

from couchbase import Couchbase, FMT_PICKLE
from couchbase.views import iterator
from couchbase.exceptions import KeyExistsError

class Access( object ):

  def __init__(self, time, elapsed, ip, code, data, method, url):
    self.time = time
    self.elapsed = elapsed
    self.ip = ip
    self.code = code
    self.data = data
    self.method = method
    self.url = url

  def get_time(self):
    return self.time

  def get_elapsed(self):
    return self.elapsed

  def get_ip(self):
    return self.ip

  def get_code(self):
    return self.code

  def get_data(self):
    return self.data

  def get_method(self):
    return self.method

  def get_url(self):
    return self.url

  def get_document(self):
    return {'time': self.time, 'elapsed': int(self.elapsed), 'ip': self.ip,
            'url': self.url, 'code': self.code, 'data': int(self.data), 
            'method': self.method}

  def save(self, database):
    #database.add(self.time, self, format=FMT_PICKLE)
    try:
      database.add(self.time.replace('.', '_').strip('\t'), self.get_document())
    except KeyExistsError:
      pass


class SquidLogParser( object ):

  def __init__(self):
    self.cb = Couchbase.connect(bucket='default')
    self.logfile = 'access.log'

    
  def get_last_key(self):
    try:
      return self.cb.get('last_key').value
    except:
      return 0

  def save_logs(self):
    counter = -1
    f = open(self.logfile)
    rawline = ""
    os.lseek(f.fileno(), counter, 2)
    last_key = 0

    for i in range(1000000):
      char = os.read(f.fileno(), 1)
      counter -= 1
      rawline = "%s%s" % (char, rawline)

      if char == "\n":
        rrr = [line for line in rawline.split(' ') if line]
        rawline = ""

        if rrr[0].split('\n')[1] >= self.get_last_key():
          access = Access(rrr[0].split('\n')[1], 
                          rrr[1], rrr[2], rrr[3], 
                          rrr[4], rrr[5], rrr[6])
          access.save(self.cb)

          if access.get_time() > last_key:
            last_key = access.get_time()

        else:
          break

      try:
        os.lseek(f.fileno(), counter, 2)
      except OSError:
        break


    self.cb.set('last_key', last_key)

    

if __name__ == '__main__':
  slp = SquidLogParser()
  slp.save_logs()