#!/usr/bin/env python

import shutil
import sys
import subprocess

print "Copying binaries"
try:
  shutil.copyfile("%s/ssher.py" % sys.argv[1], '/usr/bin/ssher')
  subprocess.call(['chmod', 'a+x', "/usr/bin/ssher"])
except IOError:
  print "You don' have permissions to perform this installation. Please, run this installation as root"