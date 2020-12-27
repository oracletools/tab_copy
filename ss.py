import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('swmapetldev01.nam.nsroot.net', username='bk94994', password = 'prince987!' )
#ssh.exec_command( 'ls -al' )
#stdin,stdout,stderr = ssh.exec_command("bash;cd /opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy;. ./.ora_profile;./run.sh t tab_copy;")
#stdin,stdout,stderr = ssh.exec_command("cd /opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy;. ./.ora_profile;./run.sh t tab_copy;")
#stdin,stdout,stderr = ssh.exec_command("pbrun voletlusr")
stdin,stdout,stderr = ssh.exec_command("cd /opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy")
print stdout.read()
stdin,stdout,stderr = ssh.exec_command(". ./.ora_profile")
print stdout.read()
stdin,stdout,stderr = ssh.exec_command("pwd")
print stdout.read()

print '#'*40
print '#'*40
print stderr.read()
sys.exit(1)

stdin.write('prince987!\n')
stdin.flush()
stdin.write('test\n')
stdin.flush()
stdin.write('ls -al\n')
stdin.flush()
data = stdout.read()
print data
sys.exit(1)
stdin.write('lol\n')
stdin.flush()
data = stdout.read()
print data
sys.exit(1)
import subprocess, sys
from getpass import getpass

import ssh
server = ssh.Connection(host='swmapetldev01.nam.nsroot.net', username='bk94994', password = 'prince987!')
result = server.execute('ls -al')
sys.exit(1)


subprocess.call(['C:\Program Files\PuTTY\putty', '-ssh', 'bk94994@swmapetldev01.nam.nsroot.net', '-pw', 'prince987!', 'ls -al'], shell=True)
sys.exit(1)
#child = subprocess.Popen(['plink', '-ssh', 'bk94994@swmapetldev01.nam.nsroot.net', 'ls -al'], shell=True)
			
p = subprocess.Popen(["ssh","bk94994@swmapetldev01.nam.nsroot.net",'ls -al'], stdout=subprocess.PIPE,stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
output=' '
out=[]
status=0
i=0
#print p.stdout.readline()
_pass = 'prince987!' #getpass('Enter your superduper password:')
p.stdin.write(_pass)
#p.stdin.write(r'\n')
#print p.stdout.readline()

#out = p.stdout.readline()
#print '--',out
#p.stdin.write('prince987!\n')
#p.communicate()[0]
#p.stdin.close()

#grep_stdout = proc.communicate(input='prince987!\n')
#grep_stdout = proc.communicate(input='\n')
#print grep_stdout

if 1:
	while output:
		output = p.stdout.readline() 
		print i,output
		out.append(output)
		i +=1
		if output.strip()=='Password:':
			print 'enter password'
	print i
	print out
if 0:	
	error=' '
	err=[]
	while error:
		error = proc.stderr.readline()						
		err.append(error)
	if err:
		print '#'*20, ' ERROR ','#'*20
		print '###','\n'.join(err)
		print '#'*20, ' ERROR ','#'*20
	#print 'after out, err'