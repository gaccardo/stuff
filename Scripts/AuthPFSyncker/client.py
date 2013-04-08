#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

"""
Client for use with authpf server
"""

__version__   = "0.1"
__author__    = "Guido Accardo <gaccardo@gmail.com>"

if sys.argv[1] == "-U" or sys.argv[1] == "--userexists":
        print "OK"
    elif sys.argv[1] == "-A" or sys.argv[1] == "--adduser":
        print "OK"
