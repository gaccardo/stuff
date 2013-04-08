import pexpect

child = pexpect.spawn("ssh adminrancid@172.18.4.51")
child.setecho(1)
child.expect('Password:')
child.sendline('#$kasdkf$DSAGSDAG454=')
child.expect('BUE1WF601>')
child.sendline('en')
child.expect('Password:')
child.sendline('MamuchaComoFunc43to')
child.expect('BUE1WF601#')
child.sendline('conf t')
child.sendline('no access-list 700')
child.sendline('no access-list 701')
child.sendline('no access-list 702')
child.sendline('\n')

child.sendline('access-list 700 permit 5894.6bd4.3780   0000.0000.0000')
child.sendline('access-list 700 deny   0000.0000.0000   ffff.ffff.ffff')
child.sendline('\n')

child.sendline('access-list 701 permit 001b.fe01.b3f8   0000.0000.0000')
child.sendline('access-list 701 deny   0000.0000.0000   ffff.ffff.ffff')
child.sendline('\n')

child.sendline('access-list 702 permit 5894.6bd4.3780   0000.0000.0000')
child.sendline('access-list 702 deny   0000.0000.0000   ffff.ffff.ffff')
child.sendline('\n')

print "Reglas actualizadas"
