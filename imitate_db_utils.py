import odbc, sys, dbi
import datetime
#import common_utils as cu
from tc_lib import  send
#blog= cu.BrowserLog()

srv={'SMARTU1A':'mapswdbun1-vip.nam.nsroot.net'}
def printerr(err):
	print '#'*60
	print '#'*26,'ERROR!', '#'*26
	print '#'*60
	print err
	print '#'*60
	print '#'*60
def query( sql, connect_as, pos=None, limit=100, caller='query_test'):
	#global db
	print connect_as
	(user,db, pwd, host, port) = connect_as
	#(db,user)= ('MRR_BI','MRR_ETL_USER')
	assert sql, 'sql statement is not defined'
	assert db, 'Database is not set'
	assert user, 'User is not set'
	#if _db: db = _db
	#db1='MRR'
	#blog.log('Connecting to %s as %s ...' % (db, user),pos)
	if pos:
		send( "append_browser_log", ('Connecting to %s as %s ...' % (db, user),pos) )
	#print 'Connecting to %s as %s ...' % (db, user)
	#mapswdbun2-vip.nam.nsroot.net
	cs ='Driver={Microsoft ODBC for Oracle};SERVER=mapswdbdn1.nam.nsroot.net:11150/%s;UID=%s;PWD=%s;'  % (db,user,pwd)
	if db=='SMARTP_B':
		cs ='Driver={Microsoft ODBC for Oracle};SERVER=mapmwdbpn1-vip.nam.nsroot.net:11150/%s;UID=%s;PWD=%s;'  % (db,user,pwd)
	if db=='SMARTU1A':
		cs ='Driver={Microsoft ODBC for Oracle};SERVER=mapswdbun1-vip.nam.nsroot.net:11150/%s;UID=%s;PWD=%s;'  % (db,user,pwd)		
	print cs
	err=None
	rowcount=None
	headers=[]
	status=0
	out=[]
	#blog.log('Fetching %s...' % (caller[3:]),pos)
	if pos:
		send( "append_browser_log", ('Fetching %s...' % (caller[3:]),pos) )
	print caller
	print sql
	#sys.exit(1)
	if caller in 'query_test':
		#print 'bytes from DBA_TS_QUOTAS'
		#print sql
		#print caller
		headers=[('Schema',),('Type',),('ID',),('CreateDt',)]
		ts=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		for i in range(10):
			out.append(('OWNER_%d' %i,'user',i,ts))	
		print out 
	if caller in 'getOwners':
		#print 'bytes from DBA_TS_QUOTAS'
		print sql
		print caller
		ts=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		for i in range(10):
			out.append(('OWNER_%d' %i,'user',i,ts))
	if caller in 'getTables':
		print sql
		print caller
		ts=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		for i in range(10):
			out.append(('TABLE_%d' %i,'table','NO',i,ts))	
		for i in range(10,20):
			out.append(('PTABLE_%d' %i,'table','YES',i,ts))
		for i in range(20,30):
			out.append(('SPTABLE_%d' %i,'table','YES',i,ts))
			
	if caller in 'getPartitions':
		print sql
		print caller
		ts=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		for i in range(10):
			out.append(('PARTITION_%d' %i,'part','NO',i,ts))
		for i in range(10,20):
			out.append(('PARTITION_%d' %i,'part','YES',i,ts))			
	if caller in 'getSubPartitions':
		print sql
		print caller
		ts=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		for i in range(20):
			out.append(('SUBPARTITION_%d' %i,'spart',i,ts))
	if caller in 'getTableColumns':
		print sql
		print caller
		ts=datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
		for i in range(20):
			out.append(('COLUMN_%d' %i,'VARCHAR2',50,'column',i,ts))
			
	#sys.exit(1)
	#blog.log('Got %d rows.' % (len(out)),pos)
	if pos:
		send( "append_browser_log", ('Got %d rows.' % (len(out)),pos) )
	return (status, err, rowcount,headers, out)