#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pexpect
import re


class sshToASA(object):

    def __init__(self, ip, hostname, username, password, status):
        self.ip = ip
        self.hostname = hostname
        self.username = username
        self.password = password
        self.status = status

    def getUsersInVpn(self, tipo):
        users = list()
        data = None
        sw = pexpect.spawn('ssh %s@%s' % (self.username, self.ip))
        sw.expect("%s@%s's password:" % (self.username, self.ip), timeout=60)
        sw.sendline('%s' % self.password)
        sw.sendline('en')
        sw.expect('Password:')
        sw.sendline('%s' % self.password)
        sw.sendline('conf t')
        sw.sendline('pager 0')
        sw.sendline('exit')
        sw.expect('%s/act/%s#' % (self.status, self.hostname))
        sw.sendline('show vpn-sessiondb %s' % tipo)
        sw.sendline('conf t')
        sw.sendline('pager 80')
        sw.sendline('exit')
        sw.sendline('exit')
        data = sw.readlines()
        sw.close()

        for line in data:
           parts = line.split()

           if len(parts) > 0:
              if parts[0] == 'Username':
                 users.append( parts[2] )

        return users


if __name__ == '__main__':
    sshtoasa = sshToASA('', '', '', '', '')
    users = list()
    users += sshtoasa.getUsersInVpn('anyconnect')
    users += sshtoasa.getUsersInVpn('ra-ikev1-ipsec')

    print users
