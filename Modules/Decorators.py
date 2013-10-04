#!/usr/bin/env python

import traceback
import sys 

from MainException import *

AUTHENTICATED = True

def auth(f):
   def inner(*args, **kwargs):
      if AUTHENTICATED:
         f(*args, **kwargs)
      else:
         tb = traceback.format_stack()
         raise UserNotAuthenticated('[PERMISSION DENIED]: User is not authenticated',
                                    f.__name__, tb) 

   return inner
