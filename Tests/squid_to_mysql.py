#!/usr/bin/env python
import MySQLdb


HOST="127.0.0.1"
USER="root"
PAWD="PedroipCop1987"
DBNA="squid"


class AccessEntry( object ):

   def __init__( self, unixtime, elapsed, remotehost, code, bytestransfer, 
                 method, url ):

      self.unixtime      = unixtime
      self.elapsed       = elapsed
      self.remotehost    = remotehost
      self.code          = code
      self.bytestransfer = bytestransfer
      self.method        = method
      self.url           = url

   def __str__( self ):
      return "Access Entry: %s [%s] ::> %s [%s]" % ( self.unixtime,
                                                     self.remotehost,
                                                     self.url,
                                                     self.code )

   def getUnixtime( self ):
      return self.unixtime

   def getElapsed( self ):
      return self.elapsed

   def getRemoteHost( self ):
      return self.remotehost

   def getCode( self ):
      return self.code

   def getBytesTransfer( self ):
      return self.bytestransfer

   def getMethod( self ):
      return self.method

   def getUrl( self ):
      return self.url


class ParseLogFile( object ):

   def __init__( self, logfile ):
      self.logfile = logfile

   def getRawAccess( self ):
      f_pointer = open( self.logfile, 'r' )
      f_buffer  = f_pointer.readlines()
      f_pointer.close()

      result = list()

      for line in f_buffer:
         line = line.split(' ')
         line = [i for i in line if i]

         access = AccessEntry( line[0],
                               line[1],
                               line[2],
                               line[3],
                               line[4],
                               line[5],
                               line[6],
                             )         

         result.append( access )

      return result


class SquidToMysql( object ):

   def __init__( self, logfile ):
      self.logfile = logfile 
      self.parser  = ParseLogFile( logfile )

   def __connectDB( self ):
      self.link   = MySQLdb.connect(host  = HOST,
                                   user   = USER,
                                   passwd = PAWD,
                                   db     = DBNA)
      self.cursor = self.link.cursor()

      return self.cursor

   def __processSQL( self, sql ):

      try:
         self.cursor.execute( sql )

         return self.cursor.fetchone()
      except:
         return False
      
   def __getLastAccessDate( self ):
      pass
      #sql    = """SELECT unixtime FROM squid_lastparse LIMIT 1"""
      #result = self.__processSQL( sql )

      #return result

   def __removeOlderEntries( self, current ):
      pass

   def __insertEntries( self, entries ):
      cursor = self.__connectDB()
      
      for entry in entries:
         sql = """INSERT INTO squid_access (unixtime, elapsed, remotehost, code, bytestransfer, method, url) VALUES (%s, %s, '%s', '%s', %s, '%s', '%s') """ % ( entry.getUnixtime(),
                                                                                                                                                                               entry.getElapsed(),
                                                                                                                                                                               entry.getRemoteHost(),
                                                                                                                                                                               entry.getCode(),
                                                                                                                                                                               entry.getBytesTransfer(),
                                                                                                                                                                               entry.getMethod(),
                                                                                                                                                                               entry.getUrl() )

         self.__processSQL( sql )

      self.link.commit()
      self.link.close()

   def __getAccesses( self ):
      access = self.parser.getRawAccess()
      last   = access[-1]

      return {'accesses': access, 'last': last}

   def run( self ):
      accesses = self.__getAccesses()
      self.__insertEntries( accesses['accesses'] )
      self.__removeOlderEntries( accesses['last'] )

      if self.__getLastAccessDate() is None:
         print "First access. This could be take a while to be processed"


if __name__ == '__main__':
   stm = SquidToMysql('/home/gaccardo/access.log')
   stm.run()
