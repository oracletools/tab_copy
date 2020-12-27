import os

ssh_pipe = os.popen("ssh bk94994@swmapetldev01.nam.nsroot.net")
ssh_pipe.write('prince987!')
ssh_pipe.write("\n")
ssh_pipe.flush()
ssh_pipe.close()

import pexpect

PASS='prince987!'
COMMAND="ssh bk94994@swmapetldev01.nam.nsroot.net"

child = pexpect.spawn(COMMAND)
child.expect('password:')
child.sendline(PASS)
child.expect(pexpect.EOF)
print child.before


import os
import getpass
import pexpect
import glob
import logging
import shutil
import time

class UpdateError(Exception): pass

g_password = 'prince987!'

def runSshCommand(cmd):
    global g_password

    ssh_newkey = 'Are you sure you want to continue connecting'
    # my ssh command line
    p=pexpect.spawn(cmd)

    i=p.expect([ssh_newkey,'password:',pexpect.EOF])
    if i==0:
        print "Saying yes to connection.."
        p.sendline('yes')
        i=p.expect([ssh_newkey,'password:',pexpect.EOF])

    if i==1:
        while True:
            if g_password is None:
                g_password = getpass.getpass("password:")
            p.sendline(g_password)
            i = p.expect(['password:',pexpect.EOF])
            if i==0:
                g_password = None
                print "Wrong password"
            else:
                break
    elif i==2:
        raise UpdateError("Got key or connection timeout")

    return p.before
	
	