#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sshToApsManager import sshToApsManager
from serviceDeskConnector import serviceDeskConnector

"""
"""

__version__   = ""
__author__    = ""
__program__   = ""
__date__      = ""
__license__   = ""
__copyright__ = ""

service      = serviceDeskConnector()
apsconnector = sshToApsManager()

service.deleteUsersNotInHD()
#service.addUsersToMacfilter()
service_log = service.getLog()

apsconnector.doSync()
