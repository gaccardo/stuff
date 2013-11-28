#!/usr/bin/env python
 
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
    self.logfile = 'access_generated.log'

    
  def get_last_key(self):
    try:
      return self.cb.get('last_key').value
    except:
      return 0

  def save_logs(self):
    file_pointer = open(self.logfile, 'r')
    file_buffer = file_pointer.readlines()
    file_pointer.close()

    last_key = 0

    for rawline in file_buffer:
      r = [line for line in rawline.split(' ') if line]
      if r[0] > self.get_last_key():
        access = Access(r[0], r[1], r[2], r[3], r[4], r[5], r[6])
        access.save(self.cb)
        last_key = access.get_time()

    if last_key != 0:
      self.cb.set('last_key', float(last_key))



if __name__ == '__main__':
  slp = SquidLogParser()
  slp.save_logs()