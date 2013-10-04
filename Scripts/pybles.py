#!/usr/bin/env python
from blessings import Terminal

class IncorrectNumberOfCells(Exception):

  def __str__(self):
    return "La cantidad de celdas es incorrecta"


class HeaderAlreadySet(Exception):

  def __str__(self):
    return "El numero de columnas no puede ser modificado una vez seteadas filas"


class Pybles(object):

  def __init__(self):
    self.table   = list()
    self.header  = list()
    self.lines   = list()
    self.longest = 0

  def add_column(self, title):
    if len(self.lines) == 0:
      self.header.append(title) 
    else:
      raise HeaderAlreadySet

  def add_line(self, line):
    if len(line) == self.get_columns_count():
      self.lines.append(line)
    else:
      raise IncorrectNumberOfCells

  def get_columns_count(self):
    return len(self.header)

  def configure_length(self, old_header, old_lines):
    header = list()
    lines  = list()

    for cell in old_header:
      header.append( {'name': cell, 'len': len(cell)} )

    for line in old_lines:
      tmp_line = list()
      for cell in line:
        try:
          tmp_line.append( {'name': cell, 'len': len(cell)} )
        except TypeError:
          tmp_line.append( {'name': cell, 'len': len(str(cell))} )

      lines.append(tmp_line)

    return header, lines

  def set_column_length(self, header, lines):
    for cellnumber in range(len(header)):
      for line in lines:
        if header[cellnumber]['len'] < line[cellnumber]['len']:
          header[cellnumber]['len'] = line[cellnumber]['len']

    for cellnumber in range(len(header)):
      for line in lines:
        line[cellnumber]['len'] = header[cellnumber]['len']        

    return header, lines

  def show_dots(self, header):
    dots = 0
    for cell in header:
      dots += cell['len']

    dots = '-' * (dots + (3 * len(header)) + 1)

    print dots

  def show_header(self, header):
    header_as_string = "|"

    self.show_dots(header)

    for cell in header:
      header_as_string += " %s%s |" % (cell['name'], " " * (cell['len'] - len(cell['name'])))

    print header_as_string

    self.show_dots(header)

  def show_lines(self, lines, header, highlight=None):
    lines_as_string = ""
    t = Terminal()

    for line in lines:
      lines_as_string += "|"
      for cell in line:
        try:
          name = cell['name']
          if highlight in name:
            name = "%s%s%s" % (t.bold, name, t.normal)

          lines_as_string += " %s%s |" % (name, " " * (cell['len'] - len(cell['name'])))
        except TypeError:
          lines_as_string += " %s%s |" % (name, " " * (cell['len'] - len(str(cell['name']))))

      lines_as_string += "\n"

    print lines_as_string.strip("\n") 
    self.show_dots(header)

  def show_table(self, highlight=None):
    header, lines = self.configure_length(self.header, self.lines)
    header, lines = self.set_column_length(header, lines)

    if len(header) != 0:
      self.show_header(header)

    if len(lines) != 0:
      self.show_lines(lines, header, highlight)


if __name__ == '__main__':
  PB = Pybles()
  PB.add_column('Nombre')
  PB.add_column('Apellido')
  PB.add_column('Edad')
  PB.add_line(['Guido', 'Accardo', 26])
  PB.show_table(highlight='Guido')