#!/usr/bin/env python

class Pybles(object):

  def __init__(self):
    self.table   = list()
    self.header  = list()
    self.lines   = list()
    self.longest = 0

  def add_column(self, title):
    self.header.append(title) 

  def add_line(self, line):
    if len(line) == self.get_columns_count():
      self.lines.append(line)
    else:
      print "Lines len"

  def get_columns_count(self):
    return len(self.header)

  def get_header(self):
    return self.header

  def get_lines(self):
    return self.lines

  def get_longest_cell(self):
    for cell in self.header:
      if len(cell) > self.longest:
        self.longest = len(cell)

    for line in self.lines:
      for cell in line:
        if len(cell) > self.longest:
          self.longest = len(cell)

  def configure_length(self, header, lines):
    new_header = list()
    new_lines  = list()

    for cell in header:
      if len(cell) < self.longest:
        add = self.longest - len(cell)
        blank = ' ' * add
        cell = '%s%s' % (cell, blank)

        new_header.append(cell)
      else:
        new_header.append(cell)

    for line in lines:
      new_line = list()
      for cell in line:
        if len(cell) < self.longest:
          add = self.longest - len(cell)
          blank = ' ' * add
          cell = '%s%s' % (cell, blank)

          new_line.append(cell)
        else:
          new_line.append(cell)

      new_lines.append(new_line)


    return new_header, new_lines

  def show_table(self):
    self.get_longest_cell()
    header, lines = self.configure_length(self.header, self.lines)

    print header 
    for line in lines:
      print line


PB = Pybles()
PB.add_column('Name')
PB.add_column('LastN')
PB.add_line(['Guido', 'Accardo'])
PB.add_line(['Delfi', 'Baravalle'])
PB.show_table()
