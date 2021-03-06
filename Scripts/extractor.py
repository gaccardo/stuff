#!/usr/bin/env python
import rarfile
import sys
import pybles

from os import listdir, mkdir, getcwd
from os.path import isfile, join

class Extractor(object):

  def __init__(self, rars_path, contact, format):
    self.rars_path = rars_path
    self.contact   = contact
    self.format    = format

  def __get_rars_list(self):
    result = [ f for f in listdir(self.rars_path) if isfile(join(self.rars_path, f)) ]
    try:
      only_rar = [ join(self.rars_path, f) for f in result if f.split('.')[1] == 'rar' ]
    except IndexError:
      print "No se encontraron archivos .rar en esta carpeta"
      sys.exit(-1)

    return only_rar

  def __get_rars_mp3(self):
    result    = list()
    rars_list = self.__get_rars_list()

    for rar_file in rars_list:
      rf = rarfile.RarFile(rar_file)
      for mp3_file in rf.infolist():
        if mp3_file.filename.split('.')[-1] == self.format:
          name = mp3_file.filename.split('\\')[-1]
          result.append({'rar_file': rar_file, 'mp3_file': name, 'size': mp3_file.file_size})

    return result

  def __get_mp3_of_contact(self):
    result   = list()
    rars_mp3 = self.__get_rars_mp3()

    for mp3 in rars_mp3:
      contact = mp3['mp3_file'].split('-')[0]

      if contact == self.contact:
        result.append( mp3 )

    return result

  def __get_what_rar_uncompress(self):
    mp3_in_rars = self.__get_mp3_of_contact()
    uncompress = list()

    for mp3 in mp3_in_rars:
      if mp3['rar_file'] not in uncompress:
        uncompress.append(mp3['rar_file'])

    return mp3_in_rars, uncompress

  def extract_mp3(self, mp3, rars):
    try:
      mkdir('/tmp/%s' % self.contact)
    except OSError:
      pass

    for m in mp3:
      print 'extraido %s de %s en /tmp/%s' % (m['mp3_file'], m['rar_file'], self.contact)
      
      rf = rarfile.RarFile(m['rar_file'])
      for f in rf.infolist():
        if f.filename.split('\\')[-1] == m['mp3_file']:
          buff = rf.read(f)
          new_file = open('/tmp/%s/%s' % (self.contact, m['mp3_file']), 'w')
          new_file.write(buff)
          new_file.close()

  def present_info_files(self, mp3, highligth):
    tabla = pybles.Pybles()

    tabla.add_column('RAR File')
    tabla.add_column('File Found')
    tabla.add_column('Size')

    for ff in mp3:
      tabla.add_line([ff['rar_file'], ff['mp3_file'], "%s K" % ff['size']])

    tabla.show_table(highligth)

  def present_info_uncompress(self, uncompress):
    for rar_file in uncompress:
      print " * %s" % rar_file

  def present_all_mp3(self, mp3):
    tabla = pybles.Pybles()

    tabla.add_column('RAR File')
    tabla.add_column('File')
    tabla.add_column('Size')

    for ff in mp3:
      tabla.add_line([ff['rar_file'], ff['mp3_file'], "%s K" % ff['size']])

    tabla.show_table()

  def run(self):
    mp3, uncompress = self.__get_what_rar_uncompress()
    
    print "\nLos siguientes archivos con formato %s fueron encontrados:" % sys.argv[2]
    self.present_info_files(mp3, sys.argv[1])

    print "Es necesario descomprimir los siguientes archivos:\n"
    self.present_info_uncompress(uncompress)

    print "\nLos archivos resultantes quedaran en /tmp/%s/" % sys.argv[1]

    opt = str(raw_input('Continuar? <y/N>: '))
    if opt == 'y' or opt == 'Y':
      self.extract_mp3(mp3, uncompress)

    opt = str(raw_input('Listar todos los mp3? <y/N>: '))    
    if opt == 'y' or opt == 'Y':
      self.present_all_mp3(self.__get_rars_mp3())


if __name__ == '__main__':
  try:
    ext = Extractor(getcwd(), sys.argv[1], sys.argv[2])
    ext.run()
  except IndexError:
    print "ERROR: Cantidad de argumentos incorrectos"
