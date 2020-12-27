import paramiko


hostname = 'swmapetldev01.nam.nsroot.net'
password = 'prince987!'
username = "bk94994"
port = 22

mypath='C:\\Python27.2.5\\_TaCo_\\Projects\\table_copy\\out\\tc_copy_test.xml'
remotepath='/opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy/pipeline/posix/tc_copy_test.xml'


t = paramiko.Transport((hostname, 22))
t.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(t)
print sftp.put(mypath, remotepath)