#!/usr/bin/env python

import sqlite3
import sys

from optparse import OptionParser


class DBConverter( object ):

   def __init__(self, args):
      self.ifile     = args.ifile
      self.ofile     = args.ofile
      self.dbname    = args.dbname
      self.tablename = args.tablename
      self.verbose   = args.verbose

      if self.ifile     == None or \
         self.ofile     == None or \
         self.dbname    == None or \
         self.tablename == None:
         print "Numero de argumentos incorrecto"
         sys.exit(-1)

      print "Datos:"
      print " * Base de datos: %s"            % self.dbname
      print " * Tabla: %s"                    % self.tablename
      print " * Archivo de base de datos: %s" % self.ifile
      print " * Archivo CVS resultante: %s"   % self.ofile

      self.run()

   def __executeQuery(self, sql, debug=None):
      if debug is True:
         import pdb;pdb.set_trace()

      self.link = sqlite3.connect( self.ifile )
      cursor    = self.link.cursor()
      result    = cursor.execute( sql )

      return result

   def __generateOutput(self, header, lines):
      output_pointer = open(self.ofile, 'w')
      output_pointer.write('%s\n' % header)

      for line in lines:
         if self.verbose is not None:
            print line

         output_pointer.write(line)

      output_pointer.close()
      
 
   def run(self):
      sql    = """SELECT * FROM %s""" % self.tablename
      result = self.__executeQuery(sql)
      header = ""

      for item in result.description:
         header = header + "%s," % item[0]

      header = header[:-1]
      rows   = result.fetchall()
      lines  = ""

      for row in rows:
         lines = lines + "%s,%s,%s,%s,%s,%s,%s,%s\n" % (row[0],
                                                        row[1],
                                                        row[2],
                                                        row[3],
                                                        row[4],
                                                        row[5],
                                                        row[6],
                                                        row[7])

      self.__generateOutput(header, lines)


if __name__ == '__main__':
   parser = OptionParser()
   parser.add_option("-i", "--input", dest="ifile",
                     help="path of the input dbfile", metavar="<SQLITE DB>")
   parser.add_option("-o", "--output", dest="ofile",
                     help="path of the output csvfile", metavar="<CSV FILE>")
   parser.add_option("-d", "--dbname", dest="dbname",
                     help="name of the dabatase", metavar="<DB NAME>")
   parser.add_option("-t", "--tablename", dest="tablename",
                     help="name of the table", metavar="<TABLE NAME>")
   parser.add_option("-v", dest="verbose", action="store_false",
                     help="show step by step")
   
   (option, args) = parser.parse_args()
   dbconverter    = DBConverter(option)
