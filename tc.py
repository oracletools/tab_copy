#!/usr/bin/python
import sys
sys.setrecursionlimit(100)
if 0:
	import wxversion
	import wxversion as wv
	wv.select("3.0")
	
import wx

import wx.aui
import wx.lib.agw.aui as aui
import os, sys, types
import time
import cPickle
from pprint import pprint
import wx.lib.agw.ultimatelistctrl as  uListCtrl
from itertools import chain

from cache_lib import ifCacheExists, loadCache, writeToCache, readFromCache, gCache, gCacheLoc
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
from tc_lib import tc_runat, tc_loc, tc_host, tc_home, tc_srv
from tc_lib import sub, send
#from tc_lib import  EVT_SIGNAL, SignalEvent
from pprint import pprint
import xml.dom.minidom
from xml.dom.minidom import Node
import common_utils as cu
import wx.lib.mixins.listctrl as listmix
from partition_copy import PartitionCopyDialog, ExecPcThread
from subpartition_copy import SubPartitionCopyDialog, ExecSPcThread
#from query_copy import QueryCopyDialog, ExecQcThread
from query_copy_panel import ExecQcThread
from table_cpy import TableCopyPanel, ExecTcThread
from design_panel import DesignPanelManager

#from wx.lib.pubsub import Publisher
from wx.lib.mixins.listctrl import TextEditMixin
from editor import TacoCodeEditor, TacoTextEditor

from collections import OrderedDict
import EnhancedStatusBar as ESB
from wx.lib.ticker import Ticker
from wx.lib.splitter import MultiSplitterWindow
from threading import Thread

#import threading
import inspect
import ctypes
import subprocess

import images
#198za8j
from xml.dom.minidom import Document
import wx.lib.agw.flatnotebook as fnb
import glob
import datetime
#from TacoSQL import SimpleSQLEditor #CodeEditor,QueryPanel, TabPanel,SQLPanel
#from TacoXML import SimpleXMLEditor

imgs=None
try:
	from agw import genericmessagedialog as GMD
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.genericmessagedialog as GMD
import win32con, win32file
import pywintypes	
from tc_init import *

try:
    from agw import ultimatelistctrl as ULC
except ImportError: # if it's not there locally, try the wxPython lib.
    from wx.lib.agw import ultimatelistctrl as ULC
import random

ALLOW_AUI_FLOATING = False

EVT_SIGNAL_ID = wx.NewId()
 
def EVT_SIGNAL(win, func):
    """Define Signal Event."""
    win.Connect(-1, -1, EVT_SIGNAL_ID, func)

class SignalEvent(wx.PyEvent):
    """Simple event to carry arbitrary signal data."""
    def __init__(self, signal,data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_SIGNAL_ID)
		self.signal = signal
		self.data = data
imitateOracle=False
if imitateOracle:
	import imitate_db_utils as dbu
else:
	import db_utils as dbu
def_ppl_prof='Parallel'
def_w_prof='Compress/Copy/Rebuild indexes/Stats'
_OFF='OFF'
_ON='ON'
_truncate='Truncate'
_compress='Compress'
_stats='Stats'
_reb_idx= 'Rebuild Indexes'
_shards='Shards'
_copyd='Copy data'
_createtab='Create table'
_flags={}
_headers=					(_truncate,	_compress,	_stats,	_reb_idx,	_shards,_createtab,	_copyd	)
_flags['Quick Copy']=		(_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_ON	)
_flags[def_w_prof]=		(_OFF,		_ON,		_ON,	_ON,		_OFF,	_OFF,		_ON	)
_flags['Truncate/Copy']=	(_ON,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_ON	)
_flags['Truncate Table']=	(_ON,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_OFF)
_flags['Create Table']=		(_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_ON,		_OFF)
_flags['Create/Copy']=		(_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_ON,		_ON	)
_flags['Custom']=			(None,		None,		None,	None,		None,	None,		None)


cp={profile:{title:flag for (title,flag) in zip(_headers,flags)} for (profile, flags) in _flags.items()}
	
#pprint(cp)

#print _qc		
#sys.exit(1)
gTableCache='global.tables'
gTableColumnsCache='global.tables.columns'
gDatabaseCache='global.databases'
gConfigCache='global.config'
gOwnersCache='global.owners'
gEnvironmentCache= 'global.environment'
gConnectListCache='global.connections'
branchingList='ConnectList' #list where we define if it's a db or a host connection
dBtn='N/A'
bLevel=100
iLevel=200
DIR_EXCLUDES = set(['.', '..'])
MASK = win32con.FILE_ATTRIBUTE_DIRECTORY | win32con.FILE_ATTRIBUTE_SYSTEM
REQUIRED = win32con.FILE_ATTRIBUTE_DIRECTORY
FindFilesW = win32file.FindFilesW


		
#blog= cu.BrowserLog()
blog=cu.blog

def get_dir_size(path):
	total_size = 0
	try:
		items = FindFilesW(path + r'\*')
	except pywintypes.error, ex:
		return total_size

	for item in items:
		total_size += item[5]
		if (item[0] & MASK == REQUIRED):
			name = item[8]
			if name not in DIR_EXCLUDES:
				total_size += get_dir_size(path + '\\' + name)

	return total_size
dir='c:\\Temp\TC'	
if 0:
	dirs =[]
	files=[]
	for dirname, dirnames, filenames in os.walk(dir):
		#print dirname
		dirs= dirnames
		files=filenames
		break
	print dirs
	print files
	#both = sorted(dirs+files)
	for d in dirs:
		dloc=os.path.join(dir,d)
		dsize=get_dir_size(dloc)
		mtime =  datetime.datetime.fromtimestamp(round(os.path.getmtime(dloc)))
		print d, 'dir', dsize, mtime, oct(os.stat(os.path.join(dir,d)).st_mode)
	for f in files:
		floc=os.path.join(dir,f)
		fsize=os.path.getsize(floc)
		mtime =  datetime.datetime.fromtimestamp(round(os.path.getmtime(floc)))
		print  f,'file',fsize, mtime,oct(os.stat(floc).st_mode)

#pprint(dir(os.path))
		
if 0:

	print os.listdir(dir) 
if 0:	
	print glob.glob('c:\\Temp\TC\*')	
if 0:	
	print get_dir_size('c:\\')/1024.0
#sys.exit(1)
def createPipelineConfig(cfrom,cto,config_file):
	#create config file
	path_from=cfrom.split('/')
	spec_file_name_from=path_from[1]
	out={}
	specfile_from ='%s.xml' % os.path.join(configDirLoc, spec_file_name_from)	
	if os.path.isfile(specfile_from):
		#doc = xml.dom.minidom.parse(specfile_from)
		doc = xml.dom.minidom.parseString(open(specfile_from, "r").read().replace('\n', '').replace('\r', ''))

		
		
		doc_to = Document()
		
		base = doc_to.createElement('test_spec')
		doc_to.appendChild(base)
		
		ps=doc.getElementsByTagName("process_spec")
		base.appendChild(ps[0])
		
		conn = doc_to.createElement('connector')
		
		base.appendChild(conn)
		
		
		from_conn=getXMLConnector(doc,path_from[2],path_from[3])
		
		conn.appendChild(from_conn)
		if cfrom<>cto:
			path_to=cto.split('/')
			spec_file_name_to=path_to[1]
			specfile_to ='%s.xml' % os.path.join(configDirLoc, spec_file_name_to)
			if os.path.isfile(specfile_to):
				doc = xml.dom.minidom.parse(specfile_to)
				to_conn=getXMLConnector(doc,path_to[2],path_to[3])		
				conn.appendChild(to_conn)
				
		ps=doc.getElementsByTagName("default")
		base.appendChild(ps[0])
		
		ps=doc.getElementsByTagName("worker")
		base.appendChild(ps[0])			
		#print doc_to.toxml()			
		out_dir=os.path.join(activeProjLoc,'out')
		#config_file='temp_spec.xml'
		out_file=os.path.join(out_dir,config_file)
		f = open(out_file,'w')
		#pprint(doc_to.toprettyxml())
		#sys.exit(1)
		pretty_print =  '\n'.join([line for line in doc_to.toprettyxml(indent=' '*2).split('\n') if line.strip()])
		f.write(pretty_print)
		f.close()
		#remote_loc='/opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy' 
		#print 'echo %s|pscp %s\\%s bk94994@swmapetldev01.nam.nsroot.net:%s' % (lpwd,out_dir,config_file,remote_loc)
		#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd,out_dir,config_file,remote_loc))
		(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]
		remote_loc='%s/%s' % (tc_path, config_path) 
		#print 'echo %s|pscp %s\\%s bk94994@swmapetldev01.nam.nsroot.net:%s' % (lpwd,out_dir,worker_file,remote_loc)
		#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,worker_file,remote_loc))
		rcopyFile(out_file,'%s/%s' % (remote_loc,config_file))
		#sys.exit(1)
	return (out_dir,remote_loc, config_file)

def getXMLConnector( doc, conn_env, conn_name):
	conn=doc.getElementsByTagName("connector")[0]
	assert conn, 'Cannot find connector tag.'
	print conn_env
	env_type=conn_env.split('.')[0]
	env=conn.getElementsByTagName(env_type)[0]
	alias_name=conn_env.split('.')[1]
	alias=env.getElementsByTagName(alias_name)[0]
	
	connector=alias.getElementsByTagName(conn_name)[0]	
	return connector
def createPipelineWorker(cfrom,cto,config, worker_file,tables,  _tcmode):
	#create config file
	max_shards=20
	print appLoc
	db_from =cfrom.split('/')[3]
	db_to =cto.split('/')[3]
	schema_from =cfrom.split('/')[len(cfrom.split('/'))-1]
	schema_to =cto.split('/')[len(cto.split('/'))-1]
	
	tmpl_loc=os.path.join(appLoc,'xml_templates')
	template_name='table_copy.xml'
	tmpl_file_loc= os.path.join(tmpl_loc,template_name)
	doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
	#doc = xml.dom.minidom.parse(tmpl_file_loc)
		
	doc_to = Document()
	base = doc_to.createElement('etldataflow')
	base.setAttribute("name","TABLE_COPY")
	base.setAttribute("pipeline_config",config)
	
	#pprint(dir(base))
	doc_to.appendChild(base)
	gl=doc.getElementsByTagName("globals")[0]
	print gl
	flowt= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
	flowt.setAttribute('value',_tcmode)
	fromdb= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
	fromdb.setAttribute('value','%'+db_from+'%')
	todb= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
	todb.setAttribute('value','%'+db_to+'%')	
	toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
	toschema.setAttribute('value',schema_to)
	
	base.appendChild(gl)
	worker_stab=doc.getElementsByTagName("worker")[0].toxml()
	print worker_stab
	#pprint(dir(doc))

	

	not_sharded='OFF'
	
	for key, tabs in tables.items():
		(tab,item) =tabs
		(tab_to,copy_profile, trunc,compress,stats, rebuildIdx,shards, createt, copyd) = item
		print item
		worker=xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
		#pprint(dir(worker))
		worker.setAttribute('name', tab_to)
		#param=worker.getElementsByTagName("param")[0]
		for n in worker.getElementsByTagName("param") :
			print n.getAttribute('name')
		#param= [n for n in worker.getElementsByTagName("param") if n.getAttribute('name')=='PARTITION'][0]
		##
		##non-partitioned table copy
		##
		#param.setAttribute('name','IGNORE_%s' % param.getAttribute('name'))
		exec_copy=worker.getElementsByTagName("exec_copy")[0]
		
		tasklet=worker.getElementsByTagName("sqlp")[0]
		if 1 : #tab<>tab_to:
			
			param = doc_to.createElement('param')
			param.setAttribute('name','TO_TABLE')
			param.setAttribute('value',tab_to)
			tasklet.appendChild(param)
		#modify CDATA
		if shards ==not_sharded:
			pass
		else:
			assert int(shards)>2 and int(shards)<max_shards, 'Num of shards should be between 2 and %d per table.'  % max_shards
			param = doc_to.createElement('param')
			param.setAttribute('name','NUM_OF_SHARDS')
			param.setAttribute('value',shards)
			tasklet.appendChild(param)
		print trunc
		if 	trunc in ('ON', 'OFF'):
			#Truncate should be "ON" or "OFF".
			param = doc_to.createElement('param')
			param.setAttribute('name','IF_TRUNCATE')
			tr={'ON':"1",'OFF':"0"}
			param.setAttribute('value',tr[trunc])
			tasklet.appendChild(param)	
		print compress 
		if 	compress=='ON':
			assert compress in ('ON', 'OFF'), 'Compress should be "ON" or "OFF".'
			tmpl_loc=os.path.join(appLoc,'xml_templates')
			template_name='compress_table.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))

			comp_tasklet=doc.getElementsByTagName("exec_select")[0]

			_table_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TABLE_NAME'][0]
			_table_name.setAttribute('value',tab_to)
			_dbconn=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='DB_CONNECTOR'][0]
			_dbconn.setAttribute('value','%'+db_to+'%')
			_schema_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SCHEMA_NAME'][0]
			_schema_name.setAttribute('value',schema_to)

			worker.insertBefore(comp_tasklet,exec_copy)
		print stats
		if 	stats=='ON':
			assert stats in ('ON', 'OFF'), 'Stats should be "ON" or "OFF".'
			tmpl_loc=os.path.join(appLoc,'xml_templates')
			template_name='gather_table_stats.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))

			stats_tasklet=doc.getElementsByTagName("exec_select")[0]

			_table_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TABLE_NAME'][0]
			_table_name.setAttribute('value',tab_to)
			_dbconn=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='DB_CONNECTOR'][0]
			_dbconn.setAttribute('value','%'+db_to+'%')
			_schema_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SCHEMA_NAME'][0]
			_schema_name.setAttribute('value',schema_to)

			worker.appendChild(stats_tasklet)
	
		if 	rebuildIdx in ('ON', 'OFF'):
			print 'rebuildIdx', rebuildIdx
			#rebuildIdx should be "ON" or "OFF"
			param = doc_to.createElement('param')
			param.setAttribute('name','SKIP_INDEX_MAINTENANCE')
			tr={'ON':"TRUE",'OFF':"FALSE"}
			param.setAttribute('value','TRUE')
			tasklet.appendChild(param)		
			param = doc_to.createElement('param')
			param.setAttribute('name','IF_REBUILD_UNUSABLE_INDEXES')
			tr={'ON':"1",'OFF':"0"}
			param.setAttribute('value',tr[rebuildIdx])
			tasklet.appendChild(param)	

			
		cd= [n for n in tasklet.getElementsByTagName("sql_template")[0].childNodes if n.nodeType==worker.CDATA_SECTION_NODE][0]
		#for n in cd.childNodes:
		#	print n
		#pprint(dir(cd))
		
		#schema= cd.wholeText.split('.')[0]
		cd.data='%s.%s' % (schema_from, tab)
		#param=worker.getElementsByTagName("param")[0]
		base.appendChild(worker)
	#print doc_to.toprettyxml()
	
	out_dir=os.path.join(activeProjLoc,'out')
	#worker_file='tc_temp_worker.xml'
	out_file=os.path.join(out_dir,worker_file)
	f = open(out_file,'w')
	#from xml.dom.minidom import parseString

	pretty_print =  '\n'.join([line for line in doc_to.toprettyxml(indent=' '*2).split('\n') if line.strip()])

#echo prince987!|pscp C:\Python27.2.5\_TaCo_\Projects\table_copy\out\tc_copy_test.xml bk94994@swmapetldev01.nam.nsroot.net:/opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy

	f.write(pretty_print)
	f.close()
	#remote_loc='/home/zkqfas6/tab_copy/clients/table_copy/tab_copy'
	(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]
	remote_loc='%s/%s' % (tc_path, client_path) 
	print 'echo %s|pscp %s\\%s bk94994@swmapetldev01.nam.nsroot.net:%s' % (lpwd,out_dir,worker_file,remote_loc)
	#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,worker_file,remote_loc))
	rcopyFile(os.path.join(out_dir,worker_file),'%s/%s' % (remote_loc,worker_file))
	#create worker file
	return (out_dir,worker_file,remote_loc)

def execRemoteCmd(specs, worker):
	#import paramiko, sys

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	(username, password, hostname) = tc_host[tc_srv]
	ssh.connect(hostname, username=username, password = password )
	#ssh.exec_command( 'ls -al' )	
	#stdin,stdout,stderr = ssh.exec_command("cd /opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy;. ./.ora_profile;./run.sh t tab_copy;")
	cmd='time python tc.py --pipeline_spec=%s --pipeline=%s;' % (specs, worker)
	print cmd
	print specs
	print worker
	stdin,stdout,stderr = ssh.exec_command("cd /opt/etl/apps/smart_dev/volumes/etl/scripts/tab_copy;. ./.ora_profile;%s" % cmd)
	
	#time python tc.py --pipeline_spec=pipeline/posix/pipeline_spec.xml --pipeline=clients/table_copy/tab_copy/tc_t.xml

	
	#stdin,stdout,stderr = ssh.exec_command("pbrun voletlusr")

	out= stdout.read()
	err= stderr.read()
	if err:
		print '#'*40
		print err.strip()
		print '#'*40
	#sys.exit(1)
	
	return (out,err)


def execTaCo( specs, worker):
	print specs
	print worker
	#plink_loc=r'C:\Program Files\PuTTY'
	#command = r"%s\plink.exe -ssh zkqfas6@lrche25546 -pw %s cd tab_copy;time python tc.py --pipeline_spec=%s --pipeline=%s" % (plink_loc, lpwd, specs,worker)
	#print command
	(out, err) = execRemoteCmd(specs, worker)
	#sys.exit(1)	
	return (out,err)
	
#C:\Program Files\PuTTY\plink.exe -ssh bk94994@swmapetldev01 -pw prince987! ls -al

#C:\Python27.2.5\_TaCo_>"C:\Program Files\PuTTY\plink.exe" -ssh bk94994@swmapetldev01.nam.nsroot.net -pw prince987! cd C:\Program Files\PuTTY\plink.exe

#;time python tc.py --pipeline_spec=/home/zkqfas6/tab_copy/pipeline/posix/temp_sp
#ec.xml --pipeline=/home/zkqfas6/tab_copy/clients/table_copy/tab_copy/tc_copy_tes
#t.xml
	
	#status=os.popen(command).read()
	if 0:
		proc = subprocess.Popen(["%s\plink.exe" % plink_loc, "-ssh", "zkqfas6@lrche25546", "-pw", lpwd, "cd tab_copy;time python tc.py --pipeline_spec=%s --pipeline=%s" % (specs,worker)], stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
		output=' '
		out=[]
		status=0
		while output:
			output = proc.stdout.readline() #string.replace(p2.stdout.readline(),'SQL>','')
			print output
			out.append(output)
		error=' '
		err=[]
		while error:
			error = proc.stderr.readline()						
			err.append(error)
		print 'after communicate'
		print out
		print err
		if err:
			print '#'*20, ' ERROR ','#'*20
			print '###'.join(err)
			print '#'*20, ' ERROR ','#'*20
		#print "program output:", out

		return (out,err)
#file_name=''	
config_file=None
if 0:
	cfrom='root/pipeline_spec.xml/dev.DEV_NZ2/ETL_MRR_BI_2/MRR_BI/MRR_ETL_USER'
	cto='root/pipeline_spec.xml/dev.DEV_NZ2/ETL_MRR/MRR_BI/MRR_DW_ADMIN'
	(local_path,remote_path, config_file)=createPipelineConfig(None,cfrom,cto)		
	#sys.exit(1)		
if 0:
	cfrom='root/pipeline_spec.xml/dev.DEV_NZ2/ETL_MRR_BI_2/MRR_BI/MRR_ETL_USER'
	cto='root/pipeline_spec.xml/dev.DEV_NZ2/ETL_MRR/MRR_BI/MRR_DW_ADMIN'
	tables={'CB_DL_D_HCY_NODE_LKUP': ['CB_DSHB_BKMAP_ATTR_LCL_RGN_TD_VW_BKP',
                           'CB_DSHB_BKMAP_ATTR_LCL_RGN_TD_VW_BKP_COPY_',
                           'Not sharded'],
 'CB_DL_D_VAR_CB_MTRC_MTDATA': ['CB_DL_FLAT_ORH_HCY_VW_BKP',
                                'CB_DL_FLAT_ORH_HCY_VW_BKP_2',
                                'Not sharded'],
 'CB_DL_FLAT_ORH_HCY_VW_BKP': ['CB_DL_D_VAR_CB_MTRC_MTDATA',
                               'CB_DL_D_VAR_CB_MTRC_MTDATA',
                               '6'],
 'CB_DSHB_BKMAP_ATTR_LCL_RGN_TD_VW_BKP': ['CB_DL_D_HCY_NODE_LKUP',
                                          'CB_DL_D_HCY_NODE_LKUP',
                                          'Not sharded']}
	print  tables
	(out_dir,worker_file,remote_loc) = createPipelineWorker(None,cfrom,cto,'%s/%s' % (remote_path,config_file),tables)	

if 0:	
	print remote_path, config_file
	print remote_loc,worker_file
	execTaCo('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file))	
	sys.exit(1)		 

#time python tc.py --pipeline_spec=/home/zkqfas6/tab_copy/pipeline/posix/temp_spec.xml --pipeline=/home/zkqfas6/tab_copy/clients/table_copy/tab_copy/tc_temp_worker.xml


#C:\Users\zkqfas6\Installs\putty\plink.exe -ssh zkqfas6@lrche25546 -pw 400Grove ls -al /home/zkqfas6/tab_copy/tmp/logs/lines

	
# Thread class that executes processing
def listRemoteDir(connect, path):
	(user,host,pwd) = connect
	print 'listRemoteDir'
	#C:\Users\zkqfas6\Installs\putty>plink.exe -ssh zkqfas6@lrche25546 -pw 300Grove c
	#print specs
	#print worker
	#plink_loc=r'C:\Users\zkqfas6\Installs\putty'
	#command = r"%s\plink.exe -ssh zkqfas6@lrche25546 -pw 300Grove ls -al %s" % (plink_loc,path)
	#status=os.popen(command).read()
	print "C:\Users\zkqfas6\Installs\putty\plink.exe", "-ssh", "%s@%s" % (user,host), "-pw", pwd, "ls -al %s" % (path)
	print ' '.join(["C:\Users\zkqfas6\Installs\putty\plink.exe", "-ssh", "%s@%s" % (user,host), "-pw", pwd, "ls -al %s" % (path)])
	proc = subprocess.Popen(["C:\Users\zkqfas6\Installs\putty\plink.exe", "-ssh", "%s@%s" % (user,host), "-pw", pwd, "ls -al %s" % (path)], stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
	output=' '
	out=[]
	status=0
	while output:
		output = proc.stdout.readline() #string.replace(p2.stdout.readline(),'SQL>','')
		print output
		out.append(output)
	error=' '
	err=[]
	while error:
		error = proc.stderr.readline()						
		err.append(error)
	#(out, err) = proc.communicate()
	#print 'after communicate'
	#print proc
	#pprint (out)
	#print out.split('\n')
	if err:
		print '#'*20, ' ERROR ','#'*20
		print '###','\n'.join(err)
		print '#'*20, ' ERROR ','#'*20
	#print 'after out, err'
	return out[3:-1]
		
#pscp  uname@MachineB:/export/home/uname/aa.txt c:\documents\foo.txt
		
#echo 198za8j|C:\Users\zkqfas6\Installs\putty\pscp.exe -C C:\Temp\TC\data\10d_test.MRR_ETL_USER.TCL_baG3d0.data zkqfas6@lrche25546:/home/zkqfas6/in		

#echo 198za8j|C:\Users\zkqfas6\Installs\putty\pscp.exe -C zkqfas6@lrche25546:/home/zkqfas6/in/10d_test.MRR_ETL_USER.TCL_baG3d0.data	 C:\Temp\TC\data\in	
		
class RemoteDirThread(Thread):
	"""Worker Thread Class."""
	def __init__(self,pos,cache, path, login,file_filter):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self.login = login
		self.path=path
		self.pos=pos
		self.cache=cache
		self.file_filter=file_filter
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()

	def run(self):
		"""Run Worker Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable
		#print self.q, self.user,self.limit
		
		#self.result=dbu.query(self.q, (self.user,self.sid,self.pwd), self.limit)
		files = listRemoteDir(self.login, self.path)

		print files
		#sys.exit(1)
		#files.sort(reverse=True)
		ta={}
		for i in range(len(files)):
			f=files[i].split()
			#st= os.stat(os.path.join(configDirLoc,f))
			#pprint(st)
			#print f
			ftype='file'
			changed='%s %s %s' % (f[5],f[6],f[7])
			name=f[8]
			ext=''
			s=name.split('.')
			if len(s)>1:
				ext=s[-1]
			#item=f[8]
			if f[0][0]=='d':
				ftype='dir'
				#item='[%s]' % f[8]
			r = (name,ftype,ext.strip(),int(f[4].strip()),f[0][1:].strip(),changed)
			#print time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(st.st_atime))
			#print r
			ta[i]=r
		self.result=ta			
		#sys.exit(1)

		# Here's where the result would be returned (this is an
		# example fixed result of the number 10, but it could be
		# any Python object)
		#self.db.result=42
		#Publisher().sendMessage( "remotedir_thread_event", ('done',self.pos,self.cache,self.result) )
		#Publisher().sendMessage( "stop_db_progress_gauge", (self.pos) )
		send( "remotedir_thread_event", ('done',self.pos,self.cache,self.result) )
		send( "stop_db_progress_gauge", (self.pos) )
	def abort1(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		print 'DbThread aborted'
		#Publisher().sendMessage( "db_thread_event", ('aborted') )
		self.result=None
		#pprint(dir(Thread))
		#self.abort()
		#Thread.abort(self)
		#return
		#self._Thread__stop()

	def _get_my_tid(self):
		"""determines this (self's) thread id"""
		if not self.isAlive():
			raise threading.ThreadError("the thread is not active")
		
		# do we have it cached?
		if hasattr(self, "_thread_id"):
			return self._thread_id
		
		# no, look for it in the _active dict
		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = tid
				return tid
		
		raise AssertionError("could not determine the thread's id")
	
	def raise_exc(self, exctype):
		"""raises the given exception type in the context of this thread"""
		_async_raise(self._get_my_tid(), exctype)
	
	def terminate(self):
		"""raises SystemExit in the context of the given thread, which should 
		cause the thread to exit silently (unless caught)"""
		self.raise_exc(SystemExit)
	
class LocalDirThread(Thread):
	"""Worker Thread Class."""
	def __init__(self,pos,cache, path, login, file_filter=None):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self.login = login
		self.path=path
		self.pos=pos
		self.cache=cache
		self.file_filter=file_filter
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()

	def run(self):
		"""Run Worker Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable
		#print self.q, self.user,self.limit
		
		
		dirs =[]
		files=[]
		for dirname, dirnames, filenames in os.walk(self.path):
			#print dirname
			dirs= dirnames
			files=filenames
			break
		print dirs
		print files
		#both = sorted(dirs+files)
		ta={}
		i=0
		#sys.exit(1)
		for d in dirs:
			dloc=os.path.join(self.path,d)
			dsize=get_dir_size(dloc)
			mtime =  datetime.datetime.fromtimestamp(round(os.path.getmtime(dloc)))
			ext=''
			r = ( d, 'dir', ext,dsize,  oct(os.stat(os.path.join(self.path,d)).st_mode),mtime)
			ta[i]=r
			i +=1
		ffiles=files
		if self.file_filter:
			filters= [ext.split('.')[1] for ext in self.file_filter.split(',')]
			print filters
			ffiles=[f for f in files if f.split('.')[1] in filters]
			print  ffiles
		for f in ffiles:
			floc=os.path.join(self.path,f)
			fsize=os.path.getsize(floc)
			mtime =  datetime.datetime.fromtimestamp(round(os.path.getmtime(floc)))
			ext=''
			s=f.split('.')
			if len(s)>1:
				ext=s[-1]				
			r = (  f,'file',ext,fsize, oct(os.stat(floc).st_mode),mtime)
			ta[i]=r
			i +=1
		#pprint(ta)
		self.result=ta			
		#sys.exit(1)

		#Publisher().sendMessage( "localdir_thread_event", ('done',self.pos,self.cache,self.result) )
		#Publisher().sendMessage( "stop_db_progress_gauge", (self.pos) )
		send("localdir_thread_event", ('done',self.pos,self.cache,self.result) )
		send( "stop_db_progress_gauge", (self.pos) )
	def abort1(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		print 'DbThread aborted'
		#Publisher().sendMessage( "db_thread_event", ('aborted') )
		self.result=None
		#pprint(dir(Thread))
		#self.abort()
		#Thread.abort(self)
		#return
		#self._Thread__stop()

	def _get_my_tid(self):
		"""determines this (self's) thread id"""
		if not self.isAlive():
			raise threading.ThreadError("the thread is not active")
		
		# do we have it cached?
		if hasattr(self, "_thread_id"):
			return self._thread_id
		
		# no, look for it in the _active dict
		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = tid
				return tid
		
		raise AssertionError("could not determine the thread's id")
	
	def raise_exc(self, exctype):
		"""raises the given exception type in the context of this thread"""
		_async_raise(self._get_my_tid(), exctype)
	
	def terminate(self):
		"""raises SystemExit in the context of the given thread, which should 
		cause the thread to exit silently (unless caught)"""
		self.raise_exc(SystemExit)

class DbThread(Thread):
	"""Worker Thread Class."""
	def __init__(self,obj, pos,cache, q, login, limit):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self.login=login
		self.obj=obj
		(self.user,self.sid,self.pwd,self.host,self.port) = login
		self.limit=limit
		self.q=q
		self.pos=pos
		self.cache_loc=cache
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()
	def send(self, signal, data):
		wx.PostEvent(self.obj, SignalEvent(signal, data))
	def run(self):
		"""Run Worker Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable
		print self.q, self.user,self.limit
		global fn
		if use_cache and self.cache_loc and ifCacheExists(self.cache_loc):
			print 'cache exists',self.cache_loc
			#blog.log('Using cache for %s' % self.cache_loc.split('/')[-1], self.pos)
			self.send( "append_browser_log", ('Using cache for %s' % self.cache_loc.split('/')[-1],self.pos) )
			self.result=readFromCache(self.cache_loc)
			#print '+++++reading from cache::::::::::::::::::::'
			#print ta
			#sys.exit(1)
			#result=(0, [], 0, [], ta)
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			#Publisher().sendMessage( "db_thread_event", ('done',self.pos,self.cache_loc,ta) )
			#Publisher().sendMessage( "stop_db_progress_gauge", (self.pos) )
			#return ta
		else:
			self.result=dbu.query(self.q, self.login, pos=self.pos,limit=self.limit, caller=fn)

			

		# Here's where the result would be returned (this is an
		# example fixed result of the number 10, but it could be
		# any Python object)
		#self.db.result=42
		#Publisher().sendMessage( "db_thread_event", ('done',self.pos,self.cache_loc,self.result) )
		#Publisher().sendMessage( "stop_db_progress_gauge", (self.pos) )
		self.send( "db_thread_event", ('done',self.pos,self.cache_loc,self.result))
		self.send( "stop_db_progress_gauge", (self.pos) )
		if update_cache:
			writeToCache(self.cache_loc, self.result)			

	def abort1(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		print 'DbThread aborted'
		#Publisher().sendMessage( "db_thread_event", ('aborted') )
		self.result=None
		#pprint(dir(Thread))
		#self.abort()
		#Thread.abort(self)
		#return
		#self._Thread__stop()

	def _get_my_tid(self):
		"""determines this (self's) thread id"""
		if not self.isAlive():
			raise threading.ThreadError("the thread is not active")
		
		# do we have it cached?
		if hasattr(self, "_thread_id"):
			return self._thread_id
		
		# no, look for it in the _active dict
		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = tid
				return tid
		
		raise AssertionError("could not determine the thread's id")
	
	def raise_exc(self, exctype):
		"""raises the given exception type in the context of this thread"""
		_async_raise(self._get_my_tid(), exctype)
	
	def terminate(self):
		"""raises SystemExit in the context of the given thread, which should 
		cause the thread to exit silently (unless caught)"""
		self.raise_exc(SystemExit)

		
def _async_raise(tid, exctype):
	"""raises the exception, performs cleanup if needed"""
	if not inspect.isclass(exctype):
		raise TypeError("Only types can be raised (not instances)")
	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
	if res == 0:
		raise ValueError("invalid thread id")
	elif res != 1:
		# """if it returns a number greater than one, you're in trouble, 
		# and you should call it again with exc=NULL to revert the effect"""
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
		raise SystemError("PyThreadState_SetAsyncExc failed")
		
def terminate_thread(thread):
	"""Terminates a python thread from another thread.

	:param thread: a threading.Thread instance
	"""
	if not thread.isAlive():
		print 'it''s already dead'
		return

	exc = ctypes.py_object(SystemExit)
	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
		ctypes.c_long(thread.ident), exc)
	print 'Terminated!'
	if res == 0:
		raise ValueError("nonexistent thread id")
	elif res > 1:
		# """if it returns a number greater than one, you're in trouble,
		# and you should call it again with exc=NULL to revert the effect"""
		ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
		raise SystemError("PyThreadState_SetAsyncExc failed")
fn=None
def print_name(func, *args, **kwargs):
	def f(*args, **kwargs):
		print func.__name__
		return func(*args, **kwargs)
	return f
def set_name(func, *args, **kwargs):
	def f(*args, **kwargs):
		global fn 
		fn = func.__name__
		print fn
		return func(*args,  **kwargs)
	return f		
class OracleDb(wx.Object):
	"""Db Class."""
	def __init__(self, parent, pos):
		self.result=None
		self.worker=None
		self.parent=parent
		self.pos=pos
		#Publisher().subscribe(self.onStopDbRequest, "stop_db_request")
		sub(self.onStopDbRequest, "stop_db_request")
		

		
	def onStopDbRequest(self, evt):
		print 'aborting db request'
		
		if self.worker:			
			#terminate_thread(self.worker)
			#
			#self.worker.join()
			print self.worker.isAlive()
			if self.worker.isAlive():
				
				print 'it''s alive, aborting...'
				#self.worker.abort()
				#self.worker.terminate()
				terminate_thread(self.worker)
				#Publisher().sendMessage( "db_thread_event", ('aborted',self.pos,None, None) )
				send("db_thread_event", ('aborted',self.pos,None, None) )
				#return
		else:
			print 'no worker thread'		
			#Publisher().sendMessage( "db_thread_event", ('done',self.worker.pos,self.worker.cache,self.worker.result) )
	def ifCacheExists(self,relative_path,  suffix=''):
		#cc= cache_key.split('.')
		cfile_name="%s%s.p" % (relative_path.split('/')[-1], suffix)
		cache_loc= os.path.join(gCacheLoc,relative_path)
		cfile=os.path.join(cache_loc,cfile_name)
		print 'reading from1:', cfile
		#sys.exit(1)
		if os.path.isfile(cfile):
			print 'cache exists'
			return True
		else: 
			print 'no cache'
			return False
	def getConfigs(self,configDirLoc):
		ta={}		
		configDirLoc='_CONFIG_'
		if 0 and ifCacheExists(gConfigCache):
			print 'getConfigs cache exists',cache
			ta=readFromCache(gConfigCache)
			#print ta
			#sys.exit(1)
		else:	
			#print configDirLoc 

			
			#os.system('subst z: "%s"' % configDirLoc)
			#configDirLoc=
			files = os.listdir(configDirLoc)
			#print files
			#files.sort(reverse=True)
			for i in range(len(files)):
				f=files[i]
				st= os.stat(os.path.join(configDirLoc,f))
				#pprint(st)
				r = (f.split('.')[0],'config',st.st_size,time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(st.st_atime)))
				#print time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(st.st_atime))
				#print r
				ta[i]=r
			#sys.exit(1)
			
			#ta=out
			#updateCache(gConfigCache,ta)
		
		return ta
		
	def getDatabases(self,login):
		ta={}
		(user,db,pwd,host,port) = login
		cache='%s.%s_%s' % (gDatabaseCache,user,db)
		#print cache
		if use_cache and ifCacheExists(cache):	
			print 'cache exists ',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select v.database,type, TO_CHAR(size,'999,999,999,999.9'),db.createdate FROM
	(select database, 'database' Type, ROUND(sum(used_bytes)/1024/1024,1) size
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	--where objname = 'UPPERCASE_TABLE_NAME'
	group by database) v, _v_database db
	where v.database=db.database order by 1"""
			#Publisher().sendMessage( "show_progress", ((0, 0)) )
			#app.frame.gaugeStart(self.pos)
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send( "start_db_progress_gauge", (self.pos) )
			
			#time.sleep(1)

			#wx.Yield()
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			self.worker = DbThread(self.parent,self.pos,gDatabaseCache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()
			#self.worker.join()
			#pprint(dir(self.worker))
			#app.frame.gaugeStop()
			if 0:
				i=0
				for rec in out:
					ta[i]=rec
					i +=1
				#updateCache(cache,ta)

		#return ta
	def readFromCache_(self, relative_path,  suffix=''):
		#cc= cache_key.split('.')
		cfile_name="%s%s.p" % (relative_path.split('/')[-1], suffix)
		cache_loc= os.path.join(gCacheLoc,relative_path)
		cfile=os.path.join(cache_loc,cfile_name)
		print 'reading from2:', cfile
		if os.path.isfile(cfile):
			s = pickle.load( open(cfile, "rb" ) )
			print s
			sys.exit(1)
			return s
		print 'Cache ', cfile, 'does not exists.'
		return {}
	def writeToCache_(self,relative_path, cache, suffix=''):
		#print 'CREATING CACHE', cache_key
		cc= relative_path.split('/')
		cfile_name="%s%s.p" % (cc[-1],suffix)
		cache_loc=os.path.join(gCacheLoc,relative_path)
		#print cache_loc,cfile_name
		#sys.exit(1)
		if not os.path.isdir(cache_loc):
			os.makedirs(cache_loc)
		cfile=os.path.join(cache_loc,cfile_name)
		print 'writing to:', cfile
		s=pickle.dump(cache, open( cfile, "wb" ))
		#global gCache
		#gCache=loadCache(gCacheLoc,'global')
		#close(cfile)
		#print s	
	@set_name
	def getOwners(self,login,cache_loc=None):
		(user,db,pwd,host,port) = login	
		ta={}
		#sys.exit(1)
		cache='%s.%s_%s' % (gOwnersCache,user,db)
		if 0 and  use_cache and cache_loc and self.ifCacheExists(cache_loc):
			print 'cache exists',cache_loc
			blog.log('Using cache for %s' % cache_loc.split('/')[-1], self.pos)
			ta=readFromCache(cache_loc)
			#print '+++++reading from cache::::::::::::::::::::'
			#print ta
			#sys.exit(1)
			#result=(0, [], 0, [], ta)
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			#Publisher().sendMessage( "db_thread_event", ('done',self.pos,cache_loc,ta) )
			send( "start_db_progress_gauge", (self.pos) )
			send("db_thread_event", ('done',self.pos,cache_loc,ta) )
			#Publisher().sendMessage( "stop_db_progress_gauge", (self.pos) )
			#return ta
			
		else:	
			
			if 1:
				q=""" select v.username,'owner' type, TO_CHAR(ROUND(bytes,2),'999,999,999,999.99')  bytes, created  from (  
select  username, sum(bytes)/1024/1024 bytes from DBA_TS_QUOTAS group by username  ) v, all_users a
where v.username=a.username and bytes>0 order by 1
				""" 
			else:
				q="""select v.username,'owner' type, TO_CHAR(ROUND(bytes,2),'999,999,999,999.99')  bytes, created  from (
select  user username, sum(bytes/1024/1024) bytes from user_ts_quotas   ) v, all_users a
where v.username=a.username and bytes>0 order by 1
				"""
			if  user =='ESMARTREF' and db=='SMARTD1':
				q="""select v.username,'owner' type, TO_CHAR(ROUND(bytes,2),'999,999,999,999.99')  bytes, created  from (
select  user username, sum(bytes/1024/1024) bytes from user_ts_quotas   ) v, all_users a
where v.username=a.username and bytes>0 order by 1
				"""	
			#(db,user) = ('MRR_BI','MRR_ETL_USER')
			print q
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send( "start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			#print __name__
			#print globals()['fn']
			#sys.exit(1)
			self.worker = DbThread(self.parent,self.pos,cache_loc,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()

	@set_name
	def getTables(self,login, location, object_filter, cache_loc):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s' % (gTableCache,user,db,location[0])
		#print cache
		if 0 and   use_cache and cache_loc and self.ifCacheExists(cache_loc):
			print 'cache exists',cache_loc
			blog.log('Using cache for %s' % cache_loc.split('/')[-1], self.pos)
			ta=readFromCache(cache_loc)
			#print '+++++reading from cache::::::::::::::::::::'
			#print ta
			#sys.exit(1)
			#result=(0, [], 0, [], ta)
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			#Publisher().sendMessage( "db_thread_event", ('done',self.pos,cache_loc,ta) )
			#Publisher().sendMessage( "stop_db_progress_gauge", (self.pos) )
			#return ta
		else:	
			q="""select table_name, 'table' type,partitioned,  TO_CHAR( nvl(ROUND(blocks*8/1024,2),0),'999,999,999,999.9') bytes, last_analyzed from all_tables 
where owner='%s' and temporary='N'
--order by 3 desc
	""" % location
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send( "start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,cache_loc,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()
			
	@set_name
	def getPartitions(self,login, location,cache_loc):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s' % (gTableCache,user,db,location[0])
		#print cache
		if use_cache and ifCacheExists(cache):
			
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select partition_name, 'partition' type,composite,  TO_CHAR( nvl(ROUND(blocks*8/1024,2),0),'999,999,999,999.9') bytes,last_analyzed from all_tab_partitions 
where table_owner='%s' and table_name='%s'
	""" % location
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send("start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,cache_loc,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()
	@set_name
	def getSubPartitions(self,login, location,cache_loc):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s' % (gTableCache,user,db,location[0])
		#print cache
		if use_cache and ifCacheExists(cache):			
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select subpartition_name, 'subpartition' type,  TO_CHAR( nvl(ROUND(blocks*8/1024,2),0),'999,999,999,999.9') bytes,last_analyzed  from all_tab_subpartitions v
where table_owner='%s' and table_name='%s' and partition_name='%s'
	""" % location
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send("start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,cache_loc,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()	
	@set_name		
	def getTableColumns(self,login, location,cache_loc):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s_%s' % (gTableColumnsCache,user,db,location[0],location[1])
		if use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select column_name,data_type,data_length,'column' type,  column_id, last_analyzed 
          from all_tab_columns where owner='%s' and UPPER(table_name)=UPPER('%s')
          order by column_id 
	""" % location
			#(db,user) = ('MRR_BI','MRR_ETL_USER')
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send( "start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,cache_loc,q, login, limit=None)
			self.worker.start()

		
	def getEnvironments(self,configFile):
		print configFile
		cache= '%s.%s' % (gEnvironmentCache, os.path.basename(configFile).replace('.','_'))
		#print cache
		out ={}
		if  use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			out=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:
			#_CONFIG_\\ORACLE.xml
			#IOError: [Errno 22] invalid mode ('rb') or filename: 'C:\\Documents and Settings\x07b95022\\My Documents\\Python27.2.5\\_TabZilla_3\\_CONFIG_\\ORACLE.xml'
			x = '_CONFIG_\\ORACLE.xml' #configFile
			doc = xml.dom.minidom.parse(x)
			
			for node in doc.getElementsByTagName("app_spec"):
			  #isbn = node.getAttribute("isbn")
			  #L = node.getElementsByTagName("title")
			  for node2 in node.childNodes:
				#title = ""
				
				if node2.nodeType != Node.TEXT_NODE:
					#print node2.nodeType, node2.nodeName	
					#if node2.nodeName=='process_spec':
						#print dir(node2.attributes.tems)
						#values=[]
						#for aName, aValue  in node2.attributes.items():
						#	values.append("%s=%s" % (aName, aValue))				
						#_tree.append((node2.nodeName,values))
					if node2.nodeName=='connector':
						#print dir(node2.attributes.tems)
						#values=[]
						i=0
						for node3  in node2.childNodes:
							if node3.nodeType != Node.TEXT_NODE and node3.nodeType != Node.COMMENT_NODE:
								env_type=node3.nodeName.upper()
								for node4  in node3.childNodes:
									if node4.nodeType != Node.TEXT_NODE and node4.nodeType != Node.COMMENT_NODE:
								
										out[i]= ('%s.%s' % (node3.nodeName,node4.nodeName), env_type,node4.attributes.getNamedItem('client_type').value, node4.attributes.getNamedItem('descr').value)
										i +=1
										print i
								#print node3.attributes.keys()
								#values.append("%s=%s@%s" % (node3.nodeName,node3.attributes.getNamedItem('schema').value, node3.attributes.getNamedItem('sid').value))
								#sys.exit(1)
						#_tree.append((node2.nodeName,values))
			#updateCache(cache,out)
		return out
		
	def getConnectList(self,configFile, environment):
		cache= '%s.%s.%s' % (gConnectListCache, os.path.basename(configFile).replace('.','_'),environment)
		#print cache
		out ={}
		if 0 and  use_cache and ifCacheExists(cache):
			
			out=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:
		
			x = '_CONFIG_\\ORACLE.xml' #configFile #'_CONFIG_' #configFile
			doc = xml.dom.minidom.parse(x)
			
			for node in doc.getElementsByTagName("app_spec"):
			  #isbn = node.getAttribute("isbn")
			  #L = node.getElementsByTagName("title")
			  for node2 in node.childNodes:
				#title = ""
				
				if node2.nodeType != Node.TEXT_NODE:
					#print node2.nodeType, node2.nodeName	
					#if node2.nodeName=='process_spec':
						#print dir(node2.attributes.tems)
						#values=[]
						#for aName, aValue  in node2.attributes.items():
						#	values.append("%s=%s" % (aName, aValue))				
						#_tree.append((node2.nodeName,values))
					if node2.nodeName=='connector':
						#print dir(node2.attributes.tems)
						i=0
						for node3  in node2.childNodes:
							if node3.nodeType != Node.TEXT_NODE and node3.nodeType != Node.COMMENT_NODE:
								print node3.nodeName								
								for node4  in node3.childNodes:
									
									if node4.nodeType != Node.TEXT_NODE and node4.nodeType != Node.COMMENT_NODE:
										if environment.upper()=='%s.%s' % (node3.nodeName.upper(),node4.nodeName.upper()):
											for node5  in node4.childNodes:
												if node5.nodeType != Node.TEXT_NODE and node5.nodeType != Node.COMMENT_NODE:										
													#print node4.nodeName
													#pprint (dir(node5.attributes))
													if node5.attributes.getNamedItem('schema'): #db login
														out[i]= (node5.nodeName, 'db_connect', '%s' % (node5.attributes.getNamedItem('schema').value), node5.attributes.getNamedItem('sid').value)
													else:
														if node5.attributes.getNamedItem('user'): #linux login
															print node5.attributes.keys()
															out[i]= (node5.nodeName, 'host_connect', '%s' % (node5.attributes.getNamedItem('user').value), node5.attributes.getNamedItem('host').value, node5.attributes.getNamedItem('home').value)
														else:
															assert 1==2, 'Undefined connect type %s' % node5.nodeName
													i+=1
													print i
								#print node3.attributes.keys()
								#values.append("%s=%s@%s" % (node3.nodeName,node3.attributes.getNamedItem('schema').value, node3.attributes.getNamedItem('sid').value))
								#sys.exit(1)
						#_tree.append((node2.nodeName,values))
			#updateCache(cache,out)
		return out

class FileDir(object):
	"""Worker Thread Class."""
	def __init__(self,pos):
		self.result=None
		self.worker=None
		self.pos=pos
		#Publisher().subscribe(self.onStopFileRequest, "stop_file_request")
		sub(self.onStopFileRequest, "stop_file_request")
	def onStopFileRequest(self, evt):
		print 'aborting db request'
		
		if self.worker:			
			#terminate_thread(self.worker)
			#
			#self.worker.join()
			print self.worker.isAlive()
			if self.worker.isAlive():
				
				print 'it''s alive, aborting...'
				#self.worker.abort()
				#self.worker.terminate()
				terminate_thread(self.worker)
				#Publisher().sendMessage( "filedir_thread_event", ('aborted',self.pos,None, None) )
				send( "filedir_thread_event", ('aborted',self.pos,None, None) )
				#return
		else:
			print 'no worker thread'		
			#Publisher().sendMessage( "db_thread_event", ('done',self.worker.pos,self.worker.cache,self.worker.result) )

	def getRootDirs0(self,connect, path):
		ta={}		
		if 0 and ifCacheExists(gConfigCache):
			print 'getConfigs cache exists',cache
			ta=readFromCache(gConfigCache)
			#print ta
			#sys.exit(1)
		else:	
			#print configDirLoc 
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send( "start_db_progress_gauge", (self.pos) )
			self.worker = RemoteDirThread(self.pos,gDatabaseCache,path, connect)
			self.worker.start()
			#print self.worker.isAlive()

	def getFileDirs(self,connect, path, file_filter):
		ta={}		
		if 0 and ifCacheExists(gConfigCache):
			print 'getConfigs cache exists',cache
			ta=readFromCache(gConfigCache)
			#print ta
			#sys.exit(1)
		else:	
			#print configDirLoc 
			(user,host,pwd)=connect
			print path
			
			if host=='localhost':
				#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
				send("start_db_progress_gauge", (self.pos) )
				
				self.worker = LocalDirThread(self.pos,gDatabaseCache,path, connect,file_filter)
				self.worker.start()
			else:
				print 'host', host
				#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
				send("start_db_progress_gauge", (self.pos) )
				self.worker = RemoteDirThread(self.pos,gDatabaseCache,path, connect,file_filter)
				self.worker.start()			
			#print self.worker.isAlive()
			

		
	def getDatabases(self,login):
		ta={}
		(user,db,pwd,host,port) = login
		cache='%s.%s_%s' % (gDatabaseCache,user,db)
		#print cache
		if use_cache and ifCacheExists(cache):	
			print 'cache exists ',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select v.database,type, TO_CHAR(size,'999,999,999,999.9'),db.createdate FROM
	(select database, 'database' Type, ROUND(sum(used_bytes)/1024/1024,1) size
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	--where objname = 'UPPERCASE_TABLE_NAME'
	group by database) v, _v_database db
	where v.database=db.database order by 1"""
			#Publisher().sendMessage( "show_progress", ((0, 0)) )
			#app.frame.gaugeStart(self.pos)
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send("start_db_progress_gauge", (self.pos) )
			
			#time.sleep(1)

			#wx.Yield()
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			self.worker = DbThread(self.parent,self.pos,gDatabaseCache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()
			#self.worker.join()
			#pprint(dir(self.worker))
			#app.frame.gaugeStop()
			if 0:
				i=0
				for rec in out:
					ta[i]=rec
					i +=1
				#updateCache(cache,ta)

		#return ta
		

	def getOwners(self,login, database='MRR_BI'):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s' % (gOwnersCache,user,db,database)
		if  use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select owner,type, TO_CHAR(size,'999,999,999,999.99') size,u .createdate from 
	(select owner, 'owner' type, ROUND(sum(used_bytes)/1024/1024,1) size
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	where database = '%s'
	group by owner) v, (select username, createdate from _v_user) u
	where v.owner=u.username
	order by 1
	""" % database
			#(db,user) = ('MRR_BI','MRR_ETL_USER')
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send("start_db_progress_gauge", (self.pos))
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,gOwnersCache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()


	def getTables(self,login, location):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s.%s' % (gTableCache,user,db,location[0])
		#print cache
		if use_cache and ifCacheExists(cache):
			
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select objname, 'table' type,TO_CHAR( ROUND(sum(used_bytes)/1024/1024,1),'999,999,999,999.9') size, createdate 
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	where 1=1 and owner='%s'
	group by objname, createdate
	order by 1
	""" % location
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send("start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,cache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()

	def getTableColumns(self,login, location):
		(user,db,pwd,host,port) = login	
		ta={}
		cache='%s.%s_%s.%s_%s' % (gTableColumnsCache,user,db,location[0],location[1])
		if use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""SELECT attname,format_type,attlen,'column',ATTNUM, createdate FROM _V_RELATION_COLUMN_XDB 
				  WHERE owner= '%s' and UPPER(NAME)=UPPER('%s') 
				  ORDER BY ATTNUM ASC;
	""" % location
			#(db,user) = ('MRR_BI','MRR_ETL_USER')
			#Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			send("start_db_progress_gauge", (self.pos))
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.parent,self.pos,cache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()

		
	def getEnvironments(self,configFile):
		print configFile
		cache= '%s.%s' % (gEnvironmentCache, os.path.basename(configFile).replace('.','_'))
		#print cache
		out ={}
		if  use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			out=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:
			
			x = '_CONFIG_\\ORACLE.xml' #configFile #'_CONFIG_' #configFile
			doc = xml.dom.minidom.parse(x)
			
			for node in doc.getElementsByTagName("app_spec"):
			  #isbn = node.getAttribute("isbn")
			  #L = node.getElementsByTagName("title")
			  for node2 in node.childNodes:
				#title = ""
				
				if node2.nodeType != Node.TEXT_NODE:
					#print node2.nodeType, node2.nodeName	
					#if node2.nodeName=='process_spec':
						#print dir(node2.attributes.tems)
						#values=[]
						#for aName, aValue  in node2.attributes.items():
						#	values.append("%s=%s" % (aName, aValue))				
						#_tree.append((node2.nodeName,values))
					if node2.nodeName=='connector':
						#print dir(node2.attributes.tems)
						#values=[]
						i=0
						for node3  in node2.childNodes:
							if node3.nodeType != Node.TEXT_NODE and node3.nodeType != Node.COMMENT_NODE:
								env_type=node3.nodeName.upper()
								for node4  in node3.childNodes:
									if node4.nodeType != Node.TEXT_NODE and node4.nodeType != Node.COMMENT_NODE:
								
										out[i]= ('%s.%s' % (node3.nodeName,node4.nodeName), env_type,node4.attributes.getNamedItem('client_type').value, node4.attributes.getNamedItem('descr').value)
										i +=1
										print i
								#print node3.attributes.keys()
								#values.append("%s=%s@%s" % (node3.nodeName,node3.attributes.getNamedItem('schema').value, node3.attributes.getNamedItem('sid').value))
								#sys.exit(1)
						#_tree.append((node2.nodeName,values))
			#updateCache(cache,out)
		return out
		
	def getConnectList(self,configFile, environment):
		cache= '%s.%s.%s' % (gConnectListCache, os.path.basename(configFile).replace('.','_'),environment)
		#print cache
		out ={}
		if  use_cache and ifCacheExists(cache):
			
			out=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:
		
			x = '_CONFIG_\\ORACLE.xml' #configFile #'_CONFIG_' #configFile
			doc = xml.dom.minidom.parse(x)
			
			for node in doc.getElementsByTagName("app_spec"):
			  #isbn = node.getAttribute("isbn")
			  #L = node.getElementsByTagName("title")
			  for node2 in node.childNodes:
				#title = ""
				
				if node2.nodeType != Node.TEXT_NODE:
					#print node2.nodeType, node2.nodeName	
					#if node2.nodeName=='process_spec':
						#print dir(node2.attributes.tems)
						#values=[]
						#for aName, aValue  in node2.attributes.items():
						#	values.append("%s=%s" % (aName, aValue))				
						#_tree.append((node2.nodeName,values))
					if node2.nodeName=='connector':
						#print dir(node2.attributes.tems)
						i=0
						for node3  in node2.childNodes:
							if node3.nodeType != Node.TEXT_NODE and node3.nodeType != Node.COMMENT_NODE:
								print node3.nodeName								
								for node4  in node3.childNodes:
									
									if node4.nodeType != Node.TEXT_NODE and node4.nodeType != Node.COMMENT_NODE:
										if environment.upper()=='%s.%s' % (node3.nodeName.upper(),node4.nodeName.upper()):
											for node5  in node4.childNodes:
												if node5.nodeType != Node.TEXT_NODE and node5.nodeType != Node.COMMENT_NODE:										
													#print node4.nodeName
													pprint (dir(node5.attributes))
													if node5.attributes.getNamedItem('schema'): #db login
														out[i]= (node5.nodeName, 'db_connect', '%s' % (node5.attributes.getNamedItem('schema').value), node5.attributes.getNamedItem('sid').value)
													else:
														if node5.attributes.getNamedItem('user'): #linux login
															print node5.attributes.keys()
															out[i]= (node5.nodeName, 'host_connect', '%s' % (node5.attributes.getNamedItem('user').value), node5.attributes.getNamedItem('host').value)
														else:
															assert 1==2, 'Undefined connect type %s' % node5.nodeName
													i+=1
													print i
								#print node3.attributes.keys()
								#values.append("%s=%s@%s" % (node3.nodeName,node3.attributes.getNamedItem('schema').value, node3.attributes.getNamedItem('sid').value))
								#sys.exit(1)
						#_tree.append((node2.nodeName,values))
			#updateCache(cache,out)
		return out
		
def sortColumn1(item1, item2):
	try: 
		i1 = int(item1)
		i2 = int(item2)
	except ValueError:
		return cmp(item1, item2)
	else:
		return cmp(i1, i2)
import wx.lib.agw.hyperlink as hl


musicdata = {
1 : ("Bad English", "The Price Of Love", "Rock"),
2 : ("DNA featuring Suzanne Vega", "Tom's Diner", "Rock"),
3 : ("George Michael", "Praying For Time", "Rock"),
4 : ("Gloria Estefan", "Here We Are", "Rock"),
5 : ("Linda Ronstadt", "Don't Know Much", "Rock"),
6 : ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
7 : ("Paul Young", "Oh Girl", "Rock"),
8 : ("Paula Abdul", "Opposites Attract", "Rock"),
9 : ("Richard Marx", "Should've Known Better", "Rock"),
10: ("Rod Stewart", "Forever Young", "Rock"),
11: ("Roxette", "Dangerous", "Rock"),
12: ("Sheena Easton", "The Lover In Me", "Rock"),
13: ("Sinead O'Connor", "Nothing Compares 2 U", "Rock"),
14: ("Stevie B.", "Because I Love You", "Rock"),
15: ("Taylor Dayne", "Love Will Lead You Back", "Rock"),
16: ("The Bangles", "Eternal Flame", "Rock"),
17: ("Wilson Phillips", "Release Me", "Rock"),
18: ("Billy Joel", "Blonde Over Blue", "Rock"),
19: ("Billy Joel", "Famous Last Words", "Rock"),
20: ("Billy Joel", "Lullabye (Goodnight, My Angel)", "Rock"),
21: ("Billy Joel", "The River Of Dreams", "Rock"),
22: ("Billy Joel", "Two Thousand Years", "Rock"),
23: ("Janet Jackson", "Alright", "Rock"),
24: ("Janet Jackson", "Black Cat", "Rock"),
25: ("Janet Jackson", "Come Back To Me", "Rock"),
26: ("Janet Jackson", "Escapade", "Rock"),
27: ("Janet Jackson", "Love Will Never Do (Without You)", "Rock"),
28: ("Janet Jackson", "Miss You Much", "Rock"),
29: ("Janet Jackson", "Rhythm Nation", "Rock"),
30: ("Janet Jackson", "State Of The World", "Rock"),
31: ("Janet Jackson", "The Knowledge", "Rock"),
32: ("Spyro Gyra", "End of Romanticism", "Jazz"),
33: ("Spyro Gyra", "Heliopolis", "Jazz"),
34: ("Spyro Gyra", "Jubilee", "Jazz"),
35: ("Spyro Gyra", "Little Linda", "Jazz"),
36: ("Spyro Gyra", "Morning Dance", "Jazz"),
37: ("Spyro Gyra", "Song for Lorraine", "Jazz"),
38: ("Yes", "Owner Of A Lonely Heart", "Rock"),
39: ("Yes", "Rhythm Of Love", "Rock"),
40: ("Cusco", "Dream Catcher", "New Age"),
41: ("Cusco", "Geronimos Laughter", "New Age"),
42: ("Cusco", "Ghost Dance", "New Age"),
43: ("Blue Man Group", "Drumbone", "New Age"),
44: ("Blue Man Group", "Endless Column", "New Age"),
45: ("Blue Man Group", "Klein Mandelbrot", "New Age"),
46: ("Kenny G", "Silhouette", "Jazz"),
47: ("Sade", "Smooth Operator", "Jazz"),
48: ("David Arkenstone", "Papillon (On The Wings Of The Butterfly)", "New Age"),
49: ("David Arkenstone", "Stepping Stars", "New Age"),
50: ("David Arkenstone", "Carnation Lily Lily Rose", "New Age"),
51: ("David Lanz", "Behind The Waterfall", "New Age"),
52: ("David Lanz", "Cristofori's Dream", "New Age"),
53: ("David Lanz", "Heartsounds", "New Age"),
54: ("David Lanz", "Leaves on the Seine", "New Age"),
}

#---------------------------------------------------------------------------


try:
	from agw import flatmenu as FM
	from agw.artmanager import ArtManager, RendererBase, DCSaver
	from agw.fmresources import ControlFocus, ControlPressed
	from agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.flatmenu as FM
	from wx.lib.agw.artmanager import ArtManager, RendererBase, DCSaver
	from wx.lib.agw.fmresources import ControlFocus, ControlPressed
	from wx.lib.agw.fmresources import FM_OPT_SHOW_CUSTOMIZE, FM_OPT_SHOW_TOOLBAR, FM_OPT_MINIBAR
	
########################################################################
class DragListCtrlPanelManager(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent,frame, pos, panel_pos):
		""""""

		wx.Panel.__init__(self, parent,  id=wx.NewId())

		self.pos=pos
		self.panel_pos=panel_pos

		self.parent=parent
		self.frame=frame
		self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_COLOURFUL_TABS|fnb.FNB_BOTTOM|fnb.FNB_BACKGROUND_GRADIENT|fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_HIDE_ON_SINGLE_TAB ) #|fnb.FNB_DCLICK_CLOSES_TABS|fnb.FNB_X_ON_TAB|fnb.FNB_X|fnb.FNB_TAB_X|fnb.FNB_BACKGROUND_GRADIENT|fnb.FNB_BTN_NONE|fnb.FNB_BTN_PRESSED|fnb.FNB_COLOURFUL_TABS|fnb.FNB_BOTTOM|fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_DROP_DOWN_ARROW|fnb.FNB_BTN_HOVER|fnb.FNB_NO_X_BUTTON) #|fnb.FNB_HIDE_ON_SINGLE_TAB)
		start=DragListCtrlPanel(self,pos,self.panel_pos)
		self.start=start
		self.list=start.list
		self.active_dlcp=start
		self.nb.AddPage(start,'')
		self.nb.SetPageText(0, 'Start')
		self.nb.SetSelection(0)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.nb, 1, wx.GROW|wx.EXPAND|wx.ALL, 0)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.onCloseTab, self.nb)
		#bg = self.nb.GetThemeBackgroundColour()
		#Publisher().subscribe(self.onOpenDesignForm, "open_design_form")
		sub(self.onOpenDesignForm, "open_design_form")
		#open_design_form

		if 1:
			
			MENU_SELECT_GRADIENT_COLOR_FROM = wx.NewId()
			MENU_SELECT_GRADIENT_COLOR_TO = wx.NewId()
			MENU_SELECT_GRADIENT_COLOR_BORDER = wx.NewId()
			MENU_SET_ACTIVE_TEXT_COLOR = wx.NewId()
			MENU_SET_ACTIVE_TAB_COLOR = wx.NewId()
			MENU_SET_TAB_AREA_COLOR = wx.NewId()
			MENU_SELECT_NONACTIVE_TEXT_COLOR = wx.NewId()

			eventid = MENU_SET_TAB_AREA_COLOR
			#data = wx.ColourData()		
			#dlg = wx.ColourDialog(self, data)
			#print 'colour----------------------------',dlg.GetColourData().GetColour()
			red=wx.Colour(255, 0, 0, 255)
			blue=wx.Colour(0, 128, 255, 255)
			green= wx.Colour(0, 128, 0, 255)
			light_yellow=wx.Colour(255, 255, 128, 255)		
			light_green=wx.Colour(128, 255, 128, 255)
			light_blue=wx.Colour(128, 255, 255, 255)
			_TAB_AREA_COLOR=red			
			if pos==(0,0):
				_TAB_AREA_COLOR=light_blue
			elif pos==(0,1):
				_TAB_AREA_COLOR=light_yellow
			elif pos==(0,2):
				_TAB_AREA_COLOR=light_green


			if 1: #dlg.ShowModal() == wx.ID_OK:
				if eventid == MENU_SELECT_GRADIENT_COLOR_BORDER:
					self.nb.SetGradientColourBorder(dlg.GetColourData().GetColour())
				elif eventid == MENU_SELECT_GRADIENT_COLOR_FROM:
					self.nb.SetGradientColourFrom(dlg.GetColourData().GetColour())
				elif eventid == MENU_SELECT_GRADIENT_COLOR_TO:
					self.nb.SetGradientColourTo(dlg.GetColourData().GetColour())
				elif eventid == MENU_SET_ACTIVE_TEXT_COLOR:
					print 'colour----------------------------',dlg.GetColourData().GetColour()
					self.nb.SetActiveTabTextColour(dlg.GetColourData().GetColour())
				elif eventid == MENU_SELECT_NONACTIVE_TEXT_COLOR:
					self.nb.SetNonActiveTabTextColour(dlg.GetColourData().GetColour())
				elif eventid == MENU_SET_ACTIVE_TAB_COLOR:
					self.nb.SetActiveTabColour(dlg.GetColourData().GetColour())
				elif eventid == MENU_SET_TAB_AREA_COLOR:
					#col = dlg.GetColourData().GetColour()
					#print 'colour----------------------------', col, type(col)
					self.nb.SetTabAreaColour(_TAB_AREA_COLOR)
	#@set_name
	def onOpenDesignForm(self, evt):
		(designer_pos, pos_from, pos_to, items_from, form_template)=evt.data	
		if self.pos==designer_pos:
			print  'onOpenDesignForm'
			print pos_from, pos_to, items_from, form_template
			if 0:
				self.msplitter.SetSashPosition(0, 300)
				self.msplitter.SetSashPosition(1, 600)
				self.msplitter.SizeWindows()
	
	def onCloseTab(self, evt):
		print 'onCloseTab'
		try:
			tabid = evt.GetSelection()
		except:
			tabid = self.GetSelection()
		print tabid
		if tabid==0:
			evt.Veto()
	def getVarsToPath(self):
		return self.active_dlcp.getVarsToPath()

class UltListCtrl(ULC.UltimateListCtrl):

	def __init__(self, parent, log):

		ULC.UltimateListCtrl.__init__(self, parent, -1,
									  agwStyle=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|ULC.ULC_SHOW_TOOLTIPS|ULC.ULC_NO_HEADER|ULC.ULC_SINGLE_SEL|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

		self.log = log
		self.InsertColumn(0, 'Time')
		self.InsertColumn(1, 'Message')
		#self.SetColumnWidth(0, 50)
		#self.SetColumnWidth(1, 600)
		self.SetColumnWidth(0, 81)
		
		self.SetColumnWidth(0, ULC.ULC_AUTOSIZE_FILL)
		self.SetColumnWidth(1, ULC.ULC_AUTOSIZE_FILL)
		self.SetColumnToolTip(0,"Timestamp")
		self.SetColumnToolTip(1,"Log Message")
		#self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
	
		if 0:
			#self.listCtrl_t.InsertStringItem(0, '/'.join(spath.split('/')[3:5]))
			self.InsertStringItem(0, 'time')
			#self.listCtrl.InsertStringItem(0, prof)
			self.SetStringItem(0, 1, 'test message')		
		if 0:
			self.il = wx.ImageList(16, 16)
			self.il.Add(images.Smiles.GetBitmap())
			self.il.Add(images.core.GetBitmap())
			self.il.Add(images.custom.GetBitmap())
			self.il.Add(images.exit.GetBitmap())
			self.il.Add(images.expansion.GetBitmap())

			self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

			self.InsertColumn(0, "First")
			self.InsertColumn(1, "Second")
			self.InsertColumn(2, "Third")
			self.SetColumnWidth(0, 175)
			self.SetColumnWidth(1, 175)
			self.SetColumnWidth(2, 175)
			self.SetColumnToolTip(0,"First Column Tooltip!")
			self.SetColumnToolTip(1,"Second Column Tooltip!")
			self.SetColumnToolTip(2,"Third Column Tooltip!")

			# After setting the column width you can specify that 
			# this column expands to fill the window. Only one
			# column may be specified.
			self.SetColumnWidth(2, ULC.ULC_AUTOSIZE_FILL)

			self.SetItemCount(50000)
			
			self.attr1 = ULC.UltimateListItemAttr()
			self.attr1.SetBackgroundColour(wx.NamedColour("yellow"))

			self.attr2 = ULC.UltimateListItemAttr()
			self.attr2.SetBackgroundColour(wx.NamedColour("light blue"))

		#self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

		#self.randomLists = [GenerateRandomList(self.il) for i in xrange(5)]  
	def append(self, msg):

		items=self.GetItemCount()
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		
		if type(msg) == types.ListType:
			self.appendList(items,now,msg)
		else:
			charge=msg.split(r'\n')
			self.appendList(items,now,charge)
		#self.EnsureVisible(items)
		self._mainWin.MoveToItem(self.GetItemCount()-1)
	def appendErr(self, msg):
		items=self.GetItemCount()
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		
		if type(msg) == types.ListType:
			self.appendList(items,now,msg, True)
		else:
			charge=msg.split(r'\n')
			self.appendList(items,now,charge, True)
		#self.EnsureVisible(items)
		self._mainWin.MoveToItem(self.GetItemCount()-1)
	def appendList(self, items,now,charge, if_error=False):
		print 'UltListCtrl.appendList'
		pprint(charge)
		if len(charge)>1:
			for m in charge:
				idx=self.InsertStringItem(items, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				self.SetStringItem(idx, 1, m.strip('\n'))
				if if_error:
					item = self.GetItem(idx,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					pink=wx.Colour(255, 168, 168, 255)
					item.SetBackgroundColour(pink)
					self.SetItem(item)
				items +=1
		else:
			idx=self.InsertStringItem(items, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
			print 'idx=self.InsertStringItem', idx
			msg =charge[0].strip()
			print 'msg =charge[0].strip()', msg
			if msg:
				s=self.SetStringItem(idx, 1, charge[0].strip())
				print 's=self.SetStringItem(idx, 1, charge[0].strip())',s
				if if_error:
					item = self.GetItem(idx,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					pink=wx.Colour(255, 168, 168, 255)
					item.SetBackgroundColour(pink)
					self.SetItem(item)
					
	def appendList_(self, items,now,charge, if_error=False):
		if len(charge)==1 and type(charge)==types.ListType and '\n' in charge[0]:
			charge=charge[0].split('\n')
		pprint(charge)
		
		if len(charge)>1:
			for m in charge:
				self.InsertStringItem(items, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				self.SetStringItem(items, 1, m.strip('\n'))
				if if_error:
					item = self.GetItem(items,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					pink=wx.Colour(255, 168, 168, 255)
					item.SetBackgroundColour(pink)
					self.SetItem(item)
				items +=1
		else:
			self.InsertStringItem(items, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
			msg =charge[0].strip('\n')
			pprint (msg)
			if msg:
				self.SetStringItem(items, 1, msg)
				if if_error:
					item = self.GetItem(items,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					item.SetBackgroundColour('#FAAFBE')
					self.SetItem(item)
			
	def scrollDown(self):
		if self.logList.GetItemCount():
			self.logList._mainWin.MoveToItem(self.logList.GetItemCount()-1)

			
class UltTacoLogger(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent, pos, style=1):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent=parent
		self.pos=pos
		#self.panel_id=panel_id
		#self.parentFrame=parent.frame
		#suffix=''
		#self.label = wx.StaticText(self, -1, 'Started code deployment.')
		#self.label.SetLabel("Hello World!")
		#self.label.SetHelpText('Deployment status.')
		self.log=cu.NullLog()
		self.logList = UltListCtrl(self,self.log)
		#print dir(self.logList)
		if 0:
			for i in range(100):
				self.logList.append('test %d' % i)
		self.sizer.Add(self.logList, 1, wx.GROW|wx.ALL, 1)

		self.SetSizer(self.sizer)
		#self.sizer.Fit(self)
		print self.logList._mainWin
		#Publisher().subscribe(self.OnAppendBLog, "append_browser_log")
		#Publisher().subscribe(self.OnAppendBErr, "append_browser_err")
		sub(self.__OnAppendBLog, "append_browser_log")
		sub(self.__OnAppendBErr, "append_browser_err")
	def Status(self, msg):
		self.label.SetLabel(msg)
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)
	def OnAppendBLog_del(self, evt):
		(msg,pos) = evt.data
		if pos==self.pos:
			self.logList.append(msg)
	def __OnAppendBLog(self, data, extra1, extra2=None):
		print '__OnAppendBLog'
		(msg,pos) = data
		if pos==self.pos:
			self.logList.append(msg)
			
	def OnAppendBErr_del(self, evt):
		(err,pos) = evt.data
		if pos==self.pos:
			self.logList.appendErr(err)		
	def __OnAppendBErr(self, data, extra1, extra2=None):
		print '__OnAppendBErr'
		(err,pos) = data
		if pos==self.pos:
			self.logList.appendErr(err)				
	def _OnExit(self,e):
		#Publisher().sendMessage( "refresh_list", (None) )
		send("refresh_list", (None))
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'

class ClearPasswordsDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size,plist, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False, 
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		self.plist=plist
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		#self.initParams()
		#suffix=''
		#if len(self.data)>1:
		#	suffix='s'
		#label = wx.StaticText(self, -1, "Clear %d password%s." % (len(self.data),suffix))
		#label.SetHelpText('Number of passwords to clear. \nPless "Cancel" button to exit.')
		#mode_btn = wx.Button(self, ID_BUTTON + 3, "Mode(SYNC)")
	
		#mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		#mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		#sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		#box = wx.BoxSizer(wx.HORIZONTAL)

		#label = wx.StaticText(self, -1, "From:",size=(50,-1))
		#label.SetHelpText("Table copy source schema.")
		#box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		#text = wx.TextCtrl(self, -1, self.parent.getVarsToPath()[4:], size=(300,-1))
		#text.Enable(False)
		#text.SetLabel()
		#text.SetHelpText("Table copy SOURCE schema")
		#box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		#sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.tc_tables={}
		self.shards_btn={}

		self.listCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES)
		self.listCtrl.InsertColumn(0, 'Config')		
		self.listCtrl.InsertColumn(1, 'Environment')		
		self.listCtrl.InsertColumn(2, 'Alias')
		self.listCtrl.InsertColumn(3, 'Username')
		self.listCtrl.InsertColumn(4, 'Oracle SID')
		self.listCtrl.SetColumnWidth(0, 80)
		self.listCtrl.SetColumnWidth(1, 90)
		self.listCtrl.SetColumnWidth(2, 160)
		self.listCtrl.SetColumnWidth(3, 110)
		self.listCtrl.SetColumnWidth(4, 110)


		for conf, envs in self.plist.items():
			#conf = self.plist[i]
			
			#box.Add((10,5),0)
			#tname=item[2].strip('[]')
			for env, cons in envs.items():
				for item in cons:
					#print i
					#item=cons[i]
					self.listCtrl.InsertStringItem(0, conf)
					self.listCtrl.SetStringItem(0, 1, env)
					self.listCtrl.SetStringItem(0, 2, item[0])					
					self.listCtrl.SetStringItem(0, 3, item[2])
					self.listCtrl.SetStringItem(0, 4, item[3])

			
		sizer.Add(self.listCtrl, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		btnDelete = wx.Button(self, ID_START, "Clear")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		#ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		button4 = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(btnDelete, 0)
		btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(button4, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnClear, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnTrial, id=ID_TRIAL)
		sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 5)


		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
		self.SetSize((600,400))
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				(config,env)=self.parent.getVarsToPath(self.pos_from).split('/')
				self.parent.deleteConnect('%s.xml' % config,env,row,self.parent.pos)
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
		
	def _initParams(self):		
		if 1:
			(self.pos_from, self.data)=(self.parent.pos, self.parent.delete_conn)
			#print 'init:', self.parent.drag_pos
			#print 'init:', 		self.parent.drop_pos
			#print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def _OnClear(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				print self.parent.getVarsToPath().strip('/').split('/')
				(root,config,env)=self.parent.getVarsToPath().strip('/').split('/')
				print row
				self.parent.frame.clearConnectPassword('%s.xml' % config,env,row,self.parent.pos)
				
		self.status='Delete'
		self.Close(True)
	def OnClear(self,e):
		self.table_to={}
	
		if 0:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				print self.parent.getVarsToPath().strip('/').split('/')
				(root,config,env)=self.parent.getVarsToPath().strip('/').split('/')
				print row
				self.parent.frame.clearConnectPassword('%s.xml' % config,env,row,self.parent.pos)
				
		#self.status='Delete'
		
		for conf, envs in self.plist.items():
			#conf = self.plist[i]
			
			#box.Add((10,5),0)
			#tname=item[2].strip('[]')
			for env, cons in envs.items():
				for item in cons:
					#ORACLE.xml
					#['CSMARTVOL_SMARTS1', 'CSMARTVOL', 'SMARTS1']
					#DEV.oracle
					#item=self.data[i]
					#tname=item[2].strip('[]')				
					#row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
					#self.table_to[row[0]]=row
					#print self.parent.getVarsToPath().strip('/').split('/')
					#(root,config,env)=self.parent.getVarsToPath().strip('/').split('/')
					row =item[:1]+item[2:]
					self.table_to[row[0]]=row
					self.parent.frame.clearConnectPassword('%s.xml' % conf,env,row,self.parent.pos)
					#sys.exit(1)
				blog.log('all passwords cleared for %s/%s' % (conf,env), self.parent.pos)
		self.Close(True)		
			
class DragListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):
	def __init__(self, parent, pos, panel_pos # log
	):
		self.ID=wx.NewId()
		wx.Panel.__init__(self, parent, self.ID, style=wx.WANTS_CHARS)
		#self.SetDoubleBuffered(True)
		global prog
		self.ulocPanel= wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(-1,50))
		#wx.BoxSizer(wx.HORIZONTAL)
		self.url_locator={}
		self.find_in_btn={}
		self.nav_hist=[]
		self.curr_hist_id=0
		self._histMenu=None
		self._favMenu=None
		self._popUpMenu = {}
		(self.row, self.col) =pos
		self.pos=pos
		self.panel_pos=panel_pos
		#print panel_pos
		#sys.exit(1)
		self.sides={'00':'Left','02':'Right'}
		self.status='Welcome to %s!' % prog
		self.count = {}
		self.root_status="ROOT: Double click on ORACLE to zoom into Table level."
		self.hist_btn=OrderedDict()
		#self.log = log		
		#print (type(parent.Parent))
		tID = wx.NewId()
		self.frame=parent.frame
		#Publisher().subscribe(self.onUpdateLocation, "update_location")
		self.listsplit = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
		self.listsplit.SetOrientation(wx.VERTICAL)	
		if 1:
			sizer = wx.BoxSizer(wx.VERTICAL)
			
			if wx.Platform == "__WXMAC__" and \
				   hasattr(wx.GetApp().GetTopWindow(), "LoadDemo"):
				self.useNative = wx.CheckBox(self, -1, "Use native listctrl")
				self.useNative.SetValue( 
					not wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") )
				self.Bind(wx.EVT_CHECKBOX, self.OnUseNative, self.useNative)
				sizer.Add(self.useNative, 0, wx.ALL | wx.ALIGN_RIGHT, 4)
				
			self.il = wx.ImageList(16, 16)

			self.idx1 = self.il.Add(images.Smiles.GetBitmap())
			self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
			self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())

			self.list = DragList(self.listsplit, self, -1,self.pos)
			self.filter =self.getFilter(self,self.list)
			self.filter_history={}
			self.currentItem = 0
		

		if 1:
			self.btnHome = wx.Button(self, -1, "[.]", style=wx.BU_EXACTFIT, size=(30,20))
			self.btnUp = wx.Button(self, -1, "[..]", style=wx.BU_EXACTFIT, size=(30,20))
			

			imageFile = "bmp_source/arrow_back_dgrey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_back=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
			imageFile = "bmp_source/arrow_back_grey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_back.SetBitmapDisabled(image1)
			self.btn_back.Disable()
			imageFile = "bmp_source/arrow_forward_dgrey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_fwd=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
			imageFile = "bmp_source/arrow_forward_grey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_fwd.SetBitmapDisabled(image1)
			self.Bind(wx.EVT_BUTTON, self.OnBackButton, self.btn_back)
			self.btn_back.Bind(wx.EVT_RIGHT_DOWN, self.OnBackButtonRightUp)
			#self.Bind(wx.EVT_RIGHT_UP, self.OnBackButtonRightUp, self.btn_back)
			
			self.Bind(wx.EVT_BUTTON, self.OnForwardButton, self.btn_fwd)
			self.btn_fwd.Bind(wx.EVT_RIGHT_DOWN, self.OnForwardButtonRightUp)
			#self.gen_bind(wx.EVT_BUTTON,self.btn_back, self.OnBackButton,(self.list.current_list))
			#self.gen_bind(wx.EVT_BUTTON,self.btn_fwd, self.OnForwardButton,(self.list.current_list))			
			self.btn_fwd.Disable()
				
			self.btnFav = wx.Button(self, -1, "Fav", style=wx.BU_EXACTFIT, size=(30,20))
			self.btnHist = wx.Button(self, -1, "Hist", style=wx.BU_EXACTFIT, size=(30,20))	
			imageFile = "bmp_source/refresh_icon_16_grey2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_refresh=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
			#self.btn_log = wx.Button(self, -1, "Log", size=(25,20))
			#self.btn_refresh = wx.Button(self, -1, "Refresh", size=(30,20)) 
			#self.sPanel.statusbar.Add([self.gauge[pos],self.btn_stop[pos]], 1, wx.EXPAND,1)
			#self.btn_stop[pos].Hide()
			#self.btn_refresh.SetPosition((1,1))
			self.gen_bind(wx.EVT_BUTTON,self.btn_refresh, self.OnRefreshList,(self.pos))
			#self.btnFwd = wx.Button(self, -1, "Forward", style=wx.BU_EXACTFIT)
			navig = wx.BoxSizer(wx.HORIZONTAL)
			navig.Add(self.btnHome, 0, wx.LEFT)
			navig.Add(self.btnUp, 0, wx.LEFT)
			navig.Add((5,5), 0, wx.LEFT)
			navig.Add(self.btn_back, 0, wx.LEFT)
			navig.Add((2,2), 0, wx.LEFT)
			navig.Add(self.btn_fwd, 0, wx.LEFT)			
			navig.Add((8,8), 0, wx.LEFT)
			#navig.Add(self.locator, 1, wx.LEFT)
			#navig.Add(self.btnFwd, 0, wx.LEFT)
			navig.Add(self.filter, 1, wx.EXPAND)
			
			navig.Add(self.btnHist, 0, wx.LEFT)		
			navig.Add(self.btnFav, 0, wx.LEFT)
			navig.Add(self.btn_refresh, 0, wx.LEFT)
			

			if 1:
				
				self.p_pos=[self.pos]
				#self.statusbar.SetSize((-1, 23))
				#self.statusbar.SetFieldsCount(4)
				#self.SetStatusBar(self.statusbar)        
				#self.statusbar.SetStatusWidths([  250, 120, 140])
				if 0:
					bmp = wx.ArtProvider_GetBitmap(wx.ART_ERROR,
												   wx.ART_TOOLBAR, (16,16))
					
					upbmp = wx.StaticBitmap(self.statusbar, -1, bmp)

					bmp = wx.ArtProvider_GetBitmap(wx.ART_HELP,
												   wx.ART_TOOLBAR, (16,16))
					
					downbmp = wx.StaticBitmap(self.statusbar, -1, bmp)
					btnmio = wx.Button(self.statusbar, -1, "Push Me!")
				
				if 0:
					choice = wx.Choice(self.statusbar, -1, size=(100,-1),
									   choices=['Hello', 'World!', 'What', 'A', 'Beautiful', 'Class!'])
					ticker = Ticker(self.statusbar, -1)
					ticker.SetText("Hello World!")
					ticker.SetBackgroundColour(wx.BLUE)
					ticker.SetForegroundColour(wx.NamedColour("YELLOW"))
					ticker.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False))
					statictext = wx.StaticText(self.statusbar, -1, "Welcome To %s!" % prog)
					
					self.ticker = ticker
				#bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
				#titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)

				self.timer={}
				self.timer_xref={}
				if 1:
					for pos in self.p_pos:
						i=wx.NewId()
						self.timer_xref[i]=pos
						self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
						self.timer[pos]=wx.Timer(self, id=i)
						#lambda event, i=i: self.Screens(event, the_id=i), id=i
						#self.gen_bind(wx.EVT_TIMER,self, self.TimerHandler,(pos))
						
				#items=[]
				#self.sPanel = wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN) # ,size=(300, 30)
				self.statusbar = wx.BoxSizer(wx.HORIZONTAL)
				#self.sPanel.status = wx.BoxSizer(wx.HORIZONTAL)
				gauge={}
				self.gauge=gauge
				#self.gauge=gauge
				for pos in self.p_pos:
					self.gauge[pos] = wx.Gauge(self, -1, size=(-1, 12),	style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
					#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
					#self.gauge[pos].SetPosition((1,1))
					#self.gauge[pos].Hide()	
					#items.append(self.gauge[pos])
				#self.gauge = gauge

				#self.Bind(wx.EVT_TIMER, self.TimerHandler0)
				#self.gen_bind(wx.EVT_TIMER,self, self.TimerHandler_pos,(self.panel_pos[0]))
				btn_stop={}
				self.btn_stop=btn_stop
				#self.btn_stop=btn_stop
				for pos in self.p_pos:
					self.btn_stop[pos] = wx.Button(self, -1, "Stop", size=(30,15)) 
					#self.sPanel.statusbar.Add([self.gauge[pos],self.btn_stop[pos]], 1, wx.EXPAND,1)
					#self.btn_stop[pos].Hide()
					self.btn_stop[pos].SetPosition((self.gauge[pos].GetSize()[0],1))
					self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
					#self.btn_stop[pos].Hide()
					#items.append(self.btn_stop[pos])
				
				#btn_refresh={}
				#self.btn_refresh=btn_refresh
				#self.btn_stop=btn_stop
				#for pos in self.panel_pos:
				if 0:
					imageFile = "bmp_source/refresh_icon_16_grey2.png"
					image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
					self.btn_refresh=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
					self.btn_log = wx.Button(self, -1, "Log", size=(25,20))
					#self.btn_refresh = wx.Button(self, -1, "Refresh", size=(30,20)) 
					#self.sPanel.statusbar.Add([self.gauge[pos],self.btn_stop[pos]], 1, wx.EXPAND,1)
					#self.btn_stop[pos].Hide()
					#self.btn_refresh.SetPosition((1,1))
					self.gen_bind(wx.EVT_BUTTON,self.btn_refresh, self.OnRefreshList,(self.pos))
						#items.append(self.btn_stop[pos])				
									
				#for pos in self.panel_pos:
				#	self.btn_stop[pos].Hide()
				#self.Bind(wx.EVT_IDLE, self.IdleHandler)
				#self.Bind(wx.EVT_CLOSE, self.OnClose)
				#self.Bind(wx.EVT_BUTTON, self.OnStopDbRequest, self.btn_stop)
				#self.fgs = wx.FlexGridSizer(1,3,5,10)
				#self.stt={}
				#for pos in self.panel_pos:
				#self.stt =wx.StaticText(self.sPanel, -1, '%s' % self.status)	
				#self.sPanel.status.Add(self.stt[pos[1]], 0, wx.EXPAND,5)
				#fillin =wx.StaticText(self.sPanel, -1, "test   ")	
				#self.sPanel.status.Add(fillin, 1, wx.EXPAND,5)
				#items.append(self.stt[pos[1]])
				#self.fgs.AddItem(self.stt[pos[1]],pos=(0,0))
				#self.stt.SetPosition((5,2))
				#print self.stt.GetSize()
				if 0:
					self.cb_c = wx.CheckBox(self, wx.ID_ANY, "cache")
					self.Bind(wx.EVT_CHECKBOX, self.OnUseCache, self.cb_c)
					self.cb_c.SetValue(False)
					self.cb_c.Enable(False)
					self.statusbar.Add((10,5))
				#self.spanelbar = wx.BoxSizer(wx.HORIZONTAL)
				#self.spanelbar.Add(self.sPanel, 1, wx.EXPAND,1)
				#self.spanelbar.Add(self.btn_log, 0, wx.RIGHT)
				#self.btn_log.Enable(False)
				#self.spanelbar.Add((30,20), 0, wx.RIGHT)	
				#self.spanelbar.Add(self.cb_c, 0, wx.LEFT|wx.CENTER)
				#self.spanelbar.Add((1,3), 0, wx.RIGHT)	
				#self.spanelbar.Add(self.btn_log, 0, wx.RIGHT)
				#self.spanelbar.Add((5,5), 0, wx.RIGHT)
				#self.spanelbar.Add(self.btn_refresh, 0, wx.RIGHT|wx.CENTER)
				self.statusbar.Add(self.gauge[self.pos], 1,wx.ALL|wx.GROW|wx.EXPAND,1)
				self.statusbar.Add((1,1))
				self.statusbar.Add(self.btn_stop[self.pos], 0,wx.RIGHT,1)
				#self.SetSizer(self.statusbar)
				#self.sPanel.SetSizer(self.sPanel.status)
				#self.fgs.AddMany(items)
				#self.statusbar.Add(self.fgs, 0, wx.ALL,0)
				#print(dir(self.fgs.AddItem))
				#items = [multi_btn,single_btn]
				#self.statusbar.Add(self.sPanel, 0, wx.ALL|wx.VERTICAL,0)

				


			


		#self.PopulateList()

		# Now that the list exists we can init the other base class,
		# see wx/lib/mixins/listctrl.py
		#self.itemDataMap = getConfigs(configDirLoc)
		
		#self.SortListItems(0, True)


		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
		#self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
		#self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
		#self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
		#self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
		#self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
		#self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)

		#self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		#self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

		# for wxMSW
		#self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

		# for wxGTK
		self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
		self.Bind(wx.EVT_BUTTON, self.OnHome, self.btnHome)
		self.Bind(wx.EVT_BUTTON, self.OnUp, self.btnUp)	
		self.gen_bind(wx.EVT_BUTTON,self.btnFav, self.OnFavButton,(self.list.current_list))
		self.gen_bind(wx.EVT_BUTTON,self.btnHist, self.OnHistButton,(self.list.current_list))
		self.Bind(wx.EVT_SET_FOCUS, self.onFocus)  		
		#self.Bind(wx.EVT_BUTTON, self.OnForward, self.btnFwd)	
		self.location=[]
		#Publisher().subscribe(self.onForceSearch, "force_search")	
		#Publisher().subscribe(self.onDbEvent, "db_thread_event")
		#Publisher().subscribe(self.onFileDirEvent, "remotedir_thread_event")
		#Publisher().subscribe(self.onFileDirEvent, "localdir_thread_event")
		sub(self.onForceSearch, "force_search")
		sub(self.__onDbEvent, "db_thread_event")
		sub(self.onFileDirEvent, "remotedir_thread_event")
		sub(self.onFileDirEvent, "localdir_thread_event")
		#Publisher().subscribe(self.onRefreshListEvent, "refresh_list_event")
		self.list.Populate()
		self.itemDataMap=self.list.data[self.list.current_list]
		#listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		#self.RecreateList(None,(self.list,self.filter))
		
		self.no_url_loc=wx.StaticText(self.ulocPanel, -1, self.root_status)
		#self.no_url_loc.SetLabel()
		self.no_url_loc.SetPosition((0,0))		
		if 1:
			if 0:
				from wx.lib.agw import ultimatelistctrl as ULC


				self.url_combo_list = ULC.UltimateListCtrl(self.ulocPanel, wx.ID_ANY, agwStyle=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES|wx.LC_SINGLE_SEL|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

				self.url_combo_list.InsertColumn(0, "Column 1")
				self.url_combo_list.InsertColumn(1, "Column 2")

				index = self.url_combo_list.InsertStringItem(sys.maxint, "Item 1")
				self.url_combo_list.SetStringItem(index, 1, "Sub-item 1")

				index = self.url_combo_list.InsertStringItem(sys.maxint, "Item 2")
				self.url_combo_list.SetStringItem(index, 1, "Sub-item 2")

				choice = wx.Choice(self.url_combo_list, -1, choices=["one", "two"])
				index = self.url_combo_list.InsertStringItem(sys.maxint, "A widget")

				self.url_combo_list.SetItemWindow(index, 1, choice, expand=True,)
			if 0:
				self.cc = wx.combo.ComboCtrl(self, style=wx.combo.CC_BUTTON_OUTSIDE_BORDER, size=(30,-1))
				self.cc.SetPopupExtents(-1,100)
				self.cc.SetPopupMaxHeight(50)
				# Create a Popup
				self.popup = ListCtrlComboPopup()

				# Associate them with each other.  This also triggers the
				# creation of the ListCtrl.
				self.cc.SetPopupControl(self.popup)
				for x in range(75):
					self.popup.AddItem("Item-%02d" % x)

			
			#self.popup.Create(wx.PreListCtrl())
			# Add some items to the listctrl.
			
			if 0:
				self.url_combo_list = wx.ListCtrl(self, -1,  size=(-1,100),
				style=wx.LC_REPORT
							 |wx.BORDER_SUNKEN
							 )
							 
				self.url_combo_list.InsertColumn(0, 'Subject')

				self.url_combo_list.InsertColumn(1, 'Due')

				self.url_combo_list.InsertColumn(2, 'Location', width=125)
				self.url_combo_list.InsertStringItem(0, '1')
				self.url_combo_list.SetStringItem(0, 1, "01/19/2010")
				self.url_combo_list.SetStringItem(0, 2, "USA")


			#self.url_combo_list.Hide()
			#print dir(self.ulocPanel)
			#self.createUrlLocator()
			upsizer = wx.BoxSizer(wx.HORIZONTAL)
			upsizer.Add((5,15), 0, wx.EXPAND)
			upsizer.Add(self.ulocPanel, 1, wx.EXPAND|wx.ALL)
			
			sizer = wx.BoxSizer(wx.VERTICAL)
			#sizer.Add(self.locator, 0, wx.EXPAND)
			sizer.Add((2,2), 0, wx.EXPAND)
			sizer.Add(upsizer, 0, wx.EXPAND)
			sizer.Add((3,3), 0, wx.EXPAND)
			#sizer.Add(self.url_combo_list, 0, wx.EXPAND)
			sizer.Add(navig, 0, wx.EXPAND)
			self.log = UltTacoLogger(self.listsplit,self.pos,self.ID)  #EmptyPanel(self.listsplit)
			(width,height) = wx.DisplaySize()
			#print wx.GetApp().GetSize()
			print (width,height)
			#sys.exit(1)
			self.listsplit.AppendWindow(self.list,height*0.7 )				
			self.listsplit.AppendWindow(self.log)	
			blog.log('Created %s config list' % (self.sides['%d%d' % self.pos]),self.pos)
			#msplitter.AppendWindow(self.panels[(0,2)],200)
			sizer.Add(self.listsplit, 1, wx.EXPAND,4)
			#sizer.Add(self.list, 1, wx.EXPAND,4)
			sizer.Add(self.statusbar, 0,wx.EXPAND)
			
			
			
			if 'wxMac' in wx.PlatformInfo:
				sizer.Add((5,5))  # Make sure there is room for the focus ring
			self.SetSizer(sizer)
			self.SetAutoLayout(True)
			
		#Publisher().subscribe(self.onGaugeStop, "stop_db_progress_gauge")
		#Publisher().subscribe(self.onGaugeStart, "start_db_progress_gauge")
		#Publisher().subscribe(self.onUpdateSbLocUrl, "update_status_bar")
		#Publisher().subscribe(self.onMirrorList, "mirror_list")
		sub(self.__onGaugeStop, "stop_db_progress_gauge")
		#sub(self.onGaugeStart, "start_db_progress_gauge")
		sub(self.__onGaugeStart, "start_db_progress_gauge")
		sub(self.__onUpdateSbLocUrl, "update_status_bar")
		sub(self.onMirrorList, "mirror_list")
		sub(self.__onAdjustDesignLogger, "adjust_design_logger")
	def __onAdjustDesignLogger(self,data, extra1, extra2=None):
		(width,height) = data
		#selected = self.nbe.GetPage(idx)
		self.listsplit.SetSashPosition(0, (height/5)*3)
		self.listsplit.SizeWindows()		
	def onFocus(self, event):
		print 'got Focus'
		#sys.exit(1)
		#event.Skip()
	def getListFromPos(self,pos):
		print self.frame
		return self.frame.getListFromPos(pos)		
	def OnRefreshList(self, event, params):
		( pos) = params
		if pos==self.pos:
			self.status='%s reloaded.' % self.list.current_list 
			self.list.refreshList()
		event.Skip()
		
	def onMirrorList(self, evt):
		(loc_to, path_to,pos_to, side_from) =  evt.data
		if pos_to==self.pos:
			#set list to path
			vars=self.list.getVarsFromPath(path_to,'/')[1:]
			print 'new vars:'
			print vars
			self.list.setNavlist()	
			if len(vars)>2:
				self.list.connect_type=self.list.getConnectType(path_to)
				print self.list.connect_type
				print self.list.nav_list.keys()
				self.list.extendNavlist(self.list.connect_type)
				print self.list.nav_list.keys()
			
			self.list.initVarsFromPath(path_to,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			
			self.list.setCurrListName(loc_to, 'reset')	
			self.status='Mirrored from %s (%s)' % (side_from, path_to)			
			self.list.execList(loc_to)
			#self.status='Mirrored from %s (%s)' % (side_from, path_to)
		#event.Skip()		
	def OnUseCache(self, event):
		print 'use cache', self.pos
		event.Skip()		
	def Status(self, msg):
		pass
		#self.stt.SetLabel(msg)
		
	def OnStopDbRequest(self, event, params):
		( pos) = params
		if pos==self.pos:
			#Publisher().sendMessage( "stop_db_request", (pos) )
			send("stop_db_request", (pos) )
		event.Skip()
	def setUrlLocator(self):
		#print '--setUrlLocator---'
		#self.url_locator={}
		print  self.url_locator
		nav_keys=self.list.nav_list.keys()
		if len(self.url_locator)<len(nav_keys)-1:
			print len(self.url_locator),len(nav_keys)
			self.createUrlLocator()
		
		for loc_id in range(len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if 1 and loc!='vars':
				print 'hiding', loc 
				if self.url_locator.has_key(loc):
					self.url_locator[loc].Hide()
					self.find_in_btn[loc].Hide()
				
		#print  self.list.nav_list.keys()
		#print self.list.loc_url
		offset=0
		prev_loc=None
		print  nav_keys
		print self.list.nav_list['vars'].keys()
		var_keys=self.list.nav_list['vars'].keys()[1:]
		print var_keys
		if not var_keys:
			#self.clearUrlLocator()
			pass
		else:
			for loc_id in range(len(var_keys)): #self.list.loc_url:
				loc=var_keys[loc_id]
				print 'location url',  loc
				if 1 or self.list.nav_list['vars'].has_key(loc):
					if 1 or loc!='vars' and loc_id>0:
						#print '???????',loc , self.list.nav_list['vars'].has_key(loc)
						#print self.list.nav_list['vars']
						#self.url_locator[loc].Show()
						if 0:
							if loc_id>1:
								offset +=self.url_locator[loc].GetSize()[0] +12 #+self.find_in_btn[prev_loc].GetSize()[0]
								#print 'offset', offset
								#print self.url_locator[prev_loc].GetSize()[0]
								#print self.find_in_btn[prev_loc].GetSize()[0]
							else:
								if loc_id==1:
									offset +=self.find_in_btn[loc].GetSize()[0] 
									self.find_in_btn[loc].SetPosition((0,0))
									self.find_in_btn[loc].Show()
						self.find_in_btn[loc].SetPosition((offset,0))
							
						
						offset +=self.find_in_btn[loc].GetSize()[0]		
						if 0:
							if self.list.nav_list['vars'].has_key(loc) :					
								#print '000has key00', loc,self.list.current_list

								
								url_label = self.list.nav_list['vars'][loc]
								self.url_locator[loc].SetLabel(url_label)						
								self.url_locator[loc].SetPosition((offset,0))
								self.url_locator[loc].Show()
								

								offset +=self.url_locator[loc].GetSize()[0]
								self.find_in_btn[loc].Show()

								#self.url_locator[loc].Refresh()
								#if self.list.current_list==loc:
								#	break;
							else:
								pass
						if loc_id==(len(var_keys)-1):
							#self.find_in_btn[loc].SetPosition((0,0))
							#self.find_in_btn[loc].Show()						
							#print '000has key00', loc,self.list.current_list
							
							url_label = self.list.nav_list['vars'][loc]
							print 'last url', loc,self.list.current_list, url_label
							self.no_url_loc.SetLabel(url_label)
							self.no_url_loc.SetPosition((offset,0))
							self.no_url_loc.Show()

							self.find_in_btn[loc].Show()
							break
						else:
							url_label = self.list.nav_list['vars'][loc]
							print 'mid url', loc,self.list.current_list,url_label
							self.url_locator[loc].SetLabel(url_label)						
							self.url_locator[loc].SetPosition((offset,0))
							self.url_locator[loc].Show()
							

							offset +=self.url_locator[loc].GetSize()[0]
							self.find_in_btn[loc].Show()

							#self.url_locator[loc].Refresh()
							#if self.list.current_list==loc:
							#	break;

								
					prev_loc=loc
				
	def setUrlLocator_0(self):
		#print '--setUrlLocator---'
		#self.url_locator={}
		print  self.url_locator
		if not self.url_locator:
			self.createUrlLocator()
		nav_keys=self.list.nav_list.keys()
		for loc_id in range(1,len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if 1 and loc!='vars':
				print 'hiding', loc 
				self.url_locator[loc].Hide()
				self.find_in_btn[loc].Hide()
				
		#print  self.list.nav_list.keys()
		#print self.list.loc_url
		offset=0
		prev_loc=None
		print  nav_keys
		for loc_id in range(len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if 1 or self.list.nav_list['vars'].has_key(loc):
				if loc!='vars' and loc_id>0:
					#print '???????',loc , self.list.nav_list['vars'].has_key(loc)
					#print self.list.nav_list['vars']
					#self.url_locator[loc].Show()
					if 0:
						if loc_id>1:
							offset +=self.url_locator[prev_loc].GetSize()[0] +12 #+self.find_in_btn[prev_loc].GetSize()[0]
							#print 'offset', offset
							#print self.url_locator[prev_loc].GetSize()[0]
							#print self.find_in_btn[prev_loc].GetSize()[0]
						else:
							if loc_id==1:
								offset +=self.find_in_btn[loc].GetSize()[0] 
								self.find_in_btn[loc].SetPosition((0,0))
								self.find_in_btn[loc].Show()
					self.find_in_btn[loc].SetPosition((offset,0))
						
					
					offset +=self.find_in_btn[loc].GetSize()[0]						
					if self.list.nav_list['vars'].has_key(loc) :					
						#print '000has key00', loc,self.list.current_list

						
						url_label = self.list.nav_list['vars'][prev_loc]
						self.url_locator[loc].SetLabel(url_label)						
						self.url_locator[loc].SetPosition((offset,0))
						self.url_locator[loc].Show()
						

						offset +=self.url_locator[loc].GetSize()[0]
						self.find_in_btn[loc].Show()

						#self.url_locator[loc].Refresh()
						#if self.list.current_list==loc:
						#	break;
					else:
						if loc==self.list.current_list:
							#self.find_in_btn[loc].SetPosition((0,0))
							#self.find_in_btn[loc].Show()						
							#print '000has key00', loc,self.list.current_list
							url_label = self.list.nav_list['vars'][prev_loc]
							self.no_url_loc.SetLabel(url_label)
							self.no_url_loc.SetPosition((offset,0))
							self.no_url_loc.Show()
							self.find_in_btn[loc].Show()
							break
						else:
							pass
						#self.url_locator[loc].Hide()

							
				prev_loc=loc

	def clearUrlLocator(self, msg="Retrieving list..."):
		self.no_url_loc.SetLabel(msg)
		self.no_url_loc.SetPosition((0,0))
		if 1:
			for loc in self.url_locator:
				self.url_locator[loc].Destroy()
				self.find_in_btn[loc].Destroy()
		self.url_locator={}
		self.find_in_btn={}
	def createUrlLocator(self):	
		print '--Creating URL locator---'
		
		offset=0


		#self.clearUrlLocator() 
		nav_keys=self.list.nav_list.keys()
		prev_loc=nav_keys[0]
		for loc_id in range(len(nav_keys)-1): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if not self.url_locator.has_key(loc):
				print 'creating url ',loc
				if self.list.nav_list['vars'].has_key(loc):
					url_label = self.list.nav_list['vars'][loc]
				else: 
					url_label=loc
				ul=hl.HyperLinkCtrl(self.ulocPanel, -1, url_label,  URL=loc)
				ul.AutoBrowse(False)
				ul.SetColours("BLUE", "BLUE", "BLUE")
				ul.EnableRollover(True)
				ul.SetUnderlines(False, False, True)
				#ul.SetBold(True)
				ul.OpenInSameWindow(True)
				ul.SetToolTip(wx.ToolTip("Click to explore %s" % url_label))
				ul.UpdateLink()
				#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
				ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
				self.url_locator[loc]=ul
				#create find_in button
				self.find_in_btn[loc] = wx.Button(self.ulocPanel, -1, "/", size=(12,16))
				#self.find_in_btn[loc].Bind(wx.EVT_BUTTON, self.OnFindInButton)
				self.gen_bind(wx.EVT_BUTTON,self.find_in_btn[loc], self.OnFindInButton,(loc_id,loc))
				#self.find_in_btn[loc].Hide()
				self.url_locator[loc].Hide()
				self.find_in_btn[loc].Hide()
			prev_loc=loc
			#else:
			#	print 'passing ',loc
	def createUrlLocator_00(self):	
		print '--Creating URL locator---'
		
		offset=0
		self.no_url_loc=wx.StaticText(self.ulocPanel, -1, '')

		self.clearUrlLocator() 
		nav_keys=self.list.nav_list.keys()
		prev_loc=nav_keys[0]
		for loc_id in range(len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if loc!='vars':
				print 'creating url ',loc
				if self.list.nav_list['vars'].has_key(loc):
					url_label = self.list.nav_list['vars'][loc]
				else: 
					url_label=loc
				ul=hl.HyperLinkCtrl(self.ulocPanel, -1, url_label,  URL=loc)
				ul.AutoBrowse(False)
				ul.SetColours("BLUE", "BLUE", "BLUE")
				ul.EnableRollover(True)
				ul.SetUnderlines(False, False, True)
				#ul.SetBold(True)
				ul.OpenInSameWindow(True)
				ul.SetToolTip(wx.ToolTip("Click to explore %s" % url_label))
				ul.UpdateLink()
				#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
				ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
				self.url_locator[loc]=ul
				#create find_in button
				self.find_in_btn[loc] = wx.Button(self.ulocPanel, -1, "/", size=(12,16))
				#self.find_in_btn[loc].Bind(wx.EVT_BUTTON, self.OnFindInButton)
				self.gen_bind(wx.EVT_BUTTON,self.find_in_btn[loc], self.OnFindInButton,(loc_id,loc))
				self.find_in_btn[loc].Hide()

				prev_loc=loc
			else:
				print 'passing ',loc				
	def OnLink(self, event):
		#ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
		#print dir(event)
		loc=event.GetEventObject().GetURL()
		var=event.GetEventObject().GetLabel()
		
		print 'aaaaaaaaaaaaaaaaaaaaaaa', loc, var
		#list_name='ConfigList'
		self.status=loc
		self.list.clearListVars(loc)
		self.list.setVar(loc, var)
		#print event.GetEventObject().GetLabel()
		#self.list.setCurrListName(loc, 'reset')
		self.list.execNextList(loc)		
		event.Skip()
	def OnFindInButton(self, event,params):
		(loc_id,loc)=params
		print (loc_id,loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		print 'creating PopupMenu((((((((((((', loc
		self.CreatePopupMenu(loc)

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._popUpMenu[loc].SetOwnerHeight(btnSize.y)
		self._popUpMenu[loc].Popup(wx.Point(btnPt.x, btnPt.y), self)		
		if 0:
			self.url_combo_list = ListCtrl2()
			self.url_combo_list.SetPosition((btn.GetPosition()[0],0))
			self.url_combo_list.Show()
			#self.url_combo_list.SetFocus()
			#print dir(self.url_combo_list)
			#self.url_combo_list.SetWindow(self)
			#self.url_combo_list.Focus()
			#print dir(self.url_combo_list)
		if 0:
			self.url_combo_list = wx.ListCtrl(self )
			#self.url_combo_list.Create(wx.PreListCtrl())	 
			self.url_combo_list.InsertColumn(0, 'Subject')

			self.url_combo_list.InsertColumn(1, 'Due')

			self.url_combo_list.InsertColumn(2, 'Location', width=125)
			self.url_combo_list.InsertStringItem(0, '1')
			self.url_combo_list.SetStringItem(0, 1, "01/19/2010")
			self.url_combo_list.SetStringItem(0, 2, "USA")
			#self.url_combo_list.SetPosition((btn.GetPosition()[0],0))

		#event.Skip()
	def CreatePopupMenu(self,loc):

		if 1 or not self._popUpMenu.has_key(loc):
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._popUpMenu[loc] = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			print self.pos
			print loc
			print self.list.data.keys()
			if loc in self.list.data.keys():
				for key, item in self.list.data[loc].items():
					menuItem = FM.FlatMenuItem(pmenu, 20001+key, '%s' % item[0], "", wx.ITEM_RADIO)
					print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if item[0]==self.list.nav_list['vars'][loc]:
						#pprint(dir(menuItem))
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnMenu,(loc,item[0]))
				
			
	def OnMenu(self, event,params):	
		(loc,item) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		item_id=event.GetId()-20001
		print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		print  params
		self.list.nav_list['vars'][loc]=item
		self.list.execList(self.list.current_list)
		self._popUpMenu.pop(loc)
		
	def CreatePopupMenu0(self):

		if not self._popUpMenu:
		
			self._popUpMenu = FM.FlatMenu()
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			subMenu = FM.FlatMenu()
			subSubMenu = FM.FlatMenu()

			# Create the menu items
			menuItem = FM.FlatMenuItem(self._popUpMenu, 20001, "First Menu Item", "", wx.ITEM_CHECK)
			self._popUpMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(self._popUpMenu, 20002, "Sec&ond Menu Item", "", wx.ITEM_CHECK)
			self._popUpMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(self._popUpMenu, wx.ID_ANY, "Checkable-Disabled Item", "", wx.ITEM_CHECK)
			menuItem.Enable(False)
			self._popUpMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(self._popUpMenu, 20003, "Third Menu Item", "", wx.ITEM_CHECK)
			self._popUpMenu.AppendItem(menuItem)

			self._popUpMenu.AppendSeparator()

			# Add sub-menu to main menu
			menuItem = FM.FlatMenuItem(self._popUpMenu, 20004, "Sub-&menu item", "", wx.ITEM_NORMAL, subMenu)
			self._popUpMenu.AppendItem(menuItem)

			# Create the submenu items and add them 
			menuItem = FM.FlatMenuItem(subMenu, 20005, "&Sub-menu Item 1", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)
		
			menuItem = FM.FlatMenuItem(subMenu, 20006, "Su&b-menu Item 2", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subMenu, 20007, "Sub-menu Item 3", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subMenu, 20008, "Sub-menu Item 4", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)

			# Create the submenu items and add them 
			menuItem = FM.FlatMenuItem(subSubMenu, 20009, "Sub-menu Item 1", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)
		
			menuItem = FM.FlatMenuItem(subSubMenu, 20010, "Sub-menu Item 2", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subSubMenu, 20011, "Sub-menu Item 3", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subSubMenu, 20012, "Sub-menu Item 4", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)

			# Add sub-menu to submenu menu
			menuItem = FM.FlatMenuItem(subMenu, 20013, "Sub-menu item", "", wx.ITEM_NORMAL, subSubMenu)
			subMenu.AppendItem(menuItem)			
	def CreateLongPopupMenu(self):

		if hasattr(self, "_longPopUpMenu"):
			return

		self._longPopUpMenu = FM.FlatMenu()
		sub = FM.FlatMenu()
		
		#-----------------------------------------------
		# Flat Menu test
		#-----------------------------------------------
		
		for ii in xrange(30):
			if ii == 0:
				menuItem = FM.FlatMenuItem(self._longPopUpMenu, wx.ID_ANY, "Menu Item #%ld"%(ii+1), "", wx.ITEM_NORMAL, sub)
				self._longPopUpMenu.AppendItem(menuItem)

				for k in xrange(5):

					menuItem = FM.FlatMenuItem(sub, wx.ID_ANY, "Sub Menu Item #%ld"%(k+1))
					sub.AppendItem(menuItem)

			else:

				menuItem = FM.FlatMenuItem(self._longPopUpMenu, wx.ID_ANY, "Menu Item #%ld"%(ii+1))
				self._longPopUpMenu.AppendItem(menuItem)
				
	def OnMouseEvent1(self, event):
		self.url_combo_list.Show()
		#self.url_combo_list.Focus()
		self.url_combo_list.Refresh()
		event.Skip()
		
	def OnItemSelected(self, event):
		##print event.GetItem().GetTextColour()
		self.currentItem = event.m_itemIndex
		#print self.list.GetItemText(self.currentItem)
		msg='%s %s ' % (self.list.current_list[:-4], self.list.GetItemText(self.currentItem).strip('[]'))
		self.Status(msg)		
		#print 'selected'
		#print(self)
		#btns=self.list.nav_list[self.list.current_list]['hot_keys']
		#print btns
		#Publisher().sendMessage( "enable_buttons", (self.pos,btns) )			
		event.Skip()		
		
	def gen_bind(self, type, instance, handler, *args, **kwargs):
		self.Bind(type, lambda event: handler(event, *args, **kwargs), instance)			
	def onGaugeStop_rem(self, evt):
		( pos) = evt.data
		if pos==self.pos:		
			print 'onGaugeStop', pos
			self.gaugeStop(pos)	
			#self.gauge[pos].Hide()
			#self.btn_stop[pos].Hide()
	def __onGaugeStop(self,data, extra1, extra2=None):
		( pos) = data
		if pos==self.pos:		
			print 'onGaugeStop', pos
			self.gaugeStop(pos)	
			#self.gauge[pos].Hide()
			#self.btn_stop[pos].Hide()			
	def onUpdateSbLocUrl(self, evt):
		(loc,pos) = evt.data
		if pos==self.pos:
			#print self.stt
			print loc
			print pos
			#self.stt.SetLabel(loc)
	def __onUpdateSbLocUrl(self,data, extra1, extra2=None):
		(loc,pos) = data
		if pos==self.pos:
			#print self.stt
			print loc
			print pos
			#self.stt.SetLabel(loc)
	def __onGaugeStart(self,data, extra1, extra2=None):
		( pos) = data
		print '=============================onGaugeStart',pos,self.pos
		if pos==self.pos:		
			#self.sPanel.SetSizer(self.sPanel.statusbar)
			print 'onGaugeStart',pos
			self.gaugeStart(pos)
			#self.gauge[pos].Show()
			#self.btn_stop[pos].Show()			
		
	def gaugeStart(self,pos):
		print pos
		print self.gauge
		print  'gaugeStart'
		if pos==self.pos:		
			#self.stt.Hide()
			#self.gauge[pos].Show()
			#self.btn_stop[pos].Show()
			self.timer[pos].Start(100)
			self.count[pos] = 0  
	def gaugeStop(self,pos):
		if pos==self.pos:	
			self.timer[pos].Stop()
			self.count[pos] = 0 
			#self.gauge.Freeze()
			#self.gauge[pos].Hide()
			#self.btn_stop[pos].Hide()
			#self.stt.Show()	
			#tmpitem = self.statusbar.GetChildren()
			#print tmpitem
			#self.statusbar.Replace ( 0, tmpitem[2])
			#self.sPanel.SetSizer(self.sPanel.status)			
	def __del__(self):
		for pos in self.panel_pos:
			self.timer[pos].Stop()
	def TimerHandler0(self, event,the_id):
		#(pos)=params
		pos=self.timer_xref[the_id]
		#print 'the_id', the_id,pos
		self.count[pos] = self.count[pos] + 15

		if self.count[pos] >= 180:
			self.count[pos] = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		
		self.gauge[pos].SetValue(self.count[pos])
		#self.gauge.Pulse()
		
	def TimerHandler_pos(self, event,params):
		(pos)=params
		self.count = self.count + 15

		if self.count >= 180:
			self.count = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		pos=self.panel_pos[0]
		self.gauge[pos].SetValue(self.count)
		#self.gauge.Pulse()
		
	def TimerHandler_(self, event,params):
		(pos)=params
		self.count[pos] = self.count[pos] + 15

		if self.count[pos] >= 180:
			self.count[pos] = 0
		#print self.count
		#self.gauge.Show()
		print '||||||||||||||||| setting count', self.count[pos]
		self.gauge[pos].SetValue(self.count[pos])
		#self.gauge.Pulse()
		
	def onShowProgress(self, evt):
		if 0:
			self.progress_bar.Show()
			self.progress_bar.SetRange(10)
			print 'in ShowProgress'
			self.progress_bar.SetValue(5)
			#print (dir(self.progress_bar))
		self.gauge.Show()
	def OnClose(self, event):

		#self.ticker.Stop()
		self.Destroy()

	def OnSize1(self, event):
		size = self.GetSize()
		print 'Size event'
		#self.splitter.SetSashPosition(size.x / 2)
		#self.sb.SetStatusText(os.getcwd())
		event.Skip()


	def OnDoubleClick(self, event):
		global prog
		size =  self.GetSize()
		self.splitter.SetSashPosition(size.x / 2)

		self.statusbar = ESB.EnhancedStatusBar(self, -1)
		self.statusbar.SetSize((-1, 23))
		self.statusbar.SetFieldsCount(7)
		self.SetStatusBar(self.statusbar)        
		self.statusbar.SetStatusWidths([50, 50, 100, 120, 120, 140, -1])

		bmp = wx.ArtProvider_GetBitmap(wx.ART_ERROR,
									   wx.ART_TOOLBAR, (16,16))
		
		upbmp = wx.StaticBitmap(self.statusbar, -1, bmp)

		bmp = wx.ArtProvider_GetBitmap(wx.ART_HELP,
									   wx.ART_TOOLBAR, (16,16))
		
		downbmp = wx.StaticBitmap(self.statusbar, -1, bmp)
		btnmio = wx.Button(self.statusbar, -1, "Push Me!")
		gauge = wx.Gauge(self.statusbar, -1, 50)
		choice = wx.Choice(self.statusbar, -1, size=(100,-1),
						   choices=['Hello', 'World!', 'What', 'A', 'Beautiful', 'Class!'])
		ticker = Ticker(self.statusbar, -1)
		ticker.SetText("Hello World!")
		ticker.SetBackgroundColour(wx.BLUE)
		ticker.SetForegroundColour(wx.NamedColour("YELLOW"))
		ticker.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False))
		statictext = wx.StaticText(self.statusbar, -1, "Welcome To %s!" % prog)
		
		self.ticker = ticker
		self.gauge = gauge

		self.count = 0        
		
		statusbarchildren = self.statusbar.GetChildren()
		for widget in statusbarchildren:
			self.statusbar.AddWidget(widget)

		self.Bind(wx.EVT_IDLE, self.IdleHandler)
		self.Bind(wx.EVT_CLOSE, self.OnClose)


	def IdleHandler(self, event):
		
		self.count = self.count + 1

		if self.count >= 100:
			self.count = 0

		self.gauge[pos].SetValue(self.count)
		
	def onDbEvent_rem(self, evt):
		print 'onDbEvent'
		(st, pos,cache,result) = evt.data
		print '--onDbEvent', st
		print self.pos,'==',pos
		if st=='done':
			if self.pos==pos:
				print result
				(status, err, rowcount,headers, out) = result
				
				data={}
				i=0
				
				for rec in out:
					data[i]=rec
					i +=1
				#pprint( out) 
				#print 'd'*60
				#print data
				#print self.list.current_list
				self.list.data[self.list.current_list]=data
				self.itemDataMap=self.list.data[self.list.current_list]
				
				self.RecreateList(None,(self.list,self.filter))				
				#self.setListData()
				self.list.Thaw()
				listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		if st=='aborted':
			print '-----------request aborted',self.pos,pos
			if self.pos==pos:
				print 'request aborted',pos
				self.gaugeStop(self.pos)	
				self.list.Thaw()
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)
		self.gaugeStop(self.pos)
	def __onDbEvent(self, data, extra1, extra2=None):
		print 'onDbEvent'
		(st, pos,cache,result) = data
		print '--onDbEvent', st
		print self.pos,'==',pos
		if st=='done':
			if self.pos==pos:
				print result
				(status, err, rowcount,headers, out) = result
				
				data={}
				i=0
				
				for rec in out:
					data[i]=rec
					i +=1
				#pprint( out) 
				#print 'd'*60
				#print data
				#print self.list.current_list
				self.list.data[self.list.current_list]=data
				self.itemDataMap=self.list.data[self.list.current_list]
				
				self.RecreateList(None,(self.list,self.filter))				
				#self.setListData()
				self.list.Thaw()
				listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		if st=='aborted':
			print '-----------request aborted',self.pos,pos
			if self.pos==pos:
				print 'request aborted',pos
				self.gaugeStop(self.pos)	
				self.list.Thaw()
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)
		self.gaugeStop(self.pos)		
	def onFileDirEvent(self, evt):
		print 'onFileDirEvent'
		(st, pos,cache,result) = evt.data
		print '--onFileDirEvent', st
		print self.pos,'==',pos
		if st=='done':
			if self.pos==pos:
				#(status, err, rowcount,headers, out) = result
				
				data=result

				self.list.data[self.list.current_list]=data
				self.itemDataMap=self.list.data[self.list.current_list]
				
				self.RecreateList(None,(self.list,self.filter))				
				#self.setListData()
				self.list.Thaw()
				listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		if st=='aborted':
			print '-----------request aborted',self.pos,pos
			if self.pos==pos:
				print 'request aborted',pos
				self.gaugeStop(self.pos)	
				self.list.Thaw()
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)
		
	def onRefreshListEvent(self, evt):
		print 'onRefreshListEvent'
		(st, pos,cache,result) = evt.data
		print 'onRefreshListEvent', st
		print self.pos,'==',pos
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)		

	def onUpdateLocation(self, evt):
		(position, data)=evt.data
		print '----------------onUpdateLocation', position, self.pos, data
		if position==self.pos:
			(direction, text) = data
			print '----------------onUpdateLocation', direction, text
			#self.filter.SetValue(fltr)	
		#evt.Skip()
	def OnHome(self, event):
		#print 'Clicked OnHome'
		#Publisher().sendMessage( "go_home", (self.pos) )
		send("go_home", (self.pos))
	def OnUp(self, event):
		#print 'Clicked OnBack'
		#Publisher().sendMessage( "go_up", (self.pos) )
		send("go_up", (self.pos))

	def onForceSearch(self, evt):
		(position, fltr)=evt.data
		if position!=self.pos:
			print '----------------onForceSearch', position, fltr
			self.filter.SetValue(fltr)
		

		
	def getFilter(self,parent,list):
		#self.treeMap[ttitle] = {}
		self.searchItems={}
		#print _tP
		#tree = TacoTree(parent,images,_tP)
		filter = wx.SearchCtrl(parent, style=wx.TE_PROCESS_ENTER)
		filter.ShowCancelButton(True)
		#filter.Bind(wx.EVT_TEXT, self.RecreateTree)
		self.gen_bind(wx.EVT_TEXT,filter, self.RecreateList,(list,filter))
		#filter.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnSearchCancelBtn)
		self.gen_bind(wx.EVT_SEARCHCTRL_CANCEL_BTN,filter, self.OnSearchCancelBtn,(list, filter))
		self.gen_bind(wx.EVT_TEXT_ENTER,filter, self.OnSearch,(list, filter))
		searchMenu = wx.Menu()
		item = searchMenu.AppendRadioItem(-1, "Current")
		#self.Bind(wx.EVT_MENU, self.OnSearchMenu, item)
		self.gen_bind(wx.EVT_MENU, item,self.OnSearchMenu,(list, filter))
		item = searchMenu.AppendRadioItem(-1, "Both")
		#self.Bind(wx.EVT_MENU, self.OnSearchMenu, item)
		self.gen_bind(wx.EVT_MENU, item,self.OnSearchMenu,(list, filter))
		filter.SetMenu(searchMenu)		


		#self.RecreateTree(None, (tree, filter,ttitle,_tP,_tL))
		#tree.SetExpansionState(self.expansionState)
		#tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded)
		#self.gen_bind(wx.EVT_TREE_ITEM_EXPANDED, tree, self.OnItemExpanded,(tree))
		#tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
		#self.gen_bind(wx.EVT_TREE_ITEM_COLLAPSED,tree, self.OnItemCollapsed,(tree))
		#tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
		#self.gen_bind(wx.EVT_TREE_SEL_CHANGED, tree,self.OnSelChanged,(tree,filter,ttitle))
		#tree.Bind(wx.EVT_LEFT_DOWN, self.OnTreeLeftDown)
		#self.gen_bind(wx.EVT_LEFT_DOWN, tree,self.OnTreeLeftDown, (ttitle) )
		#self.BuildMenuBar(_tL,ttitle)
		return filter
	def gen_bind(self, type, instance, handler, *args, **kwargs):
		self.Bind(type, lambda event: handler(event, *args, **kwargs), instance)	
	def OnSearchMenu(self, event, tparams):
		(tree, filter)=tparams
		# Catch the search type (name or content)
		searchMenu = filter.GetMenu().GetMenuItems()
		fullSearch = searchMenu[1].IsChecked()
		fltr=filter.GetValue()
		if 1:
			if fullSearch:
				print 'OnSearchMenu/fullSearch'
				#Publisher().sendMessage( "force_search", (self.pos,fltr) )
				send("force_search", (self.pos,fltr) )
				self.OnSearch(None,tparams)
			else:
				self.RecreateList(None,tparams)

		#self.RecreateList(None,tparams)
			
	def OnSearch(self, event, tf):
		#search in every list
		
		(list, filter) = tf
		fltr = filter.GetValue()
		print 'OnSearch',fltr, self.searchItems
		self.filter_history[list.current_list]=fltr
		searchItems=self.searchItems
		if not fltr:
			self.RecreateList(None,(list, filter))
			return

		wx.BeginBusyCursor()		
	
		#searchItems=[item for item in list.data.values() if fltr.lower() in str(item[0]).lower()]
	
		self.RecreateList(None,(list, filter)) 
		wx.EndBusyCursor()
		 

	def OnSearchCancelBtn(self, event,tf):
		(list, filter) = tf
		self.filter.SetValue('')
		self.filter_history[list.current_list]=''
		self.OnSearch(event,tf)
		
	def setPanel(self):
		self.list =self.getTree(self.leftPanel[ttitle],ttitle,_tacoPngs,_treeList,xml_projRootLoc)
		self.filter[ttitle] =self.getFilter(self.leftPanel[ttitle],self.tree[ttitle],ttitle,_tacoPngs,_treeList)
		self.RecreateTree(None, (self.tree[ttitle], self.filter[ttitle],ttitle,_tacoPngs,_treeList,'%s/%s' % (user,db)))
		leftBox = wx.BoxSizer(wx.VERTICAL)
		leftBox.Add(self.tree[ttitle], 1, wx.EXPAND)
		#leftBox.Add(wx.StaticText(leftPanel, label = "Filter Files:"), 0, wx.TOP|wx.LEFT, 5)
		leftBox.Add(self.filter[ttitle], 0, wx.EXPAND|wx.ALL, 5)
		if 'wxMac' in wx.PlatformInfo:
			leftBox.Add((5,5))  # Make sure there is room for the focus ring
		self.leftPanel[ttitle].SetSizer(leftBox)
	def RecreateList(self, evt=None, tf=None):
		# Catch the search type (name or content)
		cl =self.list.current_list
		print '############# in RecreateList', self.pos,'cl:', cl
		(list, filter) = tf
		fltr = filter.GetValue()
		print fltr
		btns=self.list.nav_list[self.list.current_list]['hot_keys']
		#Publisher().sendMessage( "set_buttons", (self.list.pos,btns) )
		if 1:
			searchMenu = filter.GetMenu().GetMenuItems()
			fullSearch = searchMenu[1].IsChecked()
			searchItems=self.searchItems
			if evt:
				if fullSearch:
					print 'RecreateList/fullSearch'
					#Publisher().sendMessage( "force_search", (self.pos,fltr) )
					send("force_search", (self.pos,fltr))
					# Do not`scan all the demo files for every char
					# the user input, use wx.EVT_TEXT_ENTER instead
					#return

			#expansionState = list.GetExpansionState()

			current = None
			#print(dir(list))
			#print list.GetSelectedItemCount()
			if 0:
				item = list.GetSelection()
				if item:
					prnt = list.GetItemParent(item)
					if prnt:
						current = (list.GetItemText(item),
								   list.GetItemText(prnt))
						
			#list.Freeze()
			
			#self.root = list.AddRoot(activeProjName)
			#list.SetItemImage(self.root, 0)
			#list.SetItemPyData(self.root, 0)

			treeFont = list.GetFont()
			catFont = list.GetFont()

			# The old native treectrl on MSW has a bug where it doesn't
			# draw all of the text for an item if the font is larger than
			# the default.  It seems to be clipping the item's label as if
			# it was the size of the same label in the default font.
			if 'wxMSW' not in wx.PlatformInfo or wx.GetApp().GetComCtl32Version() >= 600:
				treeFont.SetPointSize(treeFont.GetPointSize()+2)
				treeFont.SetWeight(wx.BOLD)
				catFont.SetWeight(wx.BOLD)
				
			#list.SetItemFont(self.root, treeFont)
			
			firstChild = None
			selectItem = None
			
			count = 0
			
			#for key, items in list.data.items():
			#items=list.data.values()
			if fltr:
				 self.filter_history[list.current_list]=fltr
				 #print 'fltr', fltr, 'self.filter_history[list.current_list]=', self.filter_history[list.current_list]
			#print list.current_list
			#print self.filter_history
			
			#for item in items:
				#print '------'.join(item)
				#print str(item).replace("L,'"," ").replace(","," ").replace("'","").replace(")","").replace("(","").lower()
				#if fltr.lower() in str(item).lower():
				#	print item 
			#pprint(items)
			#sys.exit(1)
			item_mask='[%s]'
			#print '|||||||||||||||||||||||||||',cl, self.list.nav_list.keys().pop() 
			nav_keys=self.list.nav_list.keys()
			#print nav_keys
			zoomable=[]
			#if nav_keys.index(cl)==len(nav_keys)-2:
			#	item_mask='%s'
			if self.list.nav_list[cl].has_key('zoomable'):
				zoomable=self.list.nav_list[cl]['zoomable']
			if 1:
				count += 1
				if fltr:
					if 0 and fullSearch:
						items = searchItems[category]
					else:
						keys = [key for key,item in list.data[list.current_list].items() if fltr.lower() in str(item[0]).lower()]
				else:
					keys = [key for key,item in list.data[list.current_list].items()]
				print keys
				if keys:
					#print keys
					j=0
					list.DeleteAllItems()
					#load favorites
					fav_path= self.getVarsToFavPath()
					relative_path= self.getVarsToPath()
					print fav_path
					fav_key='%d:%s' % (len(relative_path.split('/')),fav_path)
					#suffix='_favs%d%d' % self.pos
					gsuffix='gfavs%d%d' % self.pos
				
					gfavs=readFromCache('', gsuffix)
					check_favs=False
					favs={}
					if gfavs.has_key(fav_key):
						check_favs=True
						favs=gfavs[fav_key]
					keycolid=list.nav_list[list.current_list]['key_col_id']
					#print favs
					print keycolid
					#sys.exit(1)
					for key in keys:
						#(key,i) = val
						#pprint( list.data)
						#print '?'*60
						i= list.data[list.current_list][key]
						#print key,i
						#sys.exit(1)
						if  1:
							
							if zoomable:
								if i[1] in zoomable:
									index=list.InsertStringItem(sys.maxint, '[%s]' % i[0])
								else:
									index=list.InsertStringItem(sys.maxint,  i[0])
							else:
								index=list.InsertStringItem(sys.maxint, item_mask % i[0])
							for idx in range(1,len(i)):
								list.SetStringItem(index, idx, str(i[idx]))
							#list.SetStringItem(index, 2, str(i[2]))
							#list.SetStringItem(index, 3, str(i[3]))
							#self.SetStringItem(index, 4, str(i[4])) 				#time.strftime('%Y-%m-%d %H:%M', time.localtime(sec))
							

							list.SetItemData(index, key)
							#print favs
							#print favs.reverse()
							#pprint(dir(favs))
							#favs.remove(i[keycolid])
							##print favs
							#print '-------favs index ---------',favs.index(i[keycolid])
							if 0:
								print '@'*40
								print '@'*40
								print i[keycolid],keycolid
								print '@'*40
								print '@'*40
								print fav_key
								pprint(gfavs)
							login_schema= relative_path.split('/')[-1].split('_')[0]
							
							if favs.has_key(i[keycolid]) or login_schema==i[keycolid]:
								item = list.GetItem(index)
								font = item.GetFont()
								font.SetWeight(wx.FONTWEIGHT_BOLD)
								item.SetFont(font)
								# This does the trick:
								list.SetItem(item)
							

							#if i[1] == 'xml':
							#print list._imgstart,list.img_offset
							imgs= self.list.nav_list[cl]['img'] 
							img_type_col_id= self.list.img_col
							img_type = i[img_type_col_id]
							img_name=None
							if imgs.has_key(img_type):
								img_name=imgs[img_type]
							else:
								img_name=imgs['default']
							#print img_name
							img_id=self.list.image_refs[img_name]
							list.img[key]=img_id
							list.SetItemImage(index, list.img[key])
							#print 'SetItemImage',index,key,list.img[key]
							if (j % 2) == 0:
								list._bg='#e6f1f5'
								list.SetItemBackgroundColour(index, list._bg)
							j += 1				
					if 0:
						child = list.AppendItem(self.root, category, image=count)
						list.SetItemFont(child, catFont)
						list.SetItemPyData(child, count)
						if not firstChild: firstChild = child
						for childItem in items:
							image = count
							if DoesModifiedExist(childItem):
								image = len(_tP)
							theDemo = list.AppendItem(child, childItem, image=image)
							list.SetItemPyData(theDemo, count)
							self.treeMap[ttitle][childItem] = theDemo
							#if current and (childItem, category) == current:
							#	selectItem = theDemo
							
						
			#list.Expand(self.root)
			#if firstChild:
			#	list.Expand(firstChild)
			#if fltr:
			#	list.ExpandAll()
			#elif expansionState:
			#	list.SetExpansionState(expansionState)
			if 0 and selectItem:
				self.skipLoad = True
				list.SelectItem(selectItem)
				self.skipLoad = False
			print 'list.Thaw()'
			#print (dir(list))
			print list.pos
			#if list.IsFrozen():
			#	list.Thaw()
			#list.Show()
			searchItems = {}		
			listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
			#update location url
			#print '/'.join([l[:-4] for l in self.list.loc_url])
			out=''
			max_len=15
			dots=''
			nav_var_keys=self.list.nav_list['vars'].keys()[1:]
			for vloc in nav_var_keys:
				out =out +'/'				
				if 1:
					url_val=self.list.nav_list['vars'][vloc]
					if 0 and len(out)>30:
						if len(url_val)>max_len:
							dots='..'
						out =out+ url_val[:max_len] +dots #+' '+str(len(self.list.nav_list['vars'][l]))
						dots=''
					else:
						out =out+ url_val
				else:
					out =out+l[:-4]


			if not out:
				out =self.root_status
				#sys.exit(1)
			
			#print '#'*20
			#print out
			#print '#'*20			
			#pprint(self.hist_btn)
			#pprint(self.hist_btn.keys())
			#print(dir(self.locator))
			#self.locator.SetLabel(out)
			self.setUrlLocator()
			sb=self.status
			if not sb:
				sb=cl
				if not sb:
					sb='Douple click on pipeline file.'
			#Publisher().sendMessage( "update_status_bar", (sb,self.pos) ) 
			send( "update_status_bar", (sb,self.pos))
			#pub.sendMessage("update_status_bar", data=(sb,self.pos))	
			
			#self.updateCache()
	def add_nav_hist(self,  loc,path=None):
		#Usage:
		#self.add_nav_hist(self.getVarsToPath(),self.current_list)
		#always cut at current_hist_id
		if not path:
			path=self.getVarsToPath()
		#hist_id='%s:%s' % (loc,path)
		#if self.nav_hist.has_key(path):
		#	self.nav_hist.pop(path)
		self.nav_hist=self.nav_hist[:self.curr_hist_id+1]
		self.nav_hist.append((loc,path))
		print 'in add_nav_hist000000000000000', self.curr_hist_id, len(self.nav_hist)
		self.curr_hist_id=len(self.nav_hist)-1
		#pprint(self.nav_hist)
		#self.nav_hist[path]=loc
		if self.curr_hist_id>0:
			self.btn_back.Enable()
		self.btn_fwd.Disable()
		#print 'in add_nav_hist000000000000000', self.curr_hist_id
		
	def OnBackButton(self, event):
		#assuming self.curr_hist_id>0
		(loc_to,path_to)=self.nav_hist[self.curr_hist_id-1]
		self.curr_hist_id -=1
		print (loc_to,path_to)
		self.list.initVarsFromPath(path_to,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		print 'self.curr_hist_id', self.curr_hist_id
		if self.curr_hist_id==0:
			self.btn_back.Disable()
		self.btn_fwd.Enable()	
		
		if 0:
			idx=self.nav_hist.keys().index(relative_path)
			print relative_path,idx
			path_to=self.nav_hist.keys()[idx-1]
			loc_to=self.nav_hist[path_to]
			
			print (loc_to,path_to)
			self.list.initVarsFromPath(path_to,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			self.list.setCurrListName(loc_to, 'reset')		
			self.list.execList(loc_to)
			if idx==1:
				self.btn_back.Disable()
			self.btn_fwd.Enable()

	def OnBackButtonRightUp(self, event):
		print self.pos
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		print btn
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateBackMenu()

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._backMenu.SetOwnerHeight(btnSize.y)
		self._backMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)	
	def CreateBackMenu(self):

		if 1:
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._backMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			#(path, loc_to) = self.nav_hist[self.curr_hist_id]
			#relative_path=self.getVarsToPath()
			for id in range(len(self.nav_hist)):
				if id<self.curr_hist_id:
					tup=self.nav_hist[id]
					(loc_to, path)=tup
					#loc_to=self.hist_btn[path]
					itype=wx.ITEM_NORMAL
					if id==self.curr_hist_id:
						itype=wx.ITEM_CHECK
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
					#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if id==self.curr_hist_id:
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnBackMenu,(id,loc_to,path))		
	def OnBackMenu(self, event, params):
		(id,loc_to,path) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		#item_id=event.GetId()-21001
		#print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		#print  params
		#self.list.nav_list['vars'][loc]=item
		#list_to=
		print (loc_to,path)
		self.curr_hist_id=id
		self.list.initVarsFromPath(path,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		#self._popUpMenu.pop(loc)
		self.btn_fwd.Enable()	
		if self.curr_hist_id==0:
			self.btn_back.Disable()		
	def OnForwardButtonRightUp(self, event):
		print self.pos
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		print btn
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateForwardMenu()

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._fwdMenu.SetOwnerHeight(btnSize.y)
		self._fwdMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)		
	def CreateForwardMenu(self):

		if 1:
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._fwdMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			#(path, loc_to) = self.nav_hist[self.curr_hist_id]
			relative_path=self.getVarsToPath()
			for id in range(len(self.nav_hist)):
				if id>self.curr_hist_id:
					print id, self.curr_hist_id
					tup=self.nav_hist[id]
					(loc_to, path)=tup
					print id, self.curr_hist_id
					itype=wx.ITEM_NORMAL
					if id==self.curr_hist_id:

						itype=wx.ITEM_CHECK
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
					#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if path==relative_path:
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnForwardMenu,(id,loc_to, path))
	def OnForwardMenu(self, event, params):
		(id,loc_to, path) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		#item_id=event.GetId()-21001
		#print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		#print  params
		#self.list.nav_list['vars'][loc]=item
		#list_to=
		self.curr_hist_id=id
		print (loc_to,path)
		self.list.initVarsFromPath(path,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		#self._popUpMenu.pop(loc)
		self.btn_back.Enable()	
		if self.curr_hist_id==(len(self.nav_hist)-1):
			self.btn_fwd.Disable()
	def OnForwardButton(self, event):
		#assuming it's not the end of the list	
		(loc_to,path_to)=self.nav_hist[self.curr_hist_id+1]
		self.curr_hist_id +=1
		print (loc_to,path_to)
	
		self.list.initVarsFromPath(path_to,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		self.btn_back.Enable()	
		if self.curr_hist_id==len(self.nav_hist)-1:
			self.btn_fwd.Disable()
			
		if 0:
			relative_path=self.getVarsToPath()
			idx=self.nav_hist.keys().index(relative_path)
			print relative_path,idx
			path_to=self.nav_hist.keys()[idx+1]
			loc_to=self.nav_hist[path_to]
			self.list.initVarsFromPath(path_to,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			self.list.setCurrListName(loc_to, 'reset')		
			self.list.execList(loc_to)
			self.btn_back.Enable()	
			if idx+1==self.nav_hist-1:
				self.btn_fwd.Disable()
				
	def add_hist(self,  loc,path=None):
		if not path:
			path=self.getVarsToPath()	
		#if self.hist_btn.has_key(path):
		#	self.hist_btn.pop(path)
		self.hist_btn[path] = loc
	def OnHistButton(self, event,params):
		(loc)=params
		print (loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateHistMenu(loc)

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._histMenu.SetOwnerHeight(btnSize.y)
		self._histMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)		
	def OnFavButton(self, event,params):
		(loc)=params
		print (loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateFavMenu(loc)

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._favMenu.SetOwnerHeight(btnSize.y)
		self._favMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)	
	def CreateHistMenu(self,loc):

		if 1 or not self._popUpMenu.has_key(loc):
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._histMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			relative_path=self.getVarsToPath()
			for id in range(len(self.hist_btn)):
				path=self.hist_btn.keys()[id]
				loc_to=self.hist_btn[path]
				
				itype=wx.ITEM_NORMAL
				#print '>>>>>>>>>>>>>>',relative_path,path
				if relative_path==path:
					itype=wx.ITEM_CHECK
				menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
				#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
				pmenu.AppendItem(menuItem)				
				if relative_path==path:
					menuItem.Check(True)
					#subMenu.UpdateItem(menuItem)
					#print menuItem.IsChecked(), menuItem.IsCheckable()
					#menuItem.Enable(False)
				#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

				#print menuItem.isChecked()
				#print menuItem.IsChecked(), menuItem.IsChecked()
				#menuItem.Enable(True)
				#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
				#
				self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnHistMenu,(loc_to,path))
	def CreateFavMenu(self,loc):

		if 1 or not self._popUpMenu.has_key(loc):
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._favMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			gsuffix='gfavs%d%d' % self.pos
			gfavs=readFromCache('', gsuffix)	
			print 'gfavs:', gfavs
			gkeys=gfavs.keys()
			#gkeys=sorted(gkeys,key=lambda path: len(path.split('/'))) #reverse=True
			gkeys.sort()
			pprint(gkeys)
			#sys.exit(1)
			first=True
			for path in gkeys:	
				items=gfavs[path]
				if not first:
					pmenu.AppendSeparator()
				loc_id=p=path.split(':')[0]
				#loc=self.list.getListFromId(int(loc_id))
				p=path.split(':')[1][5:]
				if p:
					p='(%s)' %p
				ikeys=items.keys()
				ikeys.sort()
				for ikey in ikeys:
					val=items[ikey]
					print '--item--',ikey, val
					itype=wx.ITEM_NORMAL
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s %s' % (ikey, p), "", itype)
					pmenu.AppendItem(menuItem)
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnFavMenu,(loc_id,'%s/%s' %(val,ikey)))
				first=False
			if 0:
				for id in range(len(self.hist_btn)):
					path=self.hist_btn.keys()[id]
					loc_to=self.hist_btn[path]
					itype=wx.ITEM_NORMAL
					if id==(len(self.hist_btn)-1):
						itype=wx.ITEM_CHECK
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
					#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if id==(len(self.hist_btn)-1):
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnHistMenu,(loc_to,path))
	def OnHistMenu(self, event, params):
		(loc_to,path) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		#item_id=event.GetId()-21001
		#print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		#print  params
		#self.list.nav_list['vars'][loc]=item
		#list_to=
		print (loc_to,path)
		vars=self.list.getVarsFromPath(path,'/')[1:]
		self.list.setNavlist()
		if len(vars)>2:
			conn=self.list.getConnectType(path)
			print conn
			print 'before',self.list.nav_list.keys()
			self.list.extendNavlist(conn)
			print 'after',self.list.nav_list.keys()
				
		self.list.initVarsFromPath(path,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		self.add_nav_hist(loc_to)
		#self._popUpMenu.pop(loc)	
	def OnFavMenu0(self, event, params):
		(loc_to,path) = params
		#print params
		if 1:
			#print event.GetEventObject()
			#print(dir(event.GetEventObject()))
			#item_id=event.GetId()-21001
			#print item_id
			#self.list.nav_list['vars'][loc]=
			#print self.list., self.list.data[loc][item_id]
			#print  params
			#self.list.nav_list['vars'][loc]=item
			#list_to=
			print (loc_to,path)
			self.list.initVarsFromPath(path,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			self.list.setCurrListName(loc_to, 'reset')		
			self.list.execList(loc_to)
			self.add_nav_hist(loc_to)
		#self._popUpMenu.pop(loc)	
	def OnFavMenu(self, event, params):
		(loc_id,path) = params
		#print params
		if 1:
			#print event.GetEventObject()
			#print(dir(event.GetEventObject()))
			#item_id=event.GetId()-21001
			#print item_id
			#self.list.nav_list['vars'][loc]=
			#print self.list., self.list.data[loc][item_id]
			#print  params
			#self.list.nav_list['vars'][loc]=item
			#list_to=
			print (loc_id,path)
			vars=self.list.getVarsFromPath(path,'/')[1:]
			print 'new vars:'
			print vars
			#init list
			self.list.setNavlist()
			if len(vars)>2:
				conn=self.list.getConnectType(path)
				print conn
				print 'before',self.list.nav_list.keys()
				self.list.extendNavlist(conn)
				print 'after',self.list.nav_list.keys()
				#sys.exit(1)
			self.list.initVarsFromPath(path,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			loc_to=self.list.getListFromId(int(loc_id))
			self.list.setCurrListName(loc_to, 'reset')	
			print loc_to, loc_id
			print self.list.nav_list.keys()	
			print vars
			#sys.exit(1)
			self.list.execList(loc_to)
			self.add_nav_hist(loc_to)
		#self._popUpMenu.pop(loc)		
	def updateCache(self):
		relative_path='root'
		if update_cache:
			
			vars=self.list.nav_list['vars'].values()[1:]
			if len(vars)>0:
				relative_path='%s/%s'% (relative_path,'/'.join(vars))
				#print '#'*20,  
				#os.path.join(self.list.nav_list['vars'].values()[1:])
			#else:
			#	relative_path='%s/root' % relative_path
			writeToCache(relative_path, self.list.data[self.list.current_list])	
	#def updateCache(self)
	def SortListItems(self, col=-1, ascending=1):
		pass
	def GetSelection(self):
		row = -1 
		selected_items = [] 
		while 1: 
			row = self.GetNextItem(row, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED) 
			if row==-1: break 
		selected_items.append(row) 
	def OnUseNative(self, event):
		wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", not event.IsChecked())
		wx.GetApp().GetTopWindow().LoadDemo("ListCtrl")

	def PopulateList(self):
		if 0:
			# for normal, simple columns, you can add them like this:
			self.list.InsertColumn(0, "Artist")
			self.list.InsertColumn(1, "Title", wx.LIST_FORMAT_RIGHT)
			self.list.InsertColumn(2, "Genre")
		else:
			# but since we want images on the column header we have to do it the hard way:
			info = wx.ListItem()
			info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.m_image = -1
			info.m_format = 0
			info.m_text = "Artist"
			self.list.InsertColumnInfo(0, info)

			info.m_format = wx.LIST_FORMAT_RIGHT
			info.m_text = "Title"
			self.list.InsertColumnInfo(1, info)

			info.m_format = 0
			info.m_text = "Genre"
			self.list.InsertColumnInfo(2, info)

		items = musicdata.items()
		for key, data in items:
			index = self.list.InsertImageStringItem(sys.maxint, data[0], self.idx1)
			self.list.SetStringItem(index, 1, data[1])
			self.list.SetStringItem(index, 2, data[2])
			self.list.SetItemData(index, key)

		self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(2, 100)

		# show how to select an item
		#self.list.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

		# show how to change the colour of a couple items
		item = self.list.GetItem(1)
		item.SetTextColour(wx.BLUE)
		self.list.SetItem(item)
		item = self.list.GetItem(4)
		item.SetTextColour(wx.RED)
		self.list.SetItem(item)

		self.currentItem = 0


	# Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
	def GetListCtrl(self):
		return self.list

	# Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)


	def OnRightDown(self, event):
		x = event.GetX()
		y = event.GetY()
		#self.log.WriteText("x, y = %s\n" % str((x, y)))
		item, flags = self.list.HitTest((x, y))

		if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
			self.list.Select(item)

		event.Skip()


	def getColumnText(self, index, col):
		item = self.list.GetItem(index, col)
		return item.GetText()

		

	def OnItemSelected1(self, event):
		##print event.GetItem().GetTextColour()
		self.currentItem = event.m_itemIndex
		if 0:
			self.log.WriteText("OnItemSelected: %s, %s, %s, %s\n" %
							   (self.currentItem,
								self.list.GetItemText(self.currentItem),
								self.getColumnText(self.currentItem, 1),
								self.getColumnText(self.currentItem, 2)))

		if self.currentItem == 10:
			#self.log.WriteText("OnItemSelected: Veto'd selection\n")
			#event.Veto()  # doesn't work
			# this does
			self.list.SetItemState(10, 0, wx.LIST_STATE_SELECTED)

		event.Skip()


	def OnItemDeselected1(self, evt):
		item = evt.GetItem()
		print "OnItemDeselected: %d" % evt.m_itemIndex
		#self.log.WriteText("OnItemDeselected: %d" % evt.m_itemIndex)

		# Show how to reselect something we don't want deselected
		if evt.m_itemIndex == 11:
			wx.CallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
		#print "OnItemActivated: %s\nTopItem: %s" % (self.list.GetItemText(self.currentItem), self.list.GetTopItem())
		#self.log.WriteText("OnItemActivated: %s\nTopItem: %s" %
		#                   (self.list.GetItemText(self.currentItem), self.list.GetTopItem()))

	def OnBeginEdit(self, event):
		print "OnBeginEdit"
		#self.log.WriteText("OnBeginEdit")
		event.Allow()

	def OnItemDelete(self, event):
		print "OnItemDelete\n"
		#self.log.WriteText("OnItemDelete\n")

	def OnColClick(self, event):
		print "OnColClick: %d\n" % event.GetColumn()
		#self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
		#print(dir(self.list))
		#if self.list.idx_first != None:
		#	self.list.DeleteItem(self.list.idx_first)

		event.Skip()
	def OnSortOrderChanged(self):
		#print "OnSortOrderChanged!"
		#self._colSortFlag[self._col]=int(not self._colSortFlag[self._col])
		#pprint(dir(self.list))
		if 1:
			for j in range(len(self.list.data[self.list.current_list])):
				if (j % 2) == 0:
					#self.list._bg='#e6f1f5'
					self.list.SetItemBackgroundColour(j, self.list._bg)
				else:
					self.list.SetItemBackgroundColour(j, '#FFFFFF')
				#j += 1
				
		#self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
		#event.Skip()		

	def OnColRightClick(self, event):
		item = self.list.GetColumn(event.GetColumn())
		print "OnColRightClick: %d %s\n" % (event.GetColumn(), (item.GetText(), item.GetAlign(), item.GetWidth(), item.GetImage()))
		#self.log.WriteText("OnColRightClick: %d %s\n" %
		#                   (event.GetColumn(), (item.GetText(), item.GetAlign(),
		#                                        item.GetWidth(), item.GetImage())))

	def OnColBeginDrag(self, event):
		print "OnColBeginDrag\n"
		#self.log.WriteText("OnColBeginDrag\n")
		## Show how to not allow a column to be resized
		#if event.GetColumn() == 0:
		#    event.Veto()


	def OnColDragging(self, event):
		print "OnColDragging\n"
		#self.log.WriteText("OnColDragging\n")

	def OnColEndDrag(self, event):
		print "OnColEndDrag\n"
		#self.log.WriteText("OnColEndDrag\n")

	def OnDoubleClick(self, event):
		print "OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem)
		#self.log.WriteText("OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem))
		event.Skip()
	def getSide(self,pos):
		side =None
		id ='%d%d' % pos 
		if self.sides.has_key(id):
			side=self.sides[id]
		return side
	def OnRightClick(self, event):
		print "OnRightClick %s\n" % self.list.GetItemText(self.currentItem),self.list.GetSelectedItemCount()
		#self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))
		#print(dir(self.list))
		#print GetSelectedItemCount
		# only do this part the first time so the events are only bound once
		disabled_favs=False
		if self.list.GetSelectedItemCount()==0:
			disabled_favs =True
		self.show_in={}
		if 1:
			menu = wx.Menu()
			if 1: #not hasattr(self, "add_to_favorites"):
				self.add_to_favorites = wx.NewId()
				self.remove_from_favorites = wx.NewId()
				for sid in ['%d%d' % pos for pos in self.panel_pos if pos!=self.pos ]:
					print '---ii--',sid, 20100+int(sid)
					self.show_in[sid]=20100+int(sid)
				self.Bind(wx.EVT_MENU, self.OnAddToFavorites, id=self.add_to_favorites)
				self.Bind(wx.EVT_MENU, self.OnRemoveFromFavorites, id=self.remove_from_favorites)
				for sid in ['%d%d' % pos for pos in self.panel_pos if pos!=self.pos ]:
					#self.gen_bind(wx.EVT_MENU,self, self.TimerHandler_pos,(self.panel_pos[0]))
					#self.gen_bind(wx.EVT_MENU,menu, self.OnShowIn,(sid),id=self.show_in[sid])
					self.Bind(wx.EVT_MENU, self.OnShowIn, id=self.show_in[sid])
					self.Bind(wx.EVT_MENU, self.OnShowIn, id=self.show_in[sid]+10000)
					#self.Bind(wx.EVT_MENU, self.OnShowIn, id=self.show_in[sid])
					#menuItem = wx.MenuItem(pmenu, wx.ID_ANY, '%s' % ( label), "", itype)
					#self.gen_bind(wx.EVT_MENU,self.show_in[sid], self.OnShowIn ,(id))	
				if 0:
					self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
					self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
					self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
					self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
					self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

			# make a menu
			
			# add some items
			self.add_new_connect = wx.NewId()
			self.delete_connect = wx.NewId()
			self.edit_connect = wx.NewId()
			self.clear_password = wx.NewId()
			if self.list.current_list in ('ConnectList'):
				menu.Append(self.add_new_connect, "Add new connection.")
				self.Bind(wx.EVT_MENU, self.OnAddNewConnection, id=self.add_new_connect)
				menu.Append(self.delete_connect, "Delete connection.")
				self.Bind(wx.EVT_MENU, self.OnDeleteConnection, id=self.delete_connect)
				menu.Append(self.edit_connect, "Edit connection.")
				self.Bind(wx.EVT_MENU, self.OnEditConnection, id=self.edit_connect)
				if disabled_favs:
					menu.Enable(self.delete_connect, False)
				
				menu.Append(self.clear_password, "Clear Password")
				self.Bind(wx.EVT_MENU, self.OnClearPassword, id=self.clear_password)
				if disabled_favs:
					menu.Enable(self.clear_password, False)	
			if self.list.current_list in ('ConfigList','EnvironmentList'):
				menu.Append(self.clear_password, "Clear Passwords")
				self.Bind(wx.EVT_MENU, self.OnClearPasswords, id=self.clear_password)
				if disabled_favs:
					menu.Enable(self.clear_password, False)	
					
					
			menu.Append(self.add_to_favorites, "Add to Favorites.")
			menu.Append(self.remove_from_favorites, "Remove from Favorites.")
			if self.list.current_list in ('TableList','PartitionList','SubPartitionList'):
				gather_stats=wx.NewId()
				menu.Append(gather_stats, "Gather stats.")
				menu.Enable(gather_stats, False)
				copy_ddl=wx.NewId()
				menu.Append(copy_ddl, "Copy DDL.")
				menu.Enable(copy_ddl, False)
				copy_name=wx.NewId()
				menu.Append(copy_name, "Copy name.")
				menu.Enable(copy_name, False)
				
			for pos in [ pos for pos in self.panel_pos if pos!=self.pos and pos !=self.frame.designer_pos ]:
				side= self.getSide(pos)
				sid= '%d%d' % pos 
				print sid, side, self.panel_pos
				if side:
					menu.Append(self.show_in[sid], "Mirror in %s" % side)
					list=self.getListFromPos(pos)
					pos_connect='test_CSMARTBSER_QA' #'list.parent.getVarsToPath().split('/')[2]
					#db_path=self.getVarsToPath().split('/')[4:]
					#in_url="%s/%s" % (pos_connect, '/'.join(db_path))
					#menu.Append(self.show_in[sid]+10000, "Mirror in %s (%s)" % (side,in_url))
			if disabled_favs:
				menu.Enable(self.add_to_favorites, False)
				menu.Enable(self.remove_from_favorites, False)
			if 0:
				menu.Append(self.popupID1, "FindItem tests")
				menu.Append(self.popupID2, "Iterate Selected")
				menu.Append(self.popupID3, "ClearAll and repopulate")
				menu.Append(self.popupID4, "DeleteAllItems")
				menu.Append(self.popupID5, "GetItem")
				menu.Append(self.popupID6, "Edit")

			# Popup the menu.  If an item is selected then its handler
			# will be called before PopupMenu returns.
			#pprint(dir(menu))
			self.PopupMenu(menu)
			
			menu.Destroy()
	def OnDeleteConnection(self, event):		
		print 'F9 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
		list=self.list #self.frame.getListFromPos(self.pos)
		self.delete_conn = []
		idx = -1
		while True: # find all the selected items and put them in a list
			idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if idx == -1:
				break
			self.delete_conn.append(list.getItemInfo(idx))
		print self.delete_conn		
		dlg = DeleteConnectDialog(self, -1, "Delete Oracle connect.", size=(250, 250),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			print "You pressed OK\n"
			#self.log.write("You pressed OK\n")
		else:
			print "You pressed Cancel\n"
			#self.log.write("You pressed Cancel\n")
		table_to=None

		dlg.Destroy()
	def getConnectInfo(self,conn_name):
		varsToPath=self.getVarsToPath()
		#print self.parent.getVarsToPath()
		xpath=varsToPath.split('/')[1:4]
		print xpath
		#assert len(xpath)==3, 'Cannot set xpath connect filter.'
		specfile_from ='%s.xml' % os.path.join(configDirLoc, xpath[0])
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)

		
			connector=doc.getElementsByTagName("connector")[0]
			#assert len(connector), 'Cannot find connector tag in %s.' % xpath[0]
			print connector
			print xpath
			print xpath[1].split('.')
			env_type=xpath[1].split('.')[0]
			env=connector.getElementsByTagName(env_type)[0]
			alias_name=xpath[1].split('.')[1]
			alias=env.getElementsByTagName(alias_name)[0]
			print alias
			#conn_name=xpath[2]
			print conn_name
			conn=alias.getElementsByTagName(conn_name)[0]
			print conn
			#pprint (dir( conn))
			#sys.exit(1)
		if conn.hasAttribute('schema'):
			return (conn.getAttribute("schema"),conn.getAttribute("sid"),conn.getAttribute("pword"),conn.getAttribute("HOST"),conn.getAttribute("PORT"))
		if conn.hasAttribute('user'):
			file_filter=None
			if conn.hasAttribute('file_filter'):
				file_filter=conn.getAttribute("file_filter")
			return (conn.getAttribute("user"),conn.getAttribute("host"),conn.getAttribute("pword"),conn.getAttribute("home"),file_filter)
		return (None, None, None, None, None )
		
	def OnEditConnection(self, event):		
		print 'F9 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
		list=self.list #self.frame.getListFromPos(self.pos)
		self.delete_conn = []
		idx = -1
		while True: # find all the selected items and put them in a list
			idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if idx == -1:
				break
			self.delete_conn.append(list.getItemInfo(idx))
		print self.delete_conn
		conn_alias=self.delete_conn[0][2].strip('[').strip(']')
		login=(user,db,pwd,host,port) = self.getConnectInfo(conn_alias)
		print login
		#sys.exit(1)
		#self.list.Freeze()
		dlg = EditOracleConnectDialog(self, -1, "Edit Oracle connect.", size=(450, 450),login=login,
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.SYSTEM_MENU | wx.CAPTION | wx.MAXIMIZE_BOX | wx.FRAME_NO_TASKBAR| wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN,
						 #style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=False,
						 )
		
		dlg.CenterOnScreen()
		val = dlg.Show()

			
		if 0:		
			dlg = DeleteConnectDialog(self, -1, "Delete Oracle connect.", size=(250, 250),
							 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
							 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
							 useMetal=useMetal,
							 )
			dlg.CenterOnScreen()
			# this does not return until the dialog is closed.
			val = dlg.ShowModal()

			if val == wx.ID_OK:
				print "You pressed OK\n"
				#self.log.write("You pressed OK\n")
			else:
				print "You pressed Cancel\n"
				#self.log.write("You pressed Cancel\n")
			table_to=None

			dlg.Destroy()
		
	def OnClearPassword(self, event):		
		print 'F9 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
		list=self.list #self.frame.getListFromPos(self.pos)
		self.delete_conn = []
		idx = -1
		while True: # find all the selected items and put them in a list
			idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if idx == -1:
				break
			self.delete_conn.append(list.getItemInfo(idx))
		print self.delete_conn		
		dlg = ClearPasswordDialog(self, -1, "Clear Oracle passwords.", size=(250, 250),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			print "You pressed OK\n"
			#self.log.write("You pressed OK\n")
		else:
			print "You pressed Cancel\n"
			#self.log.write("You pressed Cancel\n")
		table_to=None

		dlg.Destroy()

	def OnClearPasswords(self, event):		
		print 'F9 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
		list=self.list #self.frame.getListFromPos(self.pos)
		conf_list = []
		self.delete_conn = []
		idx = -1
		if 0:
			while True: # find all the selected items and put them in a list
				idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
				if idx == -1:
					break
				conf_list.append(list.getItemInfo(idx))
			print conf_list
			#sys.exit(1)
		cons={}
		if self.list.current_list in ('ConfigList'):
			#get all connects
			conf_list = []
			self.delete_conn = []
			idx = -1
			
			while True: # find all the selected items and put them in a list
				idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
				if idx == -1:
					break
				conf_list.append(list.getItemInfo(idx))
			print conf_list	
			for crow in conf_list:			
				cfile =crow[2].strip('[').strip(']')		
				config_file= '%s.xml' % os.path.join(configDirLoc, '%s' % cfile)
				print config_file		
				#get env connects
				env_list = self.list.db.getEnvironments(config_file)
				print env_list
				#sys.exit(1)
				
				cons[cfile]={}
				for eid, env in env_list.items():
					#print env
					_EnvironmentList=env[0]
					if _EnvironmentList not in cons[cfile]:
						cons[cfile][_EnvironmentList]=[]
					
					#print _EnvironmentList
					con =self.list.db.getConnectList(config_file,_EnvironmentList).values()
					#pprint(con)
					#print cons.items()
					#print con.items()
					#print cons.items()+con.items()
					cons[cfile][_EnvironmentList]=cons[cfile][_EnvironmentList] +con
		if self.list.current_list in ('EnvironmentList'):
			env_list = []
			self.delete_conn = []
			idx = -1
			
			while True: # find all the selected items and put them in a list
				idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
				if idx == -1:
					break
				env_list.append(list.getItemInfo(idx))
			print env_list
		
			cfile =self.list._ConfigList
			config_file= '%s.xml' % os.path.join(configDirLoc, '%s' % cfile)
			print config_file		
			#get env connects
			
			cons[cfile]={}
			for env in env_list:
				#print env
				_EnvironmentList=env[2].strip('[').strip(']')
				if _EnvironmentList not in cons[cfile]:
					cons[cfile][_EnvironmentList]=[]
				
				#print _EnvironmentList
				con =self.list.db.getConnectList(config_file,_EnvironmentList).values()
				#pprint(con)
				#print cons.items()
				#print con.items()
				#print cons.items()+con.items()
				cons[cfile][_EnvironmentList]=cons[cfile][_EnvironmentList] +con
		pprint(cons)
		#sys.exit(1)
		if 0:
			while True: # find all the selected items and put them in a list
				idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
				if idx == -1:
					break
				self.delete_conn.append(list.getItemInfo(idx))
		#print self.delete_conn		
		dlg = ClearPasswordsDialog(self, -1, "Clear Oracle passwords.", size=(250, 250),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal, plist=cons
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()
		if 0:
			if val == wx.ID_OK:
				print "You pressed OK\n"
				#self.log.write("You pressed OK\n")
			else:
				print "You pressed Cancel\n"
				#self.log.write("You pressed Cancel\n")
			table_to=None

		dlg.Destroy()
		
	def OnAddNewConnection(self, event):
		print 'OnAddNewConnection'
		index = -1 
		selected_items = [] 
		
		print 'F3 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = OracleConnectDialog(self, -1, "Add Oracle connect.", size=(450, 450),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()
		if 0:
			if val == wx.ID_OK:
				self.log.write("You pressed OK\n")
			else:
				self.log.write("You pressed Cancel\n")
		table_to=None

		dlg.Destroy()
		
		if 0:
			while 1: 
				index = self.list.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
				if index==-1: 
					break 
				selected_items.append(index) 
				item = self.list.GetItem(index)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				# This does the trick:
				self.list.SetItem(item)

			print 'si',selected_items
			self.addToFavorites(selected_items)
		
	def OnShowIn(self, event):
		print 'OnShowIn'
		#print event.GetEventObject().GetLabel(event.GetId())
		#print event.GetId()
		#sys.exit(1)
		#print str(event.GetId()-100)
		#print event.GetId()-20000
		(ignore,row,col) = str(event.GetId()-20000)
		pos_to= (int(row),int(col))
		#print pos_to
		#Publisher().sendMessage( "mirror_list", (self.list.current_list, self.getVarsToPath(), pos_to, self.getSide(self.pos)) )
		send("mirror_list", (self.list.current_list, self.getVarsToPath(), pos_to, self.getSide(self.pos)))
		
	def OnRightClick_00(self, event):
		print "OnRightClick %s\n" % self.list.GetItemText(self.currentItem)
		#self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))

		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.popupID5 = wx.NewId()
			self.popupID6 = wx.NewId()

			self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
			self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
			self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

		# make a menu
		menu = wx.Menu()
		# add some items
		menu.Append(self.popupID1, "FindItem tests")
		menu.Append(self.popupID2, "Iterate Selected")
		menu.Append(self.popupID3, "ClearAll and repopulate")
		menu.Append(self.popupID4, "DeleteAllItems")
		menu.Append(self.popupID5, "GetItem")
		menu.Append(self.popupID6, "Edit")

		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(menu)
		menu.Destroy()

	def OnAddToFavorites(self, event):
		print 'OnAddToFavorites'
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.list.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			item = self.list.GetItem(index)
			font = item.GetFont()
			font.SetWeight(wx.FONTWEIGHT_BOLD)
			item.SetFont(font)
			# This does the trick:
			self.list.SetItem(item)

		print 'si',selected_items
		self.addToFavorites(selected_items)

	def OnRemoveFromFavorites(self, event):
		print 'OnRemoveFromFavorites'
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.list.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			item = self.list.GetItem(index)
			font = item.GetFont()
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
			item.SetFont(font)
			# This does the trick:
			self.list.SetItem(item)

		print 'si',selected_items
		self.removeFromFavorites(selected_items)

		
	def getVarsToPath(self):
		relative_path='root'
		if 1 or update_cache:			
			vars=self.list.nav_list['vars'].values()[1:]
			if len(vars)>0:
				relative_path='%s/%s'% (relative_path,'/'.join(vars))
		return relative_path
	def getVarsToFavPath(self):
		fav_path='root'
		if 1 or update_cache:	
			if self.list.nav_list[self.list.current_list].has_key('fav_key_start'):
				fav_start_id=self.list.nav_list[self.list.current_list]['fav_key_start']
				print 'fav_start_id', fav_start_id
				fav_start_id +=1
				print self.list.nav_list['vars'].values()
				vars=self.list.nav_list['vars'].values()[fav_start_id:]
				print vars
				if len(vars)>0:
					fav_path='%s/%s'% (fav_path,'/'.join(vars))
			else:
				
				print 'self.list.nav_list[self.list.current_list] nas no fav_key_start'
				fav_path=None
		return fav_path		
	def addToFavorites(self, ids):	
		fav_path= self.getVarsToFavPath()
		relative_path= self.getVarsToPath()
		print fav_path
		if fav_path:
			#sys.exit(1)
			if 0:
				suffix='_favs%d%d' % self.pos
				favs=readFromCache(relative_path, suffix)
				#pprint (self.list.data)
				print 'old favs:', favs
				for id in ids:
					favs[self.list.data[self.list.current_list][id][0]]=1
				print favs
				writeToCache(relative_path, favs, suffix)
			gsuffix='gfavs%d%d' % self.pos
			gfavs=readFromCache('', gsuffix)	
			print 'old gfavs:', gfavs
			print 'relative_path:', relative_path
			fav_key='%d:%s' % (len(relative_path.split('/')),fav_path)
			if not gfavs.has_key(fav_key):
				gfavs[fav_key]={}
			print '#'*40
			print '#'*40
			print ids			
			for id in ids:			
				#print id
				item = self.list.GetItem(id,0)
				#print item
				fkey= item.GetText().strip('[').strip(']')
				#fkey=self.list.data[self.list.current_list][id][0]
				print fkey		
				gfavs[fav_key][fkey]=relative_path
			print 'new global favs:',gfavs
			writeToCache('', gfavs, gsuffix)		
		else:
			self.status='Cannot define favorites on column level.'
	def removeFromFavorites(self, ids):	
		relative_path= self.getVarsToPath()
		fav_path= self.getVarsToFavPath()
		#print fav_path
		if 0:
			suffix='_favs%d%d' % self.pos
			favs=readFromCache(relative_path, suffix)
			#pprint (self.list.data)
			#print 'old favs:', favs
			for id in ids:
				print 'removing:', self.list.data[self.list.current_list][id][0]
				if favs.has_key(self.list.data[self.list.current_list][id][0]):
					favs.pop(self.list.data[self.list.current_list][id][0])
			#print favs
			writeToCache(relative_path, favs, suffix)
		gsuffix='gfavs%d%d' % self.pos
		gfavs=readFromCache('', gsuffix)	
		#print 'old gfavs:', gfavs
		#print ids
		#for key, items in gfavs.items():			
			#print key,relative_path
			#print items
		fav_key='%d:%s' % (len(relative_path.split('/')),fav_path)
		if gfavs.has_key(fav_key):
			#pprint(dir(gfavs[ relative_path]))
			for id in ids:
				#print id,  self.list.data[self.list.current_list][id][0]
				#print gfavs[ relative_path].index(self.list.data[self.list.current_list][id][0])
				#print 'before', gfavs[fav_key]
				pop_val=self.list.data[self.list.current_list][id][0]
				if gfavs[fav_key].has_key(pop_val):
					gfavs[fav_key].pop(pop_val)
				#print 'after', gfavs[fav_key]
			#gfavs[relative_path].append(self.list.data[self.list.current_list][id][0])
			#print 'new global favs:',gfavs
			writeToCache('', gfavs, gsuffix)		
		
		
	def OnPopupTwo(self, event):
		#self.log.WriteText("Selected items:\n")
		index = self.list.GetFirstSelected()

		while index != -1:
			print "      %s: %s\n" % (self.list.GetItemText(index), self.getColumnText(index, 1))
			#self.log.WriteText("      %s: %s\n" % (self.list.GetItemText(index), self.getColumnText(index, 1)))
			index = self.list.GetNextSelected(index)

	def OnPopupThree(self, event):
		print "Popup three\n"
		#self.log.WriteText("Popup three\n")
		self.list.ClearAll()
		wx.CallAfter(self.PopulateList)

	def OnPopupFour(self, event):
		self.list.DeleteAllItems()

	def OnPopupFive(self, event):
		item = self.list.GetItem(self.currentItem)
		print item.m_text, item.m_itemId, self.list.GetItemData(self.currentItem)

	def OnPopupSix(self, event):
		self.list.EditLabel(self.currentItem)	

class DragListCtrlPanel_0(wx.Panel, listmix.ColumnSorterMixin):
	def __init__(self, parent, pos, panel_pos # log
	):
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
		#self.SetDoubleBuffered(True)
		global prog
		self.ulocPanel= wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(-1,50))
		#wx.BoxSizer(wx.HORIZONTAL)
		self.url_locator={}
		self.find_in_btn={}
		self.nav_hist=[]
		self.curr_hist_id=0
		self._histMenu=None
		self._favMenu=None
		self._popUpMenu = {}
		(self.row, self.col) =pos
		self.pos=pos
		self.panel_pos=panel_pos
		#print panel_pos
		#sys.exit(1)
		self.sides={'00':'Left','01':'Right'}
		self.status='Welcome to %s!' % prog
		self.count = {}
		self.root_status="ROOT: Double click on ORACLE to zoom into Table level."
		self.hist_btn=OrderedDict()
		#self.log = log		
		#print (type(parent.Parent))
		tID = wx.NewId()
		self.frame=parent.Parent
		#Publisher().subscribe(self.onUpdateLocation, "update_location")
		
		if 1:
			sizer = wx.BoxSizer(wx.VERTICAL)
			
			if wx.Platform == "__WXMAC__" and \
				   hasattr(wx.GetApp().GetTopWindow(), "LoadDemo"):
				self.useNative = wx.CheckBox(self, -1, "Use native listctrl")
				self.useNative.SetValue( 
					not wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") )
				self.Bind(wx.EVT_CHECKBOX, self.OnUseNative, self.useNative)
				sizer.Add(self.useNative, 0, wx.ALL | wx.ALIGN_RIGHT, 4)
				
			self.il = wx.ImageList(16, 16)

			self.idx1 = self.il.Add(images.Smiles.GetBitmap())
			self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
			self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())

			self.list = DragList(self, -1,self.pos)
			self.filter =self.getFilter(self,self.list)
			self.filter_history={}
			self.currentItem = 0
		

		if 1:
			self.btnHome = wx.Button(self, -1, "[.]", style=wx.BU_EXACTFIT, size=(30,20))
			self.btnUp = wx.Button(self, -1, "[..]", style=wx.BU_EXACTFIT, size=(30,20))
			

			imageFile = "bmp_source/arrow_back_dgrey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_back=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
			imageFile = "bmp_source/arrow_back_grey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_back.SetBitmapDisabled(image1)
			self.btn_back.Disable()
			imageFile = "bmp_source/arrow_forward_dgrey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_fwd=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
			imageFile = "bmp_source/arrow_forward_grey_16x2.png"
			image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			self.btn_fwd.SetBitmapDisabled(image1)
			self.Bind(wx.EVT_BUTTON, self.OnBackButton, self.btn_back)
			self.btn_back.Bind(wx.EVT_RIGHT_DOWN, self.OnBackButtonRightUp)
			#self.Bind(wx.EVT_RIGHT_UP, self.OnBackButtonRightUp, self.btn_back)
			
			self.Bind(wx.EVT_BUTTON, self.OnForwardButton, self.btn_fwd)
			self.btn_fwd.Bind(wx.EVT_RIGHT_DOWN, self.OnForwardButtonRightUp)
			#self.gen_bind(wx.EVT_BUTTON,self.btn_back, self.OnBackButton,(self.list.current_list))
			#self.gen_bind(wx.EVT_BUTTON,self.btn_fwd, self.OnForwardButton,(self.list.current_list))			
			self.btn_fwd.Disable()
				
			self.btnFav = wx.Button(self, -1, "Fav", style=wx.BU_EXACTFIT, size=(30,20))
			self.btnHist = wx.Button(self, -1, "Hist", style=wx.BU_EXACTFIT, size=(30,20))			
			#self.btnFwd = wx.Button(self, -1, "Forward", style=wx.BU_EXACTFIT)
			navig = wx.BoxSizer(wx.HORIZONTAL)
			navig.Add(self.btnHome, 0, wx.LEFT)
			navig.Add(self.btnUp, 0, wx.LEFT)
			navig.Add((5,5), 0, wx.LEFT)
			navig.Add(self.btn_back, 0, wx.LEFT)
			navig.Add((2,2), 0, wx.LEFT)
			navig.Add(self.btn_fwd, 0, wx.LEFT)			
			navig.Add((8,8), 0, wx.LEFT)
			#navig.Add(self.locator, 1, wx.LEFT)
			#navig.Add(self.btnFwd, 0, wx.LEFT)
			navig.Add(self.filter, 1, wx.EXPAND)
			
			navig.Add(self.btnHist, 0, wx.LEFT)		
			navig.Add(self.btnFav, 0, wx.LEFT)

			if 1:
				
				self.p_pos=[self.pos]
				#self.statusbar.SetSize((-1, 23))
				#self.statusbar.SetFieldsCount(4)
				#self.SetStatusBar(self.statusbar)        
				#self.statusbar.SetStatusWidths([  250, 120, 140])
				if 0:
					bmp = wx.ArtProvider_GetBitmap(wx.ART_ERROR,
												   wx.ART_TOOLBAR, (16,16))
					
					upbmp = wx.StaticBitmap(self.statusbar, -1, bmp)

					bmp = wx.ArtProvider_GetBitmap(wx.ART_HELP,
												   wx.ART_TOOLBAR, (16,16))
					
					downbmp = wx.StaticBitmap(self.statusbar, -1, bmp)
					btnmio = wx.Button(self.statusbar, -1, "Push Me!")
				
				if 0:
					choice = wx.Choice(self.statusbar, -1, size=(100,-1),
									   choices=['Hello', 'World!', 'What', 'A', 'Beautiful', 'Class!'])
					ticker = Ticker(self.statusbar, -1)
					ticker.SetText("Hello World!")
					ticker.SetBackgroundColour(wx.BLUE)
					ticker.SetForegroundColour(wx.NamedColour("YELLOW"))
					ticker.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False))
					statictext = wx.StaticText(self.statusbar, -1, "Welcome To %s!" % prog)
					
					self.ticker = ticker
				#bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
				#titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)

				self.timer={}
				self.timer_xref={}
				if 1:
					for pos in self.p_pos:
						i=wx.NewId()
						self.timer_xref[i]=pos
						self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
						self.timer[pos]=wx.Timer(self, id=i)
						#lambda event, i=i: self.Screens(event, the_id=i), id=i
						#self.gen_bind(wx.EVT_TIMER,self, self.TimerHandler,(pos))
						
				#items=[]
				self.sPanel = wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN) # ,size=(300, 30)
				self.statusbar = wx.BoxSizer(wx.VERTICAL)
				#self.sPanel.status = wx.BoxSizer(wx.HORIZONTAL)
				gauge={}
				self.gauge=gauge
				#self.gauge=gauge
				for pos in self.p_pos:
					self.gauge[pos] = wx.Gauge(self.sPanel, -1, size=(250, 20),	style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
					#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
					self.gauge[pos].SetPosition((1,1))
					self.gauge[pos].Hide()	
					#items.append(self.gauge[pos])
				#self.gauge = gauge

				#self.Bind(wx.EVT_TIMER, self.TimerHandler0)
				#self.gen_bind(wx.EVT_TIMER,self, self.TimerHandler_pos,(self.panel_pos[0]))
				btn_stop={}
				self.btn_stop=btn_stop
				#self.btn_stop=btn_stop
				for pos in self.p_pos:
					self.btn_stop[pos] = wx.Button(self.sPanel, -1, "Stop", size=(30,20)) 
					#self.sPanel.statusbar.Add([self.gauge[pos],self.btn_stop[pos]], 1, wx.EXPAND,1)
					#self.btn_stop[pos].Hide()
					self.btn_stop[pos].SetPosition((self.gauge[pos].GetSize()[0],1))
					self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
					self.btn_stop[pos].Hide()
					#items.append(self.btn_stop[pos])
				
				#btn_refresh={}
				#self.btn_refresh=btn_refresh
				#self.btn_stop=btn_stop
				#for pos in self.panel_pos:
				imageFile = "bmp_source/refresh_icon_16_grey2.png"
				image1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
				self.btn_refresh=wx.BitmapButton(self, id=-1, bitmap=image1,size = (image1.GetWidth()+6, image1.GetHeight()+6))
				self.btn_log = wx.Button(self, -1, "Log", size=(25,20))
				#self.btn_refresh = wx.Button(self, -1, "Refresh", size=(30,20)) 
				#self.sPanel.statusbar.Add([self.gauge[pos],self.btn_stop[pos]], 1, wx.EXPAND,1)
				#self.btn_stop[pos].Hide()
				#self.btn_refresh.SetPosition((1,1))
				self.gen_bind(wx.EVT_BUTTON,self.btn_refresh, self.OnRefreshList,(self.pos))
					#items.append(self.btn_stop[pos])				
									
				#for pos in self.panel_pos:
				#	self.btn_stop[pos].Hide()
				#self.Bind(wx.EVT_IDLE, self.IdleHandler)
				self.Bind(wx.EVT_CLOSE, self.OnClose)
				#self.Bind(wx.EVT_BUTTON, self.OnStopDbRequest, self.btn_stop)
				#self.fgs = wx.FlexGridSizer(1,3,5,10)
				#self.stt={}
				#for pos in self.panel_pos:
				self.stt =wx.StaticText(self.sPanel, -1, '%s' % self.status)	
				#self.sPanel.status.Add(self.stt[pos[1]], 0, wx.EXPAND,5)
				#fillin =wx.StaticText(self.sPanel, -1, "test   ")	
				#self.sPanel.status.Add(fillin, 1, wx.EXPAND,5)
				#items.append(self.stt[pos[1]])
				#self.fgs.AddItem(self.stt[pos[1]],pos=(0,0))
				self.stt.SetPosition((5,2))
				#print self.stt.GetSize()
				
				self.cb_c = wx.CheckBox(self, wx.ID_ANY, "cache")
				self.Bind(wx.EVT_CHECKBOX, self.OnUseCache, self.cb_c)
				self.cb_c.SetValue(False)
				self.cb_c.Enable(False)
				self.statusbar.Add((10,5))
				self.spanelbar = wx.BoxSizer(wx.HORIZONTAL)
				self.spanelbar.Add(self.sPanel, 1, wx.EXPAND|wx.LEFT,5)
				self.spanelbar.Add(self.btn_log, 0, wx.RIGHT)
				self.btn_log.Enable(False)
				self.spanelbar.Add((30,10), 0, wx.RIGHT)	
				self.spanelbar.Add(self.cb_c, 0, wx.LEFT|wx.CENTER)
				#self.spanelbar.Add((1,3), 0, wx.RIGHT)	
				#self.spanelbar.Add(self.btn_log, 0, wx.RIGHT)
				#self.spanelbar.Add((5,5), 0, wx.RIGHT)
				self.spanelbar.Add(self.btn_refresh, 0, wx.RIGHT|wx.CENTER)
				self.statusbar.Add(self.spanelbar, 1,wx.EXPAND)
				#self.statusbar.Add((5,1))
				#self.SetSizer(self.statusbar)
				#self.sPanel.SetSizer(self.sPanel.status)
				#self.fgs.AddMany(items)
				#self.statusbar.Add(self.fgs, 0, wx.ALL,0)
				#print(dir(self.fgs.AddItem))
				#items = [multi_btn,single_btn]
				#self.statusbar.Add(self.sPanel, 0, wx.ALL|wx.VERTICAL,0)

				


			


		#self.PopulateList()

		# Now that the list exists we can init the other base class,
		# see wx/lib/mixins/listctrl.py
		#self.itemDataMap = getConfigs(configDirLoc)
		
		#self.SortListItems(0, True)


		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
		#self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
		#self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
		#self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
		#self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
		#self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
		#self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)

		#self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		#self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

		# for wxMSW
		#self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

		# for wxGTK
		self.list.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
		self.Bind(wx.EVT_BUTTON, self.OnHome, self.btnHome)
		self.Bind(wx.EVT_BUTTON, self.OnUp, self.btnUp)	
		self.gen_bind(wx.EVT_BUTTON,self.btnFav, self.OnFavButton,(self.list.current_list))
		self.gen_bind(wx.EVT_BUTTON,self.btnHist, self.OnHistButton,(self.list.current_list))
		self.Bind(wx.EVT_SET_FOCUS, self.onFocus)  		
		#self.Bind(wx.EVT_BUTTON, self.OnForward, self.btnFwd)	
		self.location=[]		
		#Publisher().subscribe(self.onForceSearch, "force_search")			
		#Publisher().subscribe(self.onDbEvent, "db_thread_event")
		#Publisher().subscribe(self.onFileDirEvent, "remotedir_thread_event")
		#Publisher().subscribe(self.onFileDirEvent, "localdir_thread_event")
		sub(self.onForceSearch, "force_search")
		sub(self.__onDbEvent, "db_thread_event")
		sub(self.onFileDirEvent, "remotedir_thread_event")
		sub(self.onFileDirEvent, "localdir_thread_event")
		#Publisher().subscribe(self.onRefreshListEvent, "refresh_list_event")
		self.list.Populate()
		self.itemDataMap=self.list.data[self.list.current_list]
		#listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		#self.RecreateList(None,(self.list,self.filter))
		
		self.no_url_loc=wx.StaticText(self.ulocPanel, -1, self.root_status)
		#self.no_url_loc.SetLabel()
		self.no_url_loc.SetPosition((0,0))		
		if 1:
			if 0:
				from wx.lib.agw import ultimatelistctrl as ULC


				self.url_combo_list = ULC.UltimateListCtrl(self.ulocPanel, wx.ID_ANY, agwStyle=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES|wx.LC_SINGLE_SEL|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

				self.url_combo_list.InsertColumn(0, "Column 1")
				self.url_combo_list.InsertColumn(1, "Column 2")

				index = self.url_combo_list.InsertStringItem(sys.maxint, "Item 1")
				self.url_combo_list.SetStringItem(index, 1, "Sub-item 1")

				index = self.url_combo_list.InsertStringItem(sys.maxint, "Item 2")
				self.url_combo_list.SetStringItem(index, 1, "Sub-item 2")

				choice = wx.Choice(self.url_combo_list, -1, choices=["one", "two"])
				index = self.url_combo_list.InsertStringItem(sys.maxint, "A widget")

				self.url_combo_list.SetItemWindow(index, 1, choice, expand=True,)
			if 0:
				self.cc = wx.combo.ComboCtrl(self, style=wx.combo.CC_BUTTON_OUTSIDE_BORDER, size=(30,-1))
				self.cc.SetPopupExtents(-1,100)
				self.cc.SetPopupMaxHeight(50)
				# Create a Popup
				self.popup = ListCtrlComboPopup()

				# Associate them with each other.  This also triggers the
				# creation of the ListCtrl.
				self.cc.SetPopupControl(self.popup)
				for x in range(75):
					self.popup.AddItem("Item-%02d" % x)

			
			#self.popup.Create(wx.PreListCtrl())
			# Add some items to the listctrl.
			
			if 0:
				self.url_combo_list = wx.ListCtrl(self, -1,  size=(-1,100),
				style=wx.LC_REPORT
							 |wx.BORDER_SUNKEN
							 )
							 
				self.url_combo_list.InsertColumn(0, 'Subject')

				self.url_combo_list.InsertColumn(1, 'Due')

				self.url_combo_list.InsertColumn(2, 'Location', width=125)
				self.url_combo_list.InsertStringItem(0, '1')
				self.url_combo_list.SetStringItem(0, 1, "01/19/2010")
				self.url_combo_list.SetStringItem(0, 2, "USA")


			#self.url_combo_list.Hide()
			#print dir(self.ulocPanel)
			#self.createUrlLocator()
			upsizer = wx.BoxSizer(wx.HORIZONTAL)
			upsizer.Add((5,15), 0, wx.EXPAND)
			upsizer.Add(self.ulocPanel, 1, wx.EXPAND|wx.ALL)
			
			sizer = wx.BoxSizer(wx.VERTICAL)
			#sizer.Add(self.locator, 0, wx.EXPAND)
			sizer.Add((2,2), 0, wx.EXPAND)
			sizer.Add(upsizer, 0, wx.EXPAND)
			sizer.Add((3,3), 0, wx.EXPAND)
			#sizer.Add(self.url_combo_list, 0, wx.EXPAND)
			sizer.Add(navig, 0, wx.EXPAND)
			sizer.Add(self.list, 1, wx.EXPAND,4)
			sizer.Add(self.statusbar, 0,wx.EXPAND)
			
			
			
			if 'wxMac' in wx.PlatformInfo:
				sizer.Add((5,5))  # Make sure there is room for the focus ring
			self.SetSizer(sizer)
			self.SetAutoLayout(True)
			
		#Publisher().subscribe(self.onGaugeStop, "stop_db_progress_gauge")
		#Publisher().subscribe(self.onGaugeStart, "start_db_progress_gauge")
		#Publisher().subscribe(self.onUpdateSbLocUrl, "update_status_bar")
		#Publisher().subscribe(self.onMirrorList, "mirror_list")
		sub(self.__onGaugeStop, "stop_db_progress_gauge")
		sub(self.__onGaugeStart, "start_db_progress_gauge")
		sub(self.__onUpdateSbLocUrl, "update_status_bar")
		sub(self.onMirrorList, "mirror_list")
		
	def onFocus(self, event):
		print 'got Focus'
		#sys.exit(1)
		#event.Skip()
	def getListFromPos(self,pos):
		return self.frame.getListFromPos(pos)		
	def OnRefreshList(self, event, params):
		( pos) = params
		if pos==self.pos:
			self.status='%s reloaded.' % self.list.current_list 
			self.list.refreshList()
		event.Skip()
		
	def onMirrorList(self, evt):
		(loc_to, path_to,pos_to, side_from) =  evt.data
		if pos_to==self.pos:
			#set list to path
			vars=self.list.getVarsFromPath(path_to,'/')[1:]
			print 'new vars:'
			print vars
			self.list.setNavlist()	
			if len(vars)>2:
				self.list.connect_type=self.list.getConnectType(path_to)
				print self.list.connect_type
				print self.list.nav_list.keys()
				self.list.extendNavlist(self.list.connect_type)
				print self.list.nav_list.keys()
			
			self.list.initVarsFromPath(path_to,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			
			self.list.setCurrListName(loc_to, 'reset')	
			self.status='Mirrored from %s (%s)' % (side_from, path_to)			
			self.list.execList(loc_to)
			#self.status='Mirrored from %s (%s)' % (side_from, path_to)
		#event.Skip()		
	def OnUseCache(self, event):
		print 'use cache', self.pos
		event.Skip()		
	def Status(self, msg):
		pass
		#self.stt.SetLabel(msg)
		
	def OnStopDbRequest(self, event, params):
		( pos) = params
		if pos==self.pos:
			#Publisher().sendMessage( "stop_db_request", (pos) )
			send( "stop_db_request", (pos))
		event.Skip()
	def setUrlLocator(self):
		#print '--setUrlLocator---'
		#self.url_locator={}
		print  self.url_locator
		nav_keys=self.list.nav_list.keys()
		if len(self.url_locator)<len(nav_keys)-1:
			print len(self.url_locator),len(nav_keys)
			self.createUrlLocator()
		
		for loc_id in range(len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if 1 and loc!='vars':
				print 'hiding', loc 
				if self.url_locator.has_key(loc):
					self.url_locator[loc].Hide()
					self.find_in_btn[loc].Hide()
				
		#print  self.list.nav_list.keys()
		#print self.list.loc_url
		offset=0
		prev_loc=None
		print  nav_keys
		print self.list.nav_list['vars'].keys()
		var_keys=self.list.nav_list['vars'].keys()[1:]
		print var_keys
		if not var_keys:
			#self.clearUrlLocator()
			pass
		else:
			for loc_id in range(len(var_keys)): #self.list.loc_url:
				loc=var_keys[loc_id]
				print 'location url',  loc
				if 1 or self.list.nav_list['vars'].has_key(loc):
					if 1 or loc!='vars' and loc_id>0:
						#print '???????',loc , self.list.nav_list['vars'].has_key(loc)
						#print self.list.nav_list['vars']
						#self.url_locator[loc].Show()
						if 0:
							if loc_id>1:
								offset +=self.url_locator[loc].GetSize()[0] +12 #+self.find_in_btn[prev_loc].GetSize()[0]
								#print 'offset', offset
								#print self.url_locator[prev_loc].GetSize()[0]
								#print self.find_in_btn[prev_loc].GetSize()[0]
							else:
								if loc_id==1:
									offset +=self.find_in_btn[loc].GetSize()[0] 
									self.find_in_btn[loc].SetPosition((0,0))
									self.find_in_btn[loc].Show()
						self.find_in_btn[loc].SetPosition((offset,0))
							
						
						offset +=self.find_in_btn[loc].GetSize()[0]		
						if 0:
							if self.list.nav_list['vars'].has_key(loc) :					
								#print '000has key00', loc,self.list.current_list

								
								url_label = self.list.nav_list['vars'][loc]
								self.url_locator[loc].SetLabel(url_label)						
								self.url_locator[loc].SetPosition((offset,0))
								self.url_locator[loc].Show()
								

								offset +=self.url_locator[loc].GetSize()[0]
								self.find_in_btn[loc].Show()

								#self.url_locator[loc].Refresh()
								#if self.list.current_list==loc:
								#	break;
							else:
								pass
						if loc_id==(len(var_keys)-1):
							#self.find_in_btn[loc].SetPosition((0,0))
							#self.find_in_btn[loc].Show()						
							#print '000has key00', loc,self.list.current_list
							
							url_label = self.list.nav_list['vars'][loc]
							print 'last url', loc,self.list.current_list, url_label
							self.no_url_loc.SetLabel(url_label)
							self.no_url_loc.SetPosition((offset,0))
							self.no_url_loc.Show()

							self.find_in_btn[loc].Show()
							break
						else:
							url_label = self.list.nav_list['vars'][loc]
							print 'mid url', loc,self.list.current_list,url_label
							self.url_locator[loc].SetLabel(url_label)						
							self.url_locator[loc].SetPosition((offset,0))
							self.url_locator[loc].Show()
							

							offset +=self.url_locator[loc].GetSize()[0]
							self.find_in_btn[loc].Show()

							#self.url_locator[loc].Refresh()
							#if self.list.current_list==loc:
							#	break;

								
					prev_loc=loc
				
	def setUrlLocator_0(self):
		#print '--setUrlLocator---'
		#self.url_locator={}
		print  self.url_locator
		if not self.url_locator:
			self.createUrlLocator()
		nav_keys=self.list.nav_list.keys()
		for loc_id in range(1,len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if 1 and loc!='vars':
				print 'hiding', loc 
				self.url_locator[loc].Hide()
				self.find_in_btn[loc].Hide()
				
		#print  self.list.nav_list.keys()
		#print self.list.loc_url
		offset=0
		prev_loc=None
		print  nav_keys
		for loc_id in range(len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if 1 or self.list.nav_list['vars'].has_key(loc):
				if loc!='vars' and loc_id>0:
					#print '???????',loc , self.list.nav_list['vars'].has_key(loc)
					#print self.list.nav_list['vars']
					#self.url_locator[loc].Show()
					if 0:
						if loc_id>1:
							offset +=self.url_locator[prev_loc].GetSize()[0] +12 #+self.find_in_btn[prev_loc].GetSize()[0]
							#print 'offset', offset
							#print self.url_locator[prev_loc].GetSize()[0]
							#print self.find_in_btn[prev_loc].GetSize()[0]
						else:
							if loc_id==1:
								offset +=self.find_in_btn[loc].GetSize()[0] 
								self.find_in_btn[loc].SetPosition((0,0))
								self.find_in_btn[loc].Show()
					self.find_in_btn[loc].SetPosition((offset,0))
						
					
					offset +=self.find_in_btn[loc].GetSize()[0]						
					if self.list.nav_list['vars'].has_key(loc) :					
						#print '000has key00', loc,self.list.current_list

						
						url_label = self.list.nav_list['vars'][prev_loc]
						self.url_locator[loc].SetLabel(url_label)						
						self.url_locator[loc].SetPosition((offset,0))
						self.url_locator[loc].Show()
						

						offset +=self.url_locator[loc].GetSize()[0]
						self.find_in_btn[loc].Show()

						#self.url_locator[loc].Refresh()
						#if self.list.current_list==loc:
						#	break;
					else:
						if loc==self.list.current_list:
							#self.find_in_btn[loc].SetPosition((0,0))
							#self.find_in_btn[loc].Show()						
							#print '000has key00', loc,self.list.current_list
							url_label = self.list.nav_list['vars'][prev_loc]
							self.no_url_loc.SetLabel(url_label)
							self.no_url_loc.SetPosition((offset,0))
							self.no_url_loc.Show()
							self.find_in_btn[loc].Show()
							break
						else:
							pass
						#self.url_locator[loc].Hide()

							
				prev_loc=loc

	def clearUrlLocator(self, msg="Retrieving list..."):
		self.no_url_loc.SetLabel(msg)
		self.no_url_loc.SetPosition((0,0))
		if 1:
			for loc in self.url_locator:
				self.url_locator[loc].Destroy()
				self.find_in_btn[loc].Destroy()
		self.url_locator={}
		self.find_in_btn={}
	def createUrlLocator(self):	
		print '--Creating URL locator---'
		
		offset=0


		#self.clearUrlLocator() 
		nav_keys=self.list.nav_list.keys()
		prev_loc=nav_keys[0]
		for loc_id in range(len(nav_keys)-1): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if not self.url_locator.has_key(loc):
				print 'creating url ',loc
				if self.list.nav_list['vars'].has_key(loc):
					url_label = self.list.nav_list['vars'][loc]
				else: 
					url_label=loc
				ul=hl.HyperLinkCtrl(self.ulocPanel, -1, url_label,  URL=loc)
				ul.AutoBrowse(False)
				ul.SetColours("BLUE", "BLUE", "BLUE")
				ul.EnableRollover(True)
				ul.SetUnderlines(False, False, True)
				#ul.SetBold(True)
				ul.OpenInSameWindow(True)
				ul.SetToolTip(wx.ToolTip("Click to explore %s" % url_label))
				ul.UpdateLink()
				#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
				ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
				self.url_locator[loc]=ul
				#create find_in button
				self.find_in_btn[loc] = wx.Button(self.ulocPanel, -1, "/", size=(12,16))
				#self.find_in_btn[loc].Bind(wx.EVT_BUTTON, self.OnFindInButton)
				self.gen_bind(wx.EVT_BUTTON,self.find_in_btn[loc], self.OnFindInButton,(loc_id,loc))
				#self.find_in_btn[loc].Hide()
				self.url_locator[loc].Hide()
				self.find_in_btn[loc].Hide()
			prev_loc=loc
			#else:
			#	print 'passing ',loc
	def createUrlLocator_00(self):	
		print '--Creating URL locator---'
		
		offset=0
		self.no_url_loc=wx.StaticText(self.ulocPanel, -1, '')

		self.clearUrlLocator() 
		nav_keys=self.list.nav_list.keys()
		prev_loc=nav_keys[0]
		for loc_id in range(len(nav_keys)): #self.list.loc_url:
			loc=nav_keys[loc_id]
			if loc!='vars':
				print 'creating url ',loc
				if self.list.nav_list['vars'].has_key(loc):
					url_label = self.list.nav_list['vars'][loc]
				else: 
					url_label=loc
				ul=hl.HyperLinkCtrl(self.ulocPanel, -1, url_label,  URL=loc)
				ul.AutoBrowse(False)
				ul.SetColours("BLUE", "BLUE", "BLUE")
				ul.EnableRollover(True)
				ul.SetUnderlines(False, False, True)
				#ul.SetBold(True)
				ul.OpenInSameWindow(True)
				ul.SetToolTip(wx.ToolTip("Click to explore %s" % url_label))
				ul.UpdateLink()
				#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
				ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
				self.url_locator[loc]=ul
				#create find_in button
				self.find_in_btn[loc] = wx.Button(self.ulocPanel, -1, "/", size=(12,16))
				#self.find_in_btn[loc].Bind(wx.EVT_BUTTON, self.OnFindInButton)
				self.gen_bind(wx.EVT_BUTTON,self.find_in_btn[loc], self.OnFindInButton,(loc_id,loc))
				self.find_in_btn[loc].Hide()

				prev_loc=loc
			else:
				print 'passing ',loc				
	def OnLink(self, event):
		#print dir(event)
		loc=event.GetEventObject().GetURL()
		var=event.GetEventObject().GetLabel()
		
		print 'aaaaaaaaaaaaaaaaaaaaaaa', loc, var
		#list_name='ConfigList'
		self.status=loc
		self.list.clearListVars(loc)
		self.list.setVar(loc, var)
		#print event.GetEventObject().GetLabel()
		#self.list.setCurrListName(loc, 'reset')
		self.list.execNextList(loc)		
		event.Skip()
	def OnFindInButton(self, event,params):
		(loc_id,loc)=params
		print (loc_id,loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		print 'creating PopupMenu((((((((((((', loc
		self.CreatePopupMenu(loc)

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._popUpMenu[loc].SetOwnerHeight(btnSize.y)
		self._popUpMenu[loc].Popup(wx.Point(btnPt.x, btnPt.y), self)		
		if 0:
			self.url_combo_list = ListCtrl2()
			self.url_combo_list.SetPosition((btn.GetPosition()[0],0))
			self.url_combo_list.Show()
			#self.url_combo_list.SetFocus()
			#print dir(self.url_combo_list)
			#self.url_combo_list.SetWindow(self)
			#self.url_combo_list.Focus()
			#print dir(self.url_combo_list)
		if 0:
			self.url_combo_list = wx.ListCtrl(self )
			#self.url_combo_list.Create(wx.PreListCtrl())	 
			self.url_combo_list.InsertColumn(0, 'Subject')

			self.url_combo_list.InsertColumn(1, 'Due')

			self.url_combo_list.InsertColumn(2, 'Location', width=125)
			self.url_combo_list.InsertStringItem(0, '1')
			self.url_combo_list.SetStringItem(0, 1, "01/19/2010")
			self.url_combo_list.SetStringItem(0, 2, "USA")
			#self.url_combo_list.SetPosition((btn.GetPosition()[0],0))

		#event.Skip()
	def CreatePopupMenu(self,loc):

		if 1 or not self._popUpMenu.has_key(loc):
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._popUpMenu[loc] = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			print self.pos
			print loc
			print self.list.data.keys()
			if loc in self.list.data.keys():
				for key, item in self.list.data[loc].items():
					menuItem = FM.FlatMenuItem(pmenu, 20001+key, '%s' % item[0], "", wx.ITEM_RADIO)
					print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if item[0]==self.list.nav_list['vars'][loc]:
						#pprint(dir(menuItem))
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnMenu,(loc,item[0]))
				
			
	def OnMenu(self, event,params):	
		(loc,item) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		item_id=event.GetId()-20001
		print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		print  params
		self.list.nav_list['vars'][loc]=item
		self.list.execList(self.list.current_list)
		self._popUpMenu.pop(loc)
		
	def CreatePopupMenu0(self):

		if not self._popUpMenu:
		
			self._popUpMenu = FM.FlatMenu()
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			subMenu = FM.FlatMenu()
			subSubMenu = FM.FlatMenu()

			# Create the menu items
			menuItem = FM.FlatMenuItem(self._popUpMenu, 20001, "First Menu Item", "", wx.ITEM_CHECK)
			self._popUpMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(self._popUpMenu, 20002, "Sec&ond Menu Item", "", wx.ITEM_CHECK)
			self._popUpMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(self._popUpMenu, wx.ID_ANY, "Checkable-Disabled Item", "", wx.ITEM_CHECK)
			menuItem.Enable(False)
			self._popUpMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(self._popUpMenu, 20003, "Third Menu Item", "", wx.ITEM_CHECK)
			self._popUpMenu.AppendItem(menuItem)

			self._popUpMenu.AppendSeparator()

			# Add sub-menu to main menu
			menuItem = FM.FlatMenuItem(self._popUpMenu, 20004, "Sub-&menu item", "", wx.ITEM_NORMAL, subMenu)
			self._popUpMenu.AppendItem(menuItem)

			# Create the submenu items and add them 
			menuItem = FM.FlatMenuItem(subMenu, 20005, "&Sub-menu Item 1", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)
		
			menuItem = FM.FlatMenuItem(subMenu, 20006, "Su&b-menu Item 2", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subMenu, 20007, "Sub-menu Item 3", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subMenu, 20008, "Sub-menu Item 4", "", wx.ITEM_NORMAL)
			subMenu.AppendItem(menuItem)

			# Create the submenu items and add them 
			menuItem = FM.FlatMenuItem(subSubMenu, 20009, "Sub-menu Item 1", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)
		
			menuItem = FM.FlatMenuItem(subSubMenu, 20010, "Sub-menu Item 2", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subSubMenu, 20011, "Sub-menu Item 3", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)

			menuItem = FM.FlatMenuItem(subSubMenu, 20012, "Sub-menu Item 4", "", wx.ITEM_NORMAL)
			subSubMenu.AppendItem(menuItem)

			# Add sub-menu to submenu menu
			menuItem = FM.FlatMenuItem(subMenu, 20013, "Sub-menu item", "", wx.ITEM_NORMAL, subSubMenu)
			subMenu.AppendItem(menuItem)			
	def CreateLongPopupMenu(self):

		if hasattr(self, "_longPopUpMenu"):
			return

		self._longPopUpMenu = FM.FlatMenu()
		sub = FM.FlatMenu()
		
		#-----------------------------------------------
		# Flat Menu test
		#-----------------------------------------------
		
		for ii in xrange(30):
			if ii == 0:
				menuItem = FM.FlatMenuItem(self._longPopUpMenu, wx.ID_ANY, "Menu Item #%ld"%(ii+1), "", wx.ITEM_NORMAL, sub)
				self._longPopUpMenu.AppendItem(menuItem)

				for k in xrange(5):

					menuItem = FM.FlatMenuItem(sub, wx.ID_ANY, "Sub Menu Item #%ld"%(k+1))
					sub.AppendItem(menuItem)

			else:

				menuItem = FM.FlatMenuItem(self._longPopUpMenu, wx.ID_ANY, "Menu Item #%ld"%(ii+1))
				self._longPopUpMenu.AppendItem(menuItem)
				
	def OnMouseEvent1(self, event):
		self.url_combo_list.Show()
		#self.url_combo_list.Focus()
		self.url_combo_list.Refresh()
		event.Skip()
		
	def OnItemSelected(self, event):
		##print event.GetItem().GetTextColour()
		self.currentItem = event.m_itemIndex
		#print self.list.GetItemText(self.currentItem)
		msg='%s %s ' % (self.list.current_list[:-4], self.list.GetItemText(self.currentItem).strip('[]'))
		self.Status(msg)		
		#print 'selected'
		#print(self)
		btns=self.list.nav_list[self.list.current_list]['hot_keys']
		#print btns
		#Publisher().sendMessage( "enable_buttons", (self.pos,btns) )	
		send("enable_buttons", (self.pos,btns))		
		event.Skip()		
		
	def gen_bind(self, type, instance, handler, *args, **kwargs):
		self.Bind(type, lambda event: handler(event, *args, **kwargs), instance)			
	def onGaugeStop_rem(self, evt):
		( pos) = evt.data
		if pos==self.pos:		
			print 'onGaugeStop', pos
			self.gaugeStop(pos)	
			#self.gauge[pos].Hide()
			#self.btn_stop[pos].Hide()	

	def __onGaugeStop(self,data, extra1, extra2=None):
		( pos) = data
		if pos==self.pos:		
			print 'onGaugeStop', pos
			self.gaugeStop(pos)	
			#self.gauge[pos].Hide()
			#self.btn_stop[pos].Hide()				
	def onUpdateSbLocUrl(self, evt):
		(loc,pos) = evt.data
		if pos==self.pos:
			#print self.stt
			print loc
			print pos
			#self.stt.SetLabel(loc)
		
	def onGaugeStart(self, evt):
		( pos) = evt.data
		print '=============================onGaugeStart',pos,self.pos
		if pos==self.pos:		
			#self.sPanel.SetSizer(self.sPanel.statusbar)
			print 'onGaugeStart',pos
			self.gaugeStart(pos)
			#self.gauge[pos].Show()
			#self.btn_stop[pos].Show()			
		
	def gaugeStart(self,pos):
		print pos
		print self.gauge
		print  'gaugeStart'
		if pos==self.pos:		
			#self.stt.Hide()
			self.gauge[pos].Show()
			self.btn_stop[pos].Show()
			self.timer[pos].Start(100)
			self.count[pos] = 0  
	def gaugeStop(self,pos):
		if pos==self.pos:	
			self.timer[pos].Stop()
			self.count[pos] = 0 
			#self.gauge.Freeze()
			self.gauge[pos].Hide()
			self.btn_stop[pos].Hide()
			#self.stt.Show()	
			#tmpitem = self.statusbar.GetChildren()
			#print tmpitem
			#self.statusbar.Replace ( 0, tmpitem[2])
			#self.sPanel.SetSizer(self.sPanel.status)			
	def __del__(self):
		for pos in self.panel_pos:
			self.timer[pos].Stop()
	def TimerHandler0(self, event,the_id):
		#(pos)=params
		pos=self.timer_xref[the_id]
		#print 'the_id', the_id,pos
		self.count[pos] = self.count[pos] + 15

		if self.count[pos] >= 180:
			self.count[pos] = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		
		self.gauge[pos].SetValue(self.count[pos])
		#self.gauge.Pulse()
		
	def TimerHandler_pos(self, event,params):
		(pos)=params
		self.count = self.count + 15

		if self.count >= 180:
			self.count = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		pos=self.panel_pos[0]
		self.gauge[pos].SetValue(self.count)
		#self.gauge.Pulse()
		
	def TimerHandler_(self, event,params):
		(pos)=params
		self.count[pos] = self.count[pos] + 15

		if self.count[pos] >= 180:
			self.count[pos] = 0
		#print self.count
		#self.gauge.Show()
		print '||||||||||||||||| setting count', self.count[pos]
		self.gauge[pos].SetValue(self.count[pos])
		#self.gauge.Pulse()
		
	def onShowProgress(self, evt):
		if 0:
			self.progress_bar.Show()
			self.progress_bar.SetRange(10)
			print 'in ShowProgress'
			self.progress_bar.SetValue(5)
			#print (dir(self.progress_bar))
		self.gauge.Show()
	def OnClose(self, event):

		#self.ticker.Stop()
		self.Destroy()

	def OnSize1(self, event):
		size = self.GetSize()
		print 'Size event'
		#self.splitter.SetSashPosition(size.x / 2)
		#self.sb.SetStatusText(os.getcwd())
		event.Skip()


	def OnDoubleClick(self, event):
		global prog
		size =  self.GetSize()
		self.splitter.SetSashPosition(size.x / 2)

		self.statusbar = ESB.EnhancedStatusBar(self, -1)
		self.statusbar.SetSize((-1, 23))
		self.statusbar.SetFieldsCount(7)
		self.SetStatusBar(self.statusbar)        
		self.statusbar.SetStatusWidths([50, 50, 100, 120, 120, 140, -1])

		bmp = wx.ArtProvider_GetBitmap(wx.ART_ERROR,
									   wx.ART_TOOLBAR, (16,16))
		
		upbmp = wx.StaticBitmap(self.statusbar, -1, bmp)

		bmp = wx.ArtProvider_GetBitmap(wx.ART_HELP,
									   wx.ART_TOOLBAR, (16,16))
		
		downbmp = wx.StaticBitmap(self.statusbar, -1, bmp)
		btnmio = wx.Button(self.statusbar, -1, "Push Me!")
		gauge = wx.Gauge(self.statusbar, -1, 50)
		choice = wx.Choice(self.statusbar, -1, size=(100,-1),
						   choices=['Hello', 'World!', 'What', 'A', 'Beautiful', 'Class!'])
		ticker = Ticker(self.statusbar, -1)
		ticker.SetText("Hello World!")
		ticker.SetBackgroundColour(wx.BLUE)
		ticker.SetForegroundColour(wx.NamedColour("YELLOW"))
		ticker.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False))
		statictext = wx.StaticText(self.statusbar, -1, "Welcome To %s!" % prog)
		
		self.ticker = ticker
		self.gauge = gauge

		self.count = 0        
		
		statusbarchildren = self.statusbar.GetChildren()
		for widget in statusbarchildren:
			self.statusbar.AddWidget(widget)

		self.Bind(wx.EVT_IDLE, self.IdleHandler)
		self.Bind(wx.EVT_CLOSE, self.OnClose)


	def IdleHandler(self, event):
		
		self.count = self.count + 1

		if self.count >= 100:
			self.count = 0

		self.gauge[pos].SetValue(self.count)
		
	def onDbEvent(self, evt):
		print 'onDbEvent'
		(st, pos,cache,result) = evt.data
		print '--onDbEvent', st
		print self.pos,'==',pos
		if st=='done':
			if self.pos==pos:
				(status, err, rowcount,headers, out) = result
				
				data={}
				i=0
				for rec in out:
					data[i]=rec
					i +=1					
				self.list.data[self.list.current_list]=data
				self.itemDataMap=self.list.data[self.list.current_list]
				
				self.RecreateList(None,(self.list,self.filter))				
				#self.setListData()
				self.list.Thaw()
				listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		if st=='aborted':
			print '-----------request aborted',self.pos,pos
			if self.pos==pos:
				print 'request aborted',pos
				self.gaugeStop(self.pos)	
				self.list.Thaw()
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)
	def onFileDirEvent(self, evt):
		print 'onFileDirEvent'
		(st, pos,cache,result) = evt.data
		print '--onFileDirEvent', st
		print self.pos,'==',pos
		if st=='done':
			if self.pos==pos:
				#(status, err, rowcount,headers, out) = result
				
				data=result

				self.list.data[self.list.current_list]=data
				self.itemDataMap=self.list.data[self.list.current_list]
				
				self.RecreateList(None,(self.list,self.filter))				
				#self.setListData()
				self.list.Thaw()
				listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		if st=='aborted':
			print '-----------request aborted',self.pos,pos
			if self.pos==pos:
				print 'request aborted',pos
				self.gaugeStop(self.pos)	
				self.list.Thaw()
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)
		
	def onRefreshListEvent(self, evt):
		print 'onRefreshListEvent'
		(st, pos,cache,result) = evt.data
		print 'onRefreshListEvent', st
		print self.pos,'==',pos
		if st=='xml_list':
			if self.pos==pos:
				self.list.data[self.list.current_list]=result
				self.itemDataMap=self.list.data[self.list.current_list]
				self.RecreateList(None,(self.list,self.filter))	
		#if self.pos==pos:
		#	updateCache(cache,self.list.data)		

	def onUpdateLocation(self, evt):
		(position, data)=evt.data
		print '----------------onUpdateLocation', position, self.pos, data
		if position==self.pos:
			(direction, text) = data
			print '----------------onUpdateLocation', direction, text
			#self.filter.SetValue(fltr)	
		#evt.Skip()
	def OnHome(self, event):
		#print 'Clicked OnHome'
		#Publisher().sendMessage( "go_home", (self.pos) )
		send("go_home", (self.pos))
	def OnUp(self, event):
		#print 'Clicked OnBack'
		#Publisher().sendMessage( "go_up", (self.pos) )
		send( "go_up", (self.pos))

	def onForceSearch(self, evt):
		(position, fltr)=evt.data
		if position!=self.pos:
			print '----------------onForceSearch', position, fltr
			self.filter.SetValue(fltr)
		

		
	def getFilter(self,parent,list):
		#self.treeMap[ttitle] = {}
		self.searchItems={}
		#print _tP
		#tree = TacoTree(parent,images,_tP)
		filter = wx.SearchCtrl(parent, style=wx.TE_PROCESS_ENTER)
		filter.ShowCancelButton(True)
		#filter.Bind(wx.EVT_TEXT, self.RecreateTree)
		self.gen_bind(wx.EVT_TEXT,filter, self.RecreateList,(list,filter))
		#filter.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnSearchCancelBtn)
		self.gen_bind(wx.EVT_SEARCHCTRL_CANCEL_BTN,filter, self.OnSearchCancelBtn,(list, filter))
		self.gen_bind(wx.EVT_TEXT_ENTER,filter, self.OnSearch,(list, filter))
		searchMenu = wx.Menu()
		item = searchMenu.AppendRadioItem(-1, "Current")
		#self.Bind(wx.EVT_MENU, self.OnSearchMenu, item)
		self.gen_bind(wx.EVT_MENU, item,self.OnSearchMenu,(list, filter))
		item = searchMenu.AppendRadioItem(-1, "Both")
		#self.Bind(wx.EVT_MENU, self.OnSearchMenu, item)
		self.gen_bind(wx.EVT_MENU, item,self.OnSearchMenu,(list, filter))
		filter.SetMenu(searchMenu)		


		#self.RecreateTree(None, (tree, filter,ttitle,_tP,_tL))
		#tree.SetExpansionState(self.expansionState)
		#tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded)
		#self.gen_bind(wx.EVT_TREE_ITEM_EXPANDED, tree, self.OnItemExpanded,(tree))
		#tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
		#self.gen_bind(wx.EVT_TREE_ITEM_COLLAPSED,tree, self.OnItemCollapsed,(tree))
		#tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
		#self.gen_bind(wx.EVT_TREE_SEL_CHANGED, tree,self.OnSelChanged,(tree,filter,ttitle))
		#tree.Bind(wx.EVT_LEFT_DOWN, self.OnTreeLeftDown)
		#self.gen_bind(wx.EVT_LEFT_DOWN, tree,self.OnTreeLeftDown, (ttitle) )
		#self.BuildMenuBar(_tL,ttitle)
		return filter
	def gen_bind(self, type, instance, handler, *args, **kwargs):
		self.Bind(type, lambda event: handler(event, *args, **kwargs), instance)	
	def OnSearchMenu(self, event, tparams):
		(tree, filter)=tparams
		# Catch the search type (name or content)
		searchMenu = filter.GetMenu().GetMenuItems()
		fullSearch = searchMenu[1].IsChecked()
		fltr=filter.GetValue()
		if 1:
			if fullSearch:
				print 'OnSearchMenu/fullSearch'
				#Publisher().sendMessage( "force_search", (self.pos,fltr) )
				send("force_search", (self.pos,fltr))
				self.OnSearch(None,tparams)
			else:
				self.RecreateList(None,tparams)

		#self.RecreateList(None,tparams)
			
	def OnSearch(self, event, tf):
		#search in every list
		
		(list, filter) = tf
		fltr = filter.GetValue()
		print 'OnSearch',fltr, self.searchItems
		self.filter_history[list.current_list]=fltr
		searchItems=self.searchItems
		if not fltr:
			self.RecreateList(None,(list, filter))
			return

		wx.BeginBusyCursor()		
	
		#searchItems=[item for item in list.data.values() if fltr.lower() in str(item[0]).lower()]
	
		self.RecreateList(None,(list, filter)) 
		wx.EndBusyCursor()
		 

	def OnSearchCancelBtn(self, event,tf):
		(list, filter) = tf
		self.filter.SetValue('')
		self.filter_history[list.current_list]=''
		self.OnSearch(event,tf)
		
	def setPanel(self):
		self.list =self.getTree(self.leftPanel[ttitle],ttitle,_tacoPngs,_treeList,xml_projRootLoc)
		self.filter[ttitle] =self.getFilter(self.leftPanel[ttitle],self.tree[ttitle],ttitle,_tacoPngs,_treeList)
		self.RecreateTree(None, (self.tree[ttitle], self.filter[ttitle],ttitle,_tacoPngs,_treeList,'%s/%s' % (user,db)))
		leftBox = wx.BoxSizer(wx.VERTICAL)
		leftBox.Add(self.tree[ttitle], 1, wx.EXPAND)
		#leftBox.Add(wx.StaticText(leftPanel, label = "Filter Files:"), 0, wx.TOP|wx.LEFT, 5)
		leftBox.Add(self.filter[ttitle], 0, wx.EXPAND|wx.ALL, 5)
		if 'wxMac' in wx.PlatformInfo:
			leftBox.Add((5,5))  # Make sure there is room for the focus ring
		self.leftPanel[ttitle].SetSizer(leftBox)
	def RecreateList(self, evt=None, tf=None):
		# Catch the search type (name or content)
		cl =self.list.current_list
		print '############# in RecreateList', self.pos,'cl:', cl
		(list, filter) = tf
		fltr = filter.GetValue()
		print fltr
		btns=self.list.nav_list[self.list.current_list]['hot_keys']
		#Publisher().sendMessage( "set_buttons", (self.list.pos,btns) )
		send("set_buttons", (self.list.pos,btns) )
		if 1:
			searchMenu = filter.GetMenu().GetMenuItems()
			fullSearch = searchMenu[1].IsChecked()
			searchItems=self.searchItems
			if evt:
				if fullSearch:
					print 'RecreateList/fullSearch'
					#Publisher().sendMessage( "force_search", (self.pos,fltr) )
					send("force_search", (self.pos,fltr) )
					# Do not`scan all the demo files for every char
					# the user input, use wx.EVT_TEXT_ENTER instead
					#return

			#expansionState = list.GetExpansionState()

			current = None
			#print(dir(list))
			#print list.GetSelectedItemCount()
			if 0:
				item = list.GetSelection()
				if item:
					prnt = list.GetItemParent(item)
					if prnt:
						current = (list.GetItemText(item),
								   list.GetItemText(prnt))
						
			#list.Freeze()
			
			#self.root = list.AddRoot(activeProjName)
			#list.SetItemImage(self.root, 0)
			#list.SetItemPyData(self.root, 0)

			treeFont = list.GetFont()
			catFont = list.GetFont()

			# The old native treectrl on MSW has a bug where it doesn't
			# draw all of the text for an item if the font is larger than
			# the default.  It seems to be clipping the item's label as if
			# it was the size of the same label in the default font.
			if 'wxMSW' not in wx.PlatformInfo or wx.GetApp().GetComCtl32Version() >= 600:
				treeFont.SetPointSize(treeFont.GetPointSize()+2)
				treeFont.SetWeight(wx.BOLD)
				catFont.SetWeight(wx.BOLD)
				
			#list.SetItemFont(self.root, treeFont)
			
			firstChild = None
			selectItem = None
			
			count = 0
			
			#for key, items in list.data.items():
			#items=list.data.values()
			if fltr:
				 self.filter_history[list.current_list]=fltr
				 #print 'fltr', fltr, 'self.filter_history[list.current_list]=', self.filter_history[list.current_list]
			#print list.current_list
			#print self.filter_history
			
			#for item in items:
				#print '------'.join(item)
				#print str(item).replace("L,'"," ").replace(","," ").replace("'","").replace(")","").replace("(","").lower()
				#if fltr.lower() in str(item).lower():
				#	print item 
			#pprint(items)
			#sys.exit(1)
			item_mask='[%s]'
			#print '|||||||||||||||||||||||||||',cl, self.list.nav_list.keys().pop() 
			nav_keys=self.list.nav_list.keys()
			#print nav_keys
			zoomable=[]
			#if nav_keys.index(cl)==len(nav_keys)-2:
			#	item_mask='%s'
			if self.list.nav_list[cl].has_key('zoomable'):
				zoomable=self.list.nav_list[cl]['zoomable']
			if 1:
				count += 1
				if fltr:
					if 0 and fullSearch:
						items = searchItems[category]
					else:
						keys = [key for key,item in list.data[list.current_list].items() if fltr.lower() in str(item[0]).lower()]
				else:
					keys = [key for key,item in list.data[list.current_list].items()]
				if keys:
					#print keys
					j=0
					list.DeleteAllItems()
					#load favorites
					fav_path= self.getVarsToFavPath()
					relative_path= self.getVarsToPath()
					print fav_path
					fav_key='%d:%s' % (len(relative_path.split('/')),fav_path)
					#suffix='_favs%d%d' % self.pos
					gsuffix='gfavs%d%d' % self.pos
				
					gfavs=readFromCache('', gsuffix)
					check_favs=False
					favs={}
					if gfavs.has_key(fav_key):
						check_favs=True
						favs=gfavs[fav_key]
					keycolid=list.nav_list[list.current_list]['key_col_id']
					#print favs
					print keycolid
					#sys.exit(1)
					for key in keys:
						#(key,i) = val
						i= list.data[list.current_list][key]
						#print key,i
						#sys.exit(1)
						if  1:
							
							if zoomable:
								if i[1] in zoomable:
									index=list.InsertStringItem(sys.maxint, '[%s]' % i[0])
								else:
									index=list.InsertStringItem(sys.maxint,  i[0])
							else:
								index=list.InsertStringItem(sys.maxint, item_mask % i[0])
							for idx in range(1,len(i)):
								list.SetStringItem(index, idx, str(i[idx]))
							#list.SetStringItem(index, 2, str(i[2]))
							#list.SetStringItem(index, 3, str(i[3]))
							#self.SetStringItem(index, 4, str(i[4])) 				#time.strftime('%Y-%m-%d %H:%M', time.localtime(sec))
							

							list.SetItemData(index, key)
							#print favs
							#print favs.reverse()
							#pprint(dir(favs))
							#favs.remove(i[keycolid])
							##print favs
							#print '-------favs index ---------',favs.index(i[keycolid])
							if favs.has_key(i[keycolid]):
								item = list.GetItem(index)
								font = item.GetFont()
								font.SetWeight(wx.FONTWEIGHT_BOLD)
								item.SetFont(font)
								# This does the trick:
								list.SetItem(item)
							

							#if i[1] == 'xml':
							#print list._imgstart,list.img_offset
							imgs= self.list.nav_list[cl]['img'] 
							img_type_col_id= self.list.img_col
							img_type = i[img_type_col_id]
							img_name=None
							if imgs.has_key(img_type):
								img_name=imgs[img_type]
							else:
								img_name=imgs['default']
							#print img_name
							img_id=self.list.image_refs[img_name]
							list.img[key]=img_id
							list.SetItemImage(index, list.img[key])
							#print 'SetItemImage',index,key,list.img[key]
							if (j % 2) == 0:
								list._bg='#e6f1f5'
								list.SetItemBackgroundColour(index, list._bg)
							j += 1				
					if 0:
						child = list.AppendItem(self.root, category, image=count)
						list.SetItemFont(child, catFont)
						list.SetItemPyData(child, count)
						if not firstChild: firstChild = child
						for childItem in items:
							image = count
							if DoesModifiedExist(childItem):
								image = len(_tP)
							theDemo = list.AppendItem(child, childItem, image=image)
							list.SetItemPyData(theDemo, count)
							self.treeMap[ttitle][childItem] = theDemo
							#if current and (childItem, category) == current:
							#	selectItem = theDemo
							
						
			#list.Expand(self.root)
			#if firstChild:
			#	list.Expand(firstChild)
			#if fltr:
			#	list.ExpandAll()
			#elif expansionState:
			#	list.SetExpansionState(expansionState)
			if 0 and selectItem:
				self.skipLoad = True
				list.SelectItem(selectItem)
				self.skipLoad = False
			print 'list.Thaw()'
			#print (dir(list))
			print list.pos
			#if list.IsFrozen():
			#	list.Thaw()
			#list.Show()
			searchItems = {}		
			listmix.ColumnSorterMixin.__init__(self, self.list.GetColumnCount())
			#update location url
			#print '/'.join([l[:-4] for l in self.list.loc_url])
			out=''
			max_len=15
			dots=''
			nav_var_keys=self.list.nav_list['vars'].keys()[1:]
			for vloc in nav_var_keys:
				out =out +'/'				
				if 1:
					url_val=self.list.nav_list['vars'][vloc]
					if 0 and len(out)>30:
						if len(url_val)>max_len:
							dots='..'
						out =out+ url_val[:max_len] +dots #+' '+str(len(self.list.nav_list['vars'][l]))
						dots=''
					else:
						out =out+ url_val
				else:
					out =out+l[:-4]


			if not out:
				out =self.root_status
				#sys.exit(1)
			
			#print '#'*20
			#print out
			#print '#'*20			
			#pprint(self.hist_btn)
			#pprint(self.hist_btn.keys())
			#print(dir(self.locator))
			#self.locator.SetLabel(out)
			self.setUrlLocator()
			sb=self.status
			if not sb:
				sb=cl
				if not sb:
					sb='Douple click on pipeline file.'
			#Publisher().sendMessage( "update_status_bar", (sb,self.pos) ) 
			send( "update_status_bar", (sb,self.pos))
			
			self.updateCache()
	def add_nav_hist(self,  loc,path=None):
		#Usage:
		#self.add_nav_hist(self.getVarsToPath(),self.current_list)
		#always cut at current_hist_id
		if not path:
			path=self.getVarsToPath()
		#hist_id='%s:%s' % (loc,path)
		#if self.nav_hist.has_key(path):
		#	self.nav_hist.pop(path)
		self.nav_hist=self.nav_hist[:self.curr_hist_id+1]
		self.nav_hist.append((loc,path))
		print 'in add_nav_hist000000000000000', self.curr_hist_id, len(self.nav_hist)
		self.curr_hist_id=len(self.nav_hist)-1
		#pprint(self.nav_hist)
		#self.nav_hist[path]=loc
		if self.curr_hist_id>0:
			self.btn_back.Enable()
		self.btn_fwd.Disable()
		#print 'in add_nav_hist000000000000000', self.curr_hist_id
		
	def OnBackButton(self, event):
		#assuming self.curr_hist_id>0
		(loc_to,path_to)=self.nav_hist[self.curr_hist_id-1]
		self.curr_hist_id -=1
		print (loc_to,path_to)
		self.list.initVarsFromPath(path_to,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		print 'self.curr_hist_id', self.curr_hist_id
		if self.curr_hist_id==0:
			self.btn_back.Disable()
		self.btn_fwd.Enable()	
		
		if 0:
			idx=self.nav_hist.keys().index(relative_path)
			print relative_path,idx
			path_to=self.nav_hist.keys()[idx-1]
			loc_to=self.nav_hist[path_to]
			
			print (loc_to,path_to)
			self.list.initVarsFromPath(path_to,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			self.list.setCurrListName(loc_to, 'reset')		
			self.list.execList(loc_to)
			if idx==1:
				self.btn_back.Disable()
			self.btn_fwd.Enable()

	def OnBackButtonRightUp(self, event):
		print self.pos
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		print btn
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateBackMenu()

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._backMenu.SetOwnerHeight(btnSize.y)
		self._backMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)	
	def CreateBackMenu(self):

		if 1:
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._backMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			#(path, loc_to) = self.nav_hist[self.curr_hist_id]
			#relative_path=self.getVarsToPath()
			for id in range(len(self.nav_hist)):
				if id<self.curr_hist_id:
					tup=self.nav_hist[id]
					(loc_to, path)=tup
					#loc_to=self.hist_btn[path]
					itype=wx.ITEM_NORMAL
					if id==self.curr_hist_id:
						itype=wx.ITEM_CHECK
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
					#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if id==self.curr_hist_id:
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnBackMenu,(id,loc_to,path))		
	def OnBackMenu(self, event, params):
		(id,loc_to,path) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		#item_id=event.GetId()-21001
		#print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		#print  params
		#self.list.nav_list['vars'][loc]=item
		#list_to=
		print (loc_to,path)
		self.curr_hist_id=id
		self.list.initVarsFromPath(path,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		#self._popUpMenu.pop(loc)
		self.btn_fwd.Enable()	
		if self.curr_hist_id==0:
			self.btn_back.Disable()		
	def OnForwardButtonRightUp(self, event):
		print self.pos
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		print btn
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateForwardMenu()

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._fwdMenu.SetOwnerHeight(btnSize.y)
		self._fwdMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)		
	def CreateForwardMenu(self):

		if 1:
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._fwdMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			#(path, loc_to) = self.nav_hist[self.curr_hist_id]
			relative_path=self.getVarsToPath()
			for id in range(len(self.nav_hist)):
				if id>self.curr_hist_id:
					print id, self.curr_hist_id
					tup=self.nav_hist[id]
					(loc_to, path)=tup
					print id, self.curr_hist_id
					itype=wx.ITEM_NORMAL
					if id==self.curr_hist_id:

						itype=wx.ITEM_CHECK
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
					#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if path==relative_path:
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnForwardMenu,(id,loc_to, path))
	def OnForwardMenu(self, event, params):
		(id,loc_to, path) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		#item_id=event.GetId()-21001
		#print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		#print  params
		#self.list.nav_list['vars'][loc]=item
		#list_to=
		self.curr_hist_id=id
		print (loc_to,path)
		self.list.initVarsFromPath(path,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		#self._popUpMenu.pop(loc)
		self.btn_back.Enable()	
		if self.curr_hist_id==(len(self.nav_hist)-1):
			self.btn_fwd.Disable()
	def OnForwardButton(self, event):
		#assuming it's not the end of the list	
		(loc_to,path_to)=self.nav_hist[self.curr_hist_id+1]
		self.curr_hist_id +=1
		print (loc_to,path_to)
	
		self.list.initVarsFromPath(path_to,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		self.btn_back.Enable()	
		if self.curr_hist_id==len(self.nav_hist)-1:
			self.btn_fwd.Disable()
			
		if 0:
			relative_path=self.getVarsToPath()
			idx=self.nav_hist.keys().index(relative_path)
			print relative_path,idx
			path_to=self.nav_hist.keys()[idx+1]
			loc_to=self.nav_hist[path_to]
			self.list.initVarsFromPath(path_to,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			self.list.setCurrListName(loc_to, 'reset')		
			self.list.execList(loc_to)
			self.btn_back.Enable()	
			if idx+1==self.nav_hist-1:
				self.btn_fwd.Disable()
				
	def add_hist(self,  loc,path=None):
		if not path:
			path=self.getVarsToPath()	
		#if self.hist_btn.has_key(path):
		#	self.hist_btn.pop(path)
		self.hist_btn[path] = loc
	def OnHistButton(self, event,params):
		(loc)=params
		print (loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateHistMenu(loc)

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._histMenu.SetOwnerHeight(btnSize.y)
		self._histMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)		
	def OnFavButton(self, event,params):
		(loc)=params
		print (loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateFavMenu(loc)

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._favMenu.SetOwnerHeight(btnSize.y)
		self._favMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)	
	def CreateHistMenu(self,loc):

		if 1 or not self._popUpMenu.has_key(loc):
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._histMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			relative_path=self.getVarsToPath()
			for id in range(len(self.hist_btn)):
				path=self.hist_btn.keys()[id]
				loc_to=self.hist_btn[path]
				
				itype=wx.ITEM_NORMAL
				#print '>>>>>>>>>>>>>>',relative_path,path
				if relative_path==path:
					itype=wx.ITEM_CHECK
				menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
				#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
				pmenu.AppendItem(menuItem)				
				if relative_path==path:
					menuItem.Check(True)
					#subMenu.UpdateItem(menuItem)
					#print menuItem.IsChecked(), menuItem.IsCheckable()
					#menuItem.Enable(False)
				#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

				#print menuItem.isChecked()
				#print menuItem.IsChecked(), menuItem.IsChecked()
				#menuItem.Enable(True)
				#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
				#
				self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnHistMenu,(loc_to,path))
	def CreateFavMenu(self,loc):

		if 1 or not self._popUpMenu.has_key(loc):
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._favMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			gsuffix='gfavs%d%d' % self.pos
			gfavs=readFromCache('', gsuffix)	
			print 'gfavs:', gfavs
			gkeys=gfavs.keys()
			#gkeys=sorted(gkeys,key=lambda path: len(path.split('/'))) #reverse=True
			gkeys.sort()
			pprint(gkeys)
			#sys.exit(1)
			first=True
			for path in gkeys:	
				items=gfavs[path]
				if not first:
					pmenu.AppendSeparator()
				loc_id=p=path.split(':')[0]
				#loc=self.list.getListFromId(int(loc_id))
				p=path.split(':')[1][5:]
				if p:
					p='(%s)' %p
				ikeys=items.keys()
				ikeys.sort()
				for ikey in ikeys:
					val=items[ikey]
					print '--item--',ikey, val
					itype=wx.ITEM_NORMAL
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s %s' % (ikey, p), "", itype)
					pmenu.AppendItem(menuItem)
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnFavMenu,(loc_id,'%s/%s' %(val,ikey)))
				first=False
			if 0:
				for id in range(len(self.hist_btn)):
					path=self.hist_btn.keys()[id]
					loc_to=self.hist_btn[path]
					itype=wx.ITEM_NORMAL
					if id==(len(self.hist_btn)-1):
						itype=wx.ITEM_CHECK
					menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( path), "", itype)
					#print item[0], self.list.nav_list['vars'][loc],  item[0]==self.list.nav_list['vars'][loc]
					pmenu.AppendItem(menuItem)				
					if id==(len(self.hist_btn)-1):
						menuItem.Check(True)
						#subMenu.UpdateItem(menuItem)
						#print menuItem.IsChecked(), menuItem.IsCheckable()
						#menuItem.Enable(False)
					#pmenu.AppendRadioItem(wx.ID_ANY,menuItem)

					#print menuItem.isChecked()
					#print menuItem.IsChecked(), menuItem.IsChecked()
					#menuItem.Enable(True)
					#self.Bind(FM.EVT_FLAT_MENU_SELECTED, self.OnMenu, id=20001+key)
					#
					self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnHistMenu,(loc_to,path))
	def OnHistMenu(self, event, params):
		(loc_to,path) = params
		#print event.GetEventObject()
		#print(dir(event.GetEventObject()))
		#item_id=event.GetId()-21001
		#print item_id
		#self.list.nav_list['vars'][loc]=
		#print self.list., self.list.data[loc][item_id]
		#print  params
		#self.list.nav_list['vars'][loc]=item
		#list_to=
		print (loc_to,path)
		vars=self.list.getVarsFromPath(path,'/')[1:]
		self.list.setNavlist()
		if len(vars)>2:
			conn=self.list.getConnectType(path)
			print conn
			print 'before',self.list.nav_list.keys()
			self.list.extendNavlist(conn)
			print 'after',self.list.nav_list.keys()
				
		self.list.initVarsFromPath(path,'/')
		#self.list.clearListVars(loc_to)
		#print '11111111111111111 cleared to ',loc_to
		self.list.setCurrListName(loc_to, 'reset')		
		self.list.execList(loc_to)
		self.add_nav_hist(loc_to)
		#self._popUpMenu.pop(loc)	
	def OnFavMenu0(self, event, params):
		(loc_to,path) = params
		#print params
		if 1:
			#print event.GetEventObject()
			#print(dir(event.GetEventObject()))
			#item_id=event.GetId()-21001
			#print item_id
			#self.list.nav_list['vars'][loc]=
			#print self.list., self.list.data[loc][item_id]
			#print  params
			#self.list.nav_list['vars'][loc]=item
			#list_to=
			print (loc_to,path)
			self.list.initVarsFromPath(path,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			self.list.setCurrListName(loc_to, 'reset')		
			self.list.execList(loc_to)
			self.add_nav_hist(loc_to)
		#self._popUpMenu.pop(loc)	
	def OnFavMenu(self, event, params):
		(loc_id,path) = params
		#print params
		if 1:
			#print event.GetEventObject()
			#print(dir(event.GetEventObject()))
			#item_id=event.GetId()-21001
			#print item_id
			#self.list.nav_list['vars'][loc]=
			#print self.list., self.list.data[loc][item_id]
			#print  params
			#self.list.nav_list['vars'][loc]=item
			#list_to=
			print (loc_id,path)
			vars=self.list.getVarsFromPath(path,'/')[1:]
			print 'new vars:'
			print vars
			#init list
			self.list.setNavlist()
			if len(vars)>2:
				conn=self.list.getConnectType(path)
				print conn
				print 'before',self.list.nav_list.keys()
				self.list.extendNavlist(conn)
				print 'after',self.list.nav_list.keys()
				#sys.exit(1)
			self.list.initVarsFromPath(path,'/')
			#self.list.clearListVars(loc_to)
			#print '11111111111111111 cleared to ',loc_to
			loc_to=self.list.getListFromId(int(loc_id))
			self.list.setCurrListName(loc_to, 'reset')	
			print loc_to, loc_id
			print self.list.nav_list.keys()	
			print vars
			#sys.exit(1)
			self.list.execList(loc_to)
			self.add_nav_hist(loc_to)
		#self._popUpMenu.pop(loc)		
	def updateCache(self):
		relative_path='root'
		if update_cache:
			
			vars=self.list.nav_list['vars'].values()[1:]
			if len(vars)>0:
				relative_path='%s/%s'% (relative_path,'/'.join(vars))
				#print '#'*20,  
				#os.path.join(self.list.nav_list['vars'].values()[1:])
			#else:
			#	relative_path='%s/root' % relative_path
			writeToCache(relative_path, self.list.data[self.list.current_list])	
	#def updateCache(self)
	def SortListItems(self, col=-1, ascending=1):
		pass
	def GetSelection(self):
		row = -1 
		selected_items = [] 
		while 1: 
			row = self.GetNextItem(row, wxLIST_NEXT_ALL, wxLIST_STATE_SELECTED) 
			if row==-1: break 
		selected_items.append(row) 
	def OnUseNative(self, event):
		wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", not event.IsChecked())
		wx.GetApp().GetTopWindow().LoadDemo("ListCtrl")

	def PopulateList(self):
		if 0:
			# for normal, simple columns, you can add them like this:
			self.list.InsertColumn(0, "Artist")
			self.list.InsertColumn(1, "Title", wx.LIST_FORMAT_RIGHT)
			self.list.InsertColumn(2, "Genre")
		else:
			# but since we want images on the column header we have to do it the hard way:
			info = wx.ListItem()
			info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
			info.m_image = -1
			info.m_format = 0
			info.m_text = "Artist"
			self.list.InsertColumnInfo(0, info)

			info.m_format = wx.LIST_FORMAT_RIGHT
			info.m_text = "Title"
			self.list.InsertColumnInfo(1, info)

			info.m_format = 0
			info.m_text = "Genre"
			self.list.InsertColumnInfo(2, info)

		items = musicdata.items()
		for key, data in items:
			index = self.list.InsertImageStringItem(sys.maxint, data[0], self.idx1)
			self.list.SetStringItem(index, 1, data[1])
			self.list.SetStringItem(index, 2, data[2])
			self.list.SetItemData(index, key)

		self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(2, 100)

		# show how to select an item
		#self.list.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

		# show how to change the colour of a couple items
		item = self.list.GetItem(1)
		item.SetTextColour(wx.BLUE)
		self.list.SetItem(item)
		item = self.list.GetItem(4)
		item.SetTextColour(wx.RED)
		self.list.SetItem(item)

		self.currentItem = 0


	# Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
	def GetListCtrl(self):
		return self.list

	# Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
	def GetSortImages(self):
		return (self.sm_dn, self.sm_up)


	def OnRightDown(self, event):
		x = event.GetX()
		y = event.GetY()
		#self.log.WriteText("x, y = %s\n" % str((x, y)))
		item, flags = self.list.HitTest((x, y))

		if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
			self.list.Select(item)

		event.Skip()


	def getColumnText(self, index, col):
		item = self.list.GetItem(index, col)
		return item.GetText()

		

	def OnItemSelected1(self, event):
		##print event.GetItem().GetTextColour()
		self.currentItem = event.m_itemIndex
		if 0:
			self.log.WriteText("OnItemSelected: %s, %s, %s, %s\n" %
							   (self.currentItem,
								self.list.GetItemText(self.currentItem),
								self.getColumnText(self.currentItem, 1),
								self.getColumnText(self.currentItem, 2)))

		if self.currentItem == 10:
			#self.log.WriteText("OnItemSelected: Veto'd selection\n")
			#event.Veto()  # doesn't work
			# this does
			self.list.SetItemState(10, 0, wx.LIST_STATE_SELECTED)

		event.Skip()


	def OnItemDeselected1(self, evt):
		item = evt.GetItem()
		print "OnItemDeselected: %d" % evt.m_itemIndex
		#self.log.WriteText("OnItemDeselected: %d" % evt.m_itemIndex)

		# Show how to reselect something we don't want deselected
		if evt.m_itemIndex == 11:
			wx.CallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)


	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
		print "OnItemActivated: %s\nTopItem: %s" % (self.list.GetItemText(self.currentItem), self.list.GetTopItem())
		#self.log.WriteText("OnItemActivated: %s\nTopItem: %s" %
		#                   (self.list.GetItemText(self.currentItem), self.list.GetTopItem()))

	def OnBeginEdit(self, event):
		print "OnBeginEdit"
		#self.log.WriteText("OnBeginEdit")
		event.Allow()

	def OnItemDelete(self, event):
		print "OnItemDelete\n"
		#self.log.WriteText("OnItemDelete\n")

	def OnColClick(self, event):
		print "OnColClick: %d\n" % event.GetColumn()
		#self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
		#print(dir(self.list))
		#if self.list.idx_first != None:
		#	self.list.DeleteItem(self.list.idx_first)

		event.Skip()
	def OnSortOrderChanged(self):
		#print "OnSortOrderChanged!"
		#self._colSortFlag[self._col]=int(not self._colSortFlag[self._col])
		#pprint(dir(self.list))
		for j in range(len(self.list.data[self.list.current_list])):
			if (j % 2) == 0:
				#self.list._bg='#e6f1f5'
				self.list.SetItemBackgroundColour(j, self.list._bg)
			else:
				self.list.SetItemBackgroundColour(j, '#FFFFFF')
			#j += 1
				
		#self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
		#event.Skip()		

	def OnColRightClick(self, event):
		item = self.list.GetColumn(event.GetColumn())
		print "OnColRightClick: %d %s\n" % (event.GetColumn(), (item.GetText(), item.GetAlign(), item.GetWidth(), item.GetImage()))
		#self.log.WriteText("OnColRightClick: %d %s\n" %
		#                   (event.GetColumn(), (item.GetText(), item.GetAlign(),
		#                                        item.GetWidth(), item.GetImage())))

	def OnColBeginDrag(self, event):
		print "OnColBeginDrag\n"
		#self.log.WriteText("OnColBeginDrag\n")
		## Show how to not allow a column to be resized
		#if event.GetColumn() == 0:
		#    event.Veto()


	def OnColDragging(self, event):
		print "OnColDragging\n"
		#self.log.WriteText("OnColDragging\n")

	def OnColEndDrag(self, event):
		print "OnColEndDrag\n"
		#self.log.WriteText("OnColEndDrag\n")

	def OnDoubleClick(self, event):
		print "OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem)
		#self.log.WriteText("OnDoubleClick item %s\n" % self.list.GetItemText(self.currentItem))
		event.Skip()
	def getSide(self,pos):
		side =None
		id ='%d%d' % pos 
		if self.sides.has_key(id):
			side=self.sides[id]
		return side
	def OnRightClick(self, event):
		print "OnRightClick %s\n" % self.list.GetItemText(self.currentItem),self.list.GetSelectedItemCount()
		#self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))
		#print(dir(self.list))
		#print GetSelectedItemCount
		# only do this part the first time so the events are only bound once
		disabled_favs=False
		if self.list.GetSelectedItemCount()==0:
			disabled_favs =True
		self.show_in={}
		if 1:
			menu = wx.Menu()
			if 1: #not hasattr(self, "add_to_favorites"):
				self.add_to_favorites = wx.NewId()
				self.remove_from_favorites = wx.NewId()
				for sid in ['%d%d' % pos for pos in self.panel_pos if pos!=self.pos ]:
					print '---ii--',sid, 20100+int(sid)
					self.show_in[sid]=20100+int(sid)
				self.Bind(wx.EVT_MENU, self.OnAddToFavorites, id=self.add_to_favorites)
				self.Bind(wx.EVT_MENU, self.OnRemoveFromFavorites, id=self.remove_from_favorites)
				for sid in ['%d%d' % pos for pos in self.panel_pos if pos!=self.pos ]:
					#self.gen_bind(wx.EVT_MENU,self, self.TimerHandler_pos,(self.panel_pos[0]))
					#self.gen_bind(wx.EVT_MENU,menu, self.OnShowIn,(sid),id=self.show_in[sid])
					self.Bind(wx.EVT_MENU, self.OnShowIn, id=self.show_in[sid])
					self.Bind(wx.EVT_MENU, self.OnShowIn, id=self.show_in[sid]+10000)
					#self.Bind(wx.EVT_MENU, self.OnShowIn, id=self.show_in[sid])
					#menuItem = wx.MenuItem(pmenu, wx.ID_ANY, '%s' % ( label), "", itype)
					#self.gen_bind(wx.EVT_MENU,self.show_in[sid], self.OnShowIn ,(id))	
				if 0:
					self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
					self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
					self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
					self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
					self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

			# make a menu
			
			# add some items
			menu.Append(self.add_to_favorites, "Add to Favorites.")
			menu.Append(self.remove_from_favorites, "Remove from Favorites.")
			if self.list.current_list in ('TableList','PartitionList','SubPartitionList'):
				gather_stats=wx.NewId()
				menu.Append(gather_stats, "Gather stats.")
				menu.Enable(gather_stats, False)
				copy_ddl=wx.NewId()
				menu.Append(copy_ddl, "Copy DDL.")
				menu.Enable(copy_ddl, False)
				copy_name=wx.NewId()
				menu.Append(copy_name, "Copy name.")
				menu.Enable(copy_name, False)
				
			for pos in [ pos for pos in self.panel_pos if pos!=self.pos ]:
				side= self.getSide(pos)
				sid= '%d%d' % pos 
				print sid, side, self.panel_pos
				if side:
					menu.Append(self.show_in[sid], "Mirror in %s" % side)
					list=self.getListFromPos(pos)
					pos_connect='test_CSMARTBSER_QA' #'list.parent.getVarsToPath().split('/')[2]
					#db_path=self.getVarsToPath().split('/')[4:]
					#in_url="%s/%s" % (pos_connect, '/'.join(db_path))
					#menu.Append(self.show_in[sid]+10000, "Mirror in %s (%s)" % (side,in_url))
			if disabled_favs:
				menu.Enable(self.add_to_favorites, False)
				menu.Enable(self.remove_from_favorites, False)
			if 0:
				menu.Append(self.popupID1, "FindItem tests")
				menu.Append(self.popupID2, "Iterate Selected")
				menu.Append(self.popupID3, "ClearAll and repopulate")
				menu.Append(self.popupID4, "DeleteAllItems")
				menu.Append(self.popupID5, "GetItem")
				menu.Append(self.popupID6, "Edit")

			# Popup the menu.  If an item is selected then its handler
			# will be called before PopupMenu returns.
			#pprint(dir(menu))
			self.PopupMenu(menu)
			
			menu.Destroy()
			
	def OnShowIn(self, event):
		print 'OnShowIn'
		#print event.GetEventObject().GetLabel(event.GetId())
		#print event.GetId()
		#sys.exit(1)
		#print str(event.GetId()-100)
		#print event.GetId()-20000
		(ignore,row,col) = str(event.GetId()-20000)
		pos_to= (int(row),int(col))
		#print pos_to
		#Publisher().sendMessage( "mirror_list", (self.list.current_list, self.getVarsToPath(), pos_to, self.getSide(self.pos)) )
		send("mirror_list", (self.list.current_list, self.getVarsToPath(), pos_to, self.getSide(self.pos)) )
		
	def OnRightClick_00(self, event):
		print "OnRightClick %s\n" % self.list.GetItemText(self.currentItem)
		#self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))

		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()
			self.popupID3 = wx.NewId()
			self.popupID4 = wx.NewId()
			self.popupID5 = wx.NewId()
			self.popupID6 = wx.NewId()

			self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
			self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
			self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
			self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
			self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)

		# make a menu
		menu = wx.Menu()
		# add some items
		menu.Append(self.popupID1, "FindItem tests")
		menu.Append(self.popupID2, "Iterate Selected")
		menu.Append(self.popupID3, "ClearAll and repopulate")
		menu.Append(self.popupID4, "DeleteAllItems")
		menu.Append(self.popupID5, "GetItem")
		menu.Append(self.popupID6, "Edit")

		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(menu)
		menu.Destroy()

	def OnAddToFavorites(self, event):
		print 'OnAddToFavorites'
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.list.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			item = self.list.GetItem(index)
			font = item.GetFont()
			font.SetWeight(wx.FONTWEIGHT_BOLD)
			item.SetFont(font)
			# This does the trick:
			self.list.SetItem(item)

		print 'si',selected_items
		self.addToFavorites(selected_items)

	def OnRemoveFromFavorites(self, event):
		print 'OnRemoveFromFavorites'
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.list.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			item = self.list.GetItem(index)
			font = item.GetFont()
			font.SetWeight(wx.FONTWEIGHT_NORMAL)
			item.SetFont(font)
			# This does the trick:
			self.list.SetItem(item)

		print 'si',selected_items
		self.removeFromFavorites(selected_items)

		
	def getVarsToPath(self):
		relative_path='root'
		if 1 or update_cache:			
			vars=self.list.nav_list['vars'].values()[1:]
			if len(vars)>0:
				relative_path='%s/%s'% (relative_path,'/'.join(vars))
		return relative_path
	def getVarsToFavPath(self):
		fav_path='root'
		if 1 or update_cache:	
			if self.list.nav_list[self.list.current_list].has_key('fav_key_start'):
				fav_start_id=self.list.nav_list[self.list.current_list]['fav_key_start']
				print 'fav_start_id', fav_start_id
				fav_start_id +=1
				print self.list.nav_list['vars'].values()
				vars=self.list.nav_list['vars'].values()[fav_start_id:]
				print vars
				if len(vars)>0:
					fav_path='%s/%s'% (fav_path,'/'.join(vars))
			else:
				
				print 'self.list.nav_list[self.list.current_list] nas no fav_key_start'
				fav_path=None
		return fav_path		
	def addToFavorites(self, ids):	
		fav_path= self.getVarsToFavPath()
		relative_path= self.getVarsToPath()
		print fav_path
		if fav_path:
			#sys.exit(1)
			if 0:
				suffix='_favs%d%d' % self.pos
				favs=readFromCache(relative_path, suffix)
				#pprint (self.list.data)
				print 'old favs:', favs
				for id in ids:
					favs[self.list.data[self.list.current_list][id][0]]=1
				print favs
				writeToCache(relative_path, favs, suffix)
			gsuffix='gfavs%d%d' % self.pos
			gfavs=readFromCache('', gsuffix)	
			print 'old gfavs:', gfavs
			print 'relative_path:', relative_path
			fav_key='%d:%s' % (len(relative_path.split('/')),fav_path)
			if not gfavs.has_key(fav_key):
				gfavs[fav_key]={}
			
			#print '#'*40
			#print '#'*40
			#print ids			
			for id in ids:			
				#print id
				fkey=self.list.data[self.list.current_list][id][0]
				#print fkey
				gfavs[fav_key][self.list.data[self.list.current_list][id][0]]=relative_path
			#print 'new global favs:',gfavs
			writeToCache('', gfavs, gsuffix)		
		else:
			self.status='Cannot define favorites on column level.'
	def removeFromFavorites(self, ids):	
		relative_path= self.getVarsToPath()
		fav_path= self.getVarsToFavPath()
		print fav_path
		if 0:
			suffix='_favs%d%d' % self.pos
			favs=readFromCache(relative_path, suffix)
			#pprint (self.list.data)
			print 'old favs:', favs
			for id in ids:
				print 'removing:', self.list.data[self.list.current_list][id][0]
				if favs.has_key(self.list.data[self.list.current_list][id][0]):
					favs.pop(self.list.data[self.list.current_list][id][0])
			print favs
			writeToCache(relative_path, favs, suffix)
		gsuffix='gfavs%d%d' % self.pos
		gfavs=readFromCache('', gsuffix)	
		print 'old gfavs:', gfavs
		#print ids
		#for key, items in gfavs.items():			
			#print key,relative_path
			#print items
		fav_key='%d:%s' % (len(relative_path.split('/')),fav_path)
		if gfavs.has_key(fav_key):
			#pprint(dir(gfavs[ relative_path]))
			for id in ids:
				#print id,  self.list.data[self.list.current_list][id][0]
				#print gfavs[ relative_path].index(self.list.data[self.list.current_list][id][0])
				print 'before', gfavs[fav_key]
				pop_val=self.list.data[self.list.current_list][id][0]
				if gfavs[fav_key].has_key(pop_val):
					gfavs[fav_key].pop(pop_val)
				print 'after', gfavs[fav_key]
			#gfavs[relative_path].append(self.list.data[self.list.current_list][id][0])
			#print 'new global favs:',gfavs
			writeToCache('', gfavs, gsuffix)		
		
		
	def OnPopupTwo(self, event):
		#self.log.WriteText("Selected items:\n")
		index = self.list.GetFirstSelected()

		while index != -1:
			print "      %s: %s\n" % (self.list.GetItemText(index), self.getColumnText(index, 1))
			#self.log.WriteText("      %s: %s\n" % (self.list.GetItemText(index), self.getColumnText(index, 1)))
			index = self.list.GetNextSelected(index)

	def OnPopupThree(self, event):
		print "Popup three\n"
		#self.log.WriteText("Popup three\n")
		self.list.ClearAll()
		wx.CallAfter(self.PopulateList)

	def OnPopupFour(self, event):
		self.list.DeleteAllItems()

	def OnPopupFive(self, event):
		item = self.list.GetItem(self.currentItem)
		print item.m_text, item.m_itemId, self.list.GetItemData(self.currentItem)

	def OnPopupSix(self, event):
		self.list.EditLabel(self.currentItem)	
		

		
class DragList(wx.ListCtrl):
	def __init__(self, splitter, parent,  id,pos):
		wx.ListCtrl.__init__(self, splitter, id, style=
										wx.LC_REPORT
										)

		self.parent=parent
		self.images = [ 'bmp_source/arrow_sans_up_16.png', 'bmp_source/arrow_sans_down_16.png','bmp_source/arrow_sans_up_16.png', \
		'bmp_source/Right_Arrow_16.png', 'bmp_source/Left_Arrow_16.png', 'bmp_source/folder_16.png'  \
		 , 'bmp_source/config_16.png','bmp_source/database-sql_16.png', 'bmp_source/database_share_16.png', \
		 'bmp_source/database_connect_16.png','bmp_source/user_16.png','bmp_source/database_table_16.png', \
		'bmp_source/table_select_column_16.png','bmp_source/database_red_16.png',
		'bmp_source/database_green_16.png',
		'bmp_source/database_blue_16.png',
		'bmp_source/database_black_16.png','bmp_source/file_16.png',]
		self.image_refs={}
		self._bg='#e6f1f5'
		self._imgstart=3
		self.img_offset=0
		self.img_col = 1
		self._imgid=self._imgstart+1
		self.data={}
		self.img={}
		self.current_list=None
		self.connect_type=None
		self.pos=pos
		self.db= OracleDb(self,pos)
		EVT_SIGNAL(self, self.relaySignal)
		self.file= FileDir(pos)
		self.il = wx.ImageList(16, 16)
		#self.sm_up = self.il.Add(images.SmallUpArrow.GetBitmap())
		#self.sm_dn = self.il.Add(images.SmallDnArrow.GetBitmap())		
		for i in range(len(self.images)):
			img=self.images[i]
			self.il.Add(wx.Bitmap(img))
			self.image_refs[img]=i
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)		
		pprint(self.image_refs)
		#sys.exit(1)
		#self.setColumnList(('MRR_BI','MRR_ETL_USER','CUBE_DATA_20130903144531_AB'))
		self.Bind(wx.EVT_LIST_BEGIN_DRAG, self._startDrag)

		dt = ListDrop(self, self.pos)
		self.SetDropTarget(dt)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._onEnter)
		#self.
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._onSelect)
		#self.nav_list=OrderedDict()
		self.setNavlist()
		#self.loc_url=[]	
		
		#
		#self.setFocus(0)
		#self.loc_url.append(self.GetSelected())
		#self.loc_url.append(self.Get);
		#Publisher().sendMessage( "update_location", ((self.parent.row, self.parent.pos),('forward','_CONFIG_')) )
		#self.parent.itemDataMap=self.data
		#listmix.ColumnSorterMixin.__init__(self.parent, 4)
		#Publisher().subscribe(self.GoHome, "go_home")		
		#Publisher().subscribe(self.GoUp, "go_up")
		#Publisher().subscribe(self.OnClearDrugStart, "clear_drug_start")
		#Publisher().subscribe(self.OnRefreshList, "refresh_list")
		#Publisher().subscribe(self.onSetEnvList,'set_env_list')
		#Publisher().subscribe(self.onSetOwnerList,'set_owner_list')
		sub(self.__GoHome, "go_home")
		sub(self.__GoUp, "go_up")
		sub(self.OnClearDrugStart, "clear_drug_start")
		sub(self.OnRefreshList, "refresh_list")
		sub(self.__onSetEnvList,'set_env_list')
		sub(self.onSetOwnerList,'set_owner_list')
		#Publisher().subscribe(self.onDbEvent, "db_thread_event")
		#pprint(self.nav_list.keys())
		#sys.exit(1)
		self.Bind(wx.EVT_SET_FOCUS, self.onFocus)  	
		self.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus) 
		self.buttons_set=False
	def relaySignal(self, msg):
		"""
		Receives data from thread and updates the display
		"""
		print  msg.data
		print  msg.signal
		send(msg.signal,msg.data)		
	def onFocus(self, event):
		#print 'got Focus list',self.pos
		#print self.current_list
		#event.skip()
		self.buttons_set=False
	def onKillFocus(self, event):
		#print 'lost Focus list', self.pos	
		#print self.current_list
		#event.skip()	
		self.buttons_set=True
	def setNavlist(self):
		self.connect_type=None
		self.nav_list=OrderedDict()
		self.nav_list['ConfigList']={'code':"self.setConfigList(('configDirLoc',))", 'up':'', 'forward':'EnvironmentList', \
							'img':{'config':'bmp_source/config_16.png', 'default':'bmp_source/config_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':0, \
							'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}
		self.nav_list['EnvironmentList']={'code':"self.setEnvironmentList(('configDirLoc','ConfigList',))", 'up':'ConfigList', 'forward':'ConnectList', \
							'img':{'default':'bmp_source/database_green_16.png', 'DEV':'bmp_source/database_green_16.png','PROD':'bmp_source/database_red_16.png', \
							'UAT':'bmp_source/database_blue_16.png','QA':'bmp_source/database_black_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':0, \
							'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}		
		self.nav_list['ConnectList']={'code':"self.setConnectList(('ConfigList','EnvironmentList',))", 'up':'EnvironmentList', 'forward':'OwnerList', \
							'img':{'db_connect':'bmp_source/database_connect_16.png','host_connect':'bmp_source/database_connect_16.png', 'default':'bmp_source/database_connect_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':0, \
							'hot_keys':{'F3':'New','F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':'Delete'}}
		self.root_list='ConfigList'
		
		#print dir(self.nav_list)
		#print list(self.nav_list.iterkeys())
		#print self.nav_list.keys()
		#sys.exit(1)
		self.nav_list['vars']=OrderedDict()
		self.nav_list['vars']['configDirLoc'] = configDirLoc
		self.draggable_lists=[]
		self.droppable_lists={}
		#table to table data copy
		#self.droppable_lists['TableList']=('TableList') #,'ColumnList'
		#fs to db upload
		self.droppable_lists['LeafDirList']=('ColumnList') #'TableList',
		self.droppable_lists['Level1DirList']=('ColumnList')
		self.droppable_lists['RootDirList']=('ColumnList')			
		#fs to fs file copy
		self.droppable_lists['LeafDirList']=('LeafDirList','RootDirList','Level1DirList') #'TableList',
		self.droppable_lists['RootDirList']=('LeafDirList','RootDirList','Level1DirList') #'TableList',
		self.droppable_lists['Level1DirList']=('LeafDirList','RootDirList','Level1DirList') #'TableList',
		# db to fs data spool
		self.droppable_lists['TableList']=('TableList','LeafDirList','RootDirList','Level1DirList') #,'ColumnList'
		self.droppable_lists['PartitionList']=('PartitionList','LeafDirList','RootDirList','Level1DirList') #,'ColumnList'
		self.droppable_lists['SubPartitionList']=('SubPartitionList','LeafDirList','RootDirList','Level1DirList') #,'ColumnList'
		self.droppable_lists['ColumnList']=('TableList') #, 'PartitionList','SubPartitionList','ColumnList','ColumnList','LeafDirList','RootDirList','Level1DirList'
		
	def extendNavlist(self,type=None):
		vars=self.nav_list['vars']
		self.nav_list.pop('vars')
		
		if type=='db_connect':
			self.nav_list['ConnectList'][ 'forward'] ='OwnerList'
			if 0:
				self.nav_list['DatabaseList']={'code':"self.setDatabaseList(('ConnectList',))", 'up':'ConnectList', 'forward':'OwnerList', \
									'img':{'database':'bmp_source/database-sql_16.png', 'default':'bmp_source/database-sql_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2, \
									'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}
			self.nav_list['OwnerList']={'code':"self.setOwnerList(('ConnectList',))", 'up':'ConnectList', 'forward':'TableList', \
								'img':{'owner':'bmp_source/user_16.png', 'default':'bmp_source/user_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2, \
								'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}
			self.nav_list['TableList']=	{'code':"self.setTableList(('ConnectList','OwnerList',))", 'up':'OwnerList', 'forward':'PartitionList', \
								'img':{'table':'bmp_source/database_table_16.png', 'default':'bmp_source/database_table_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2, \
								'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}
			self.nav_list['PartitionList']=	{'code':"self.setPartitionList(('ConnectList','OwnerList','TableList',))", 'up':'TableList', 'forward':'SubPartitionList', \
								'img':{'table':'bmp_source/database_table_16.png', 'default':'bmp_source/database_table_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2, \
								'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}
			self.nav_list['SubPartitionList']=	{'code':"self.setSubPartitionList(('ConnectList','OwnerList','TableList','PartitionList',))", 'up':'PartitionList', 'forward':'ColumnList', \
								'img':{'table':'bmp_source/database_table_16.png', 'default':'bmp_source/database_table_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2, \
								'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}
			self.nav_list['ColumnList']={'code':"self.setColumnList(('ConnectList','OwnerList','TableList',))", 'up':'SubPartitionList', 'forward':'', \
								'img':{'column':'bmp_source/table_select_column_16.png', 'default':'bmp_source/table_select_column_16.png'}, 'update_cache':update_cache, 'key_col_id':0,'zoomable':('dummy'), \
								'hot_keys':{'F3':dBtn,'F4':dBtn,'F5':dBtn,'F6':dBtn,'F7':dBtn,'F8':dBtn,'F9':dBtn}}	
			self.draggable_lists=('TableList','PartitionList','SubPartitionList','ColumnList')
			
			#[from]=(to)
				
		if type=='host_connect':
			self.nav_list['ConnectList'][ 'forward'] ='RootDirList'
			self.nav_list['RootDirList']={'code':"self.setRootDirList(('ConnectList',))", 'up':'ConnectList', 'forward':'Level1DirList', \
								'img':{'dir':'bmp_source/folder_16.png', 'file':'bmp_source/file_16.png'}, \
								'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2,'zoomable':('dir'), \
								'hot_keys':{'F3':disabledBtn,'F4':disabledBtn,'F5':disabledBtn,'F6':disabledBtn,'F7':disabledBtn,'F8':disabledBtn,'F9':disabledBtn}}
			self.nav_list['Level1DirList']={'code':"self.setLevel1DirList(('ConnectList','RootDirList',))", 'up':'RootDirList', 'forward':'LeafDirList', \
								'img':{'dir':'bmp_source/folder_16.png', 'file':'bmp_source/file_16.png', 'default':'bmp_source/file_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2,'zoomable':('dir'), \
								'hot_keys':{'F3':disabledBtn,'F4':disabledBtn,'F5':disabledBtn,'F6':disabledBtn,'F7':disabledBtn,'F8':disabledBtn,'F9':disabledBtn}}
			self.nav_list['LeafDirList']={'code':"self.setLeafDirList(('ConnectList','RootDirList','Level1DirList',))", 'up':'Level1DirList', 'forward':'', \
								'img':{'dir':'bmp_source/folder_16.png', 'file':'bmp_source/file_16.png', 'default':'bmp_source/file_16.png'}, 'update_cache':update_cache, 'key_col_id':0, 'fav_key_start':2,'zoomable':('dummy'), \
								'hot_keys':{'F3':disabledBtn,'F4':disabledBtn,'F5':disabledBtn,'F6':disabledBtn,'F7':disabledBtn,'F8':disabledBtn,'F9':disabledBtn}}
			self.draggable_lists=('LeafDirList','Level1DirList','RootDirList')
			#[from]=(to)

		self.nav_list['vars']=vars	
		if 0:
			for loc in self.parent.url_locator:
				self.parent.url_locator[loc].Hide()
				self.parent.find_in_btn[loc].Hide()	
		self.parent.clearUrlLocator()
		#self.parent.createUrlLocator()
		self.parent.setUrlLocator()
	def OnRefreshList(self, evt):
		print '--OnRefreshList'
		( pos) = evt.data
		if not pos:
			pos=self.parent.frame.drop_pos
		print pos
		print self.pos
		if pos==self.pos:
			print '%s reloaded.' % self.current_list
			self.parent.status='%s reloaded.' % self.current_list 
			self.execList(self.current_list)		
	def refreshList(self):
		#refresh current list
		
		self.execList(self.current_list)
		#Publisher().sendMessage( "stop_db_request", (pos) )
		
	def OnClearDrugStart(self, evt):
		(pos,items)=evt.data		
		#print position, self.parent.pos
		if 0:
			imgs= self.list.nav_list[cl]['img'] 
			img_type_col_id= self.list.img_col
			img_type = i[img_type_col_id]
			img_name=None
			if imgs.has_key(img_type):
				img_name=imgs[img_type]
			else:
				img_name=imgs['default']
			#print img_name
			img_id=self.list.image_refs[img_name]
			list.img[key]=img_id
			list.SetItemImage(index, list.img[key])
							
		if pos== self.parent.pos:
			#print(dir(self))
			l = []
			idx = -1
			while True: # find all the selected items and put them in a list
				idx = self.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
				print idx
				
				if idx == -1:
					break
				else:
					print 'selected index||||||||||',idx, self.img[0]
					self.SetItemImage(long(idx), 6)
				l.append(self.getItemInfo(idx))
			print 'lll:',l	
			if 1:
				for i in items:
					#print pos,s[0]
					#self.SetItemImage(s[0], 2)
					print i
					key=i[0]
					imgs= self.nav_list[self.current_list]['img'] 
					img_type_col_id= self.img_col
					img_type = i[img_type_col_id]
					img_name=None
					if imgs.has_key(img_type):
						img_name=imgs[img_type]
					else:
						img_name=imgs['default']
					print key, img_name,img_type
					img_id=self.image_refs[img_name]
					self.img[key]=img_id
					self.SetItemImage(7, 6)
			
		print 'after OnClearDrugStart'
	def setVar(self, name, value):
		self.nav_list['vars'][name]=value
	def getListFromId(self, id):
		print '-------------------',id
		print self.nav_list.keys()
		
		print '-------------------',id
		print self.nav_list
		print '-------------------',id
		return self.nav_list.keys()[id]
	def getRootName(self):
		return self.getListFromId(0)
		#print '11111111111111111111111111', elf.nav_list.keys()[0]
	def clearListVars(self, varname=None):
		#including tail
		if not varname:
			configDirLoc=self.nav_list['vars']['configDirLoc']
			self.nav_list['vars']=OrderedDict()
			self.nav_list['vars']['configDirLoc'] = configDirLoc
		else:
			nav_keys=self.nav_list.keys()
			idx=nav_keys.index(varname)
			for var_id in range(idx, len(nav_keys)-1 ):
				var=nav_keys[var_id]
				print 'clearListVars', idx, var 
				if self.nav_list['vars'].has_key(var):
					print self.nav_list['vars'][var]
					self.nav_list['vars'].pop(var)
	def setCurrListName_00(self, lname, direction):
		#print 'setCurrListName', self.loc_url
		from_list=self.current_list
		self.current_list=lname
		if direction=='forward':
			self.loc_url.append(lname)
		else:
			if direction=='up':
				if len(self.loc_url):
					self.loc_url.pop()
				print  '@'*20, from_list, lname, self.getRootName()
				if from_list==self.getRootName() or lname==self.getRootName():
					self.clearListVars()
					self.parent.clearUrlLocator()
				else:
					if self.nav_list['vars'].has_key(from_list):
						self.nav_list['vars'].pop(from_list)
			else:
				if direction=='home':
					self.loc_url=[]
				else:
					new_loc_url=[]
					if direction=='reset':						
						for loc in self.loc_url:
							if lname==loc:
								break;
							else:
								new_loc_url.append(loc)
						self.loc_url=new_loc_url
								
					self.loc_url=[]
	def setCurrListName(self, lname, direction):
		#print 'setCurrListName', self.loc_url
		from_list=self.current_list
		self.current_list=lname
		#if direction=='forward':
		#	self.loc_url.append(lname)
		#else:
		if 1:
			if direction=='up':
				#if len(self.loc_url):
				#	self.loc_url.pop()
				
				print  '@'*20, from_list, lname, self.getRootName()
				
				if from_list==self.getRootName() or lname==self.getRootName():
					self.clearListVars()
					#self.parent.clearUrlLocator()
				else:
					if self.nav_list['vars'].has_key(from_list):
						self.nav_list['vars'].pop(from_list)
			#else:
			if 0:
				if direction=='home':
					self.loc_url=[]
				else:
					new_loc_url=[]
					if direction=='reset':						
						for loc in self.loc_url:
							if lname==loc:
								break;
							else:
								new_loc_url.append(loc)
						self.loc_url=new_loc_url								
					self.loc_url=[]			
	def Populate(self):
		self.Freeze()
		#self.current_list='ConfigList'
		self.setCurrListName(self.root_list, 'forward')
		#self.setConfigList(('configDirLoc',))
		#self.Thaw()
		self.execList(self.root_list)
		self.parent.add_nav_hist(self.root_list)
		self.Thaw()			
	def __GoHome(self, data, extra1, extra2=None):
		(position)=data		
		print position, self.parent.pos
		if position== self.parent.pos:
			#self.Freeze()
			#self.current_list='ConfigList'
			#self.loc_url=[]
			self.clearListVars()
			self.setCurrListName(self.root_list, 'home')
			#self.setConfigList(('configDirLoc',))
			self.parent.status='Home (%s)' % self.root_list
			print self.pos ,self.current_list
			self.execList(self.root_list)
			#self.Thaw()
			self.parent.itemDataMap = self.data[self.current_list]
			self.parent.add_nav_hist(self.current_list)
			#listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())
			#self.setFocus(0)
			
			#self.loc_url.append(self.GetSelected())
			#self.parent.RecreateList(None,(self.parent.list,self.parent.filter))	
		else:
			print 'position mismatch', position,self.parent.pos

		self.parent.clearUrlLocator(self.parent.root_status)		
	def GoHome_del(self, evt):
		(position)=evt.data		
		print position, self.parent.pos
		if position== self.parent.pos:
			#self.Freeze()
			#self.current_list='ConfigList'
			#self.loc_url=[]
			self.clearListVars()
			self.setCurrListName(self.root_list, 'home')
			#self.setConfigList(('configDirLoc',))
			self.parent.status='Home (%s)' % self.root_list
			print self.pos ,self.current_list
			self.execList(self.root_list)
			#self.Thaw()
			self.parent.itemDataMap = self.data[self.current_list]
			self.parent.add_nav_hist(self.current_list)
			#listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())
			#self.setFocus(0)
			
			#self.loc_url.append(self.GetSelected())
			#self.parent.RecreateList(None,(self.parent.list,self.parent.filter))	
		else:
			print 'position mismatch', position,self.parent.pos

		self.parent.clearUrlLocator(self.parent.root_status)
		
	def __GoUp(self, data, extra1, extra2=None):
		(position)=data
		
		print position, self.parent.pos
		if position== self.parent.pos:
			cl_node=self.nav_list[self.current_list]
			#self.nav_list['vars'][self.current_list] = event.m_item.m_text
			#self.parent.filter_history[self.current_list]=self.parent.filter.GetValue()
			up=cl_node['up']
			if up:
				#back move				
				print 'up', up
				if 1:
					#self.Freeze()
					#if self.clearListVars()
					self.parent.status='Up (%s)' % up
					self.clearListVars(up)
					self.current_list=up
					#self.clearListVars()
					self.setCurrListName(up, 'up')
					self.execList(up)
					print 'after self.execList(up) +++++++++++++'
					#exec(self.nav_list[back]['code'], globals(), locals())
					self.parent.itemDataMap = self.data[self.current_list]
					
					self.parent.add_nav_hist(self.current_list)
					#listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())
					#listmix.ColumnSorterMixin.__init__(self, 4)
					#self.setFocus(0)
					#print(self.loc_url)
					#self.loc_url.pop()
					#print 'after pop', self.loc_url
					#self.parent.RecreateList(None,(self.parent.list,self.parent.filter))
					if self.current_list==self.root_list:
						self.parent.clearUrlLocator(self.parent.root_status)
				#self.parent.filter.SetValue(self.parent.filter_history[back])
				
		else:
			print 'position mismatch', position, self.parent.pos
		#self.Thaw()
		#self.Show()
	def GoUp_rem(self, evt):
		(position)=evt.data
		
		print position, self.parent.pos
		if position== self.parent.pos:
			cl_node=self.nav_list[self.current_list]
			#self.nav_list['vars'][self.current_list] = event.m_item.m_text
			#self.parent.filter_history[self.current_list]=self.parent.filter.GetValue()
			up=cl_node['up']
			if up:
				#back move				
				print 'up', up
				if 1:
					#self.Freeze()
					#if self.clearListVars()
					self.parent.status='Up (%s)' % up
					self.clearListVars(up)
					self.current_list=up
					#self.clearListVars()
					self.setCurrListName(up, 'up')
					self.execList(up)
					print 'after self.execList(up) +++++++++++++'
					#exec(self.nav_list[back]['code'], globals(), locals())
					self.parent.itemDataMap = self.data[self.current_list]
					
					self.parent.add_nav_hist(self.current_list)
					#listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())
					#listmix.ColumnSorterMixin.__init__(self, 4)
					#self.setFocus(0)
					#print(self.loc_url)
					#self.loc_url.pop()
					#print 'after pop', self.loc_url
					#self.parent.RecreateList(None,(self.parent.list,self.parent.filter))
					if self.current_list==self.root_list:
						self.parent.clearUrlLocator(self.parent.root_status)
				#self.parent.filter.SetValue(self.parent.filter_history[back])
				
		else:
			print 'position mismatch', position, self.parent.pos
		#self.Thaw()
		#self.Show()		
	def getVar(self,varname):
		return self.nav_list[varname]
	def getFileLocation(self):
		path= self.parent.getVarsToPath()
		(user,host,pwd,  home,file_filter)=self.getConnectInfo()
		return '/'.join((home,"/".join(path.split('/')[4:])))

	def _onEnter(self, event):
		global branchingList
		print '_onEnter'
		#print 'Enter!' , event.m_itemIndex
		#pprint(dir(event.m_item))
		#print event.m_item.m_text
		#print self.current_list
		#print self.nav_list[self.current_list]
	
		if self.current_list==branchingList:
			self.conn_id=event.m_itemIndex
			self.connect_type = self.GetItem(self.conn_id,1).GetText()	
			pprint(self.nav_list.keys())
			self.extendNavlist(self.connect_type )
			pprint(self.nav_list.keys())
			#sys.exit(1)
		if self.current_list=='TableList':
			partitioned= self.GetItem(event.m_itemIndex,2).GetText()
			assert partitioned in ('YES', 'NO'), 'Uknown partitioned status "" for table %s' % (partitioned, self.GetItem(event.m_itemIndex,0).GetText())
			if partitioned=='NO':
				#handle column list navigation
				self.nav_list['TableList']['forward']='ColumnList'
				self.nav_list['ColumnList']['up']='TableList'
			if partitioned=='YES':
				self.nav_list['TableList']['forward']='PartitionList'
				self.nav_list['ColumnList']['up']='SubPartitionList'
		if self.current_list=='PartitionList':
			subpartitioned= self.GetItem(event.m_itemIndex,2).GetText()
			assert subpartitioned in ('YES', 'NO'), 'Uknown subpartitioned status "" for partition %s' % (subpartitioned, self.GetItem(event.m_itemIndex,0).GetText())
			if subpartitioned=='NO':
				#handle column list navigation
				self.nav_list['PartitionList']['forward']='ColumnList'
				self.nav_list['ColumnList']['up']='PartitionList'
			if subpartitioned=='YES':
				self.nav_list['PartitionList']['forward']='SubPartitionList'
				self.nav_list['ColumnList']['up']='SubPartitionList'
			
			#sys.exit(1)
		cl_node=self.nav_list[self.current_list]
		self.nav_list['vars'][self.current_list] = event.m_item.m_text.strip('[]')
		#pprint(dir(event.m_item))
		#print event.m_item.GetData()
		self.parent.filter_history[self.current_list]=self.parent.filter.GetValue()
		soomable=True
		if cl_node.has_key('zoomable'):
			if not self.GetItem(event.m_itemIndex,1).GetText() in cl_node['zoomable']:
				soomable=False
				is_sql_file=self.GetItem(event.m_itemIndex,1).GetText()	=='file' and self.GetItem(event.m_itemIndex,2).GetText()=='sql' 
				if is_sql_file:
					#open modal SimpleSQLEditor here					
					file_to_open=self.getFileLocation()
					dlg = SimpleSQLEditor(self.parent.frame, sys.stdout,'Editing %s' % file_to_open, file_to_open)
					dlg.CenterOnScreen()
					# this does not return until the dialog is closed.
					val=dlg.Show()
					print 'dialog val=', val,wx.ID_OK
					#dlg.Destroy()
				is_xml_file=self.GetItem(event.m_itemIndex,1).GetText()	=='file' and self.GetItem(event.m_itemIndex,2).GetText()=='xml' 
				if is_xml_file:
					#open modal SimpleSQLEditor here					
					file_to_open=self.getFileLocation()
					dlg = SimpleXMLEditor(self.parent.frame, sys.stdout,'Editing %s' % file_to_open, file_to_open)
					dlg.CenterOnScreen()
					# this does not return until the dialog is closed.
					val=dlg.Show()
					print 'dialog val=', val,wx.ID_OK
					#dlg.Destroy()					
		if soomable:
			forward=cl_node['forward']
			if forward:
				self.setCurrListName(forward, 'forward')
				self.parent.status=forward
				self.execList(forward)
				self.parent.add_nav_hist(forward)
		else:
			blog.err('Columns are not zoomable.' ,self.pos)
			#print 'not zoomable'
		
		#Publisher().sendMessage( "set_buttons", (btns) )
		event.Skip()
	def execList(self,list_name):
		self.Freeze()
		blog.log('Creating %s' % list_name, self.pos)
		print 'execList', list_name,
		print self.nav_list[list_name]['code']
		#send( "start_db_progress_gauge", (self.pos) )
		exec(self.nav_list[list_name]['code'], globals(), locals())
		
		self.parent.add_hist(list_name)
		
		
		
	def execNextList(self,list_name):
		self.Freeze()
		next_list=self.nav_list[list_name]['forward']
		self.setCurrListName(next_list, 'reset')
		print 'execList', next_list
		exec(self.nav_list[next_list]['code'], globals(), locals())
		self.parent.add_nav_hist(list_name)
		
	def setFocus(self, id):
		if  self.GetItemCount():
			self.SetItemState(id, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
	def setFilter(self,value):
		#print(dir(self.parent.filter))
		self.parent.filter.SetValue(value)
	def _onSelect(self, event):
		#self.startIndex=event.m_itemIndex
		print 'Selected!',event.m_itemIndex
		event.Skip()		
	def setConfigList(self,vars):
		#self.Freeze()
		self.ClearAll()
		#self.current_list='ConfigList'
		self.setVars(vars)	
		#(database, owner) = location
		#self.InsertColumn(0, '##')
		self.InsertColumn(0, 'Configuration')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Created')

		#self.SetColumnWidth(0, 60)
		self.SetColumnWidth(0, 220)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 60)
		self.SetColumnWidth(3, 420)
		#print(dir(self))
		self.img_col = 1
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.InsertStringItem(0, '[..]')
		#self.idx_first=None
		#self.SetItemImage(0, 2)
		#(db,user) = ('MRR_BI','MRR_ETL_USER')
		
		self.data[self.current_list]=self.db.getConfigs(self._configDirLoc)
		#self.itemDataMap=self.data
		#self.parent.RecreateList(None,(self,self.parent.filter))
		#print 'sending evnt refresh_list_event'
		#Publisher().sendMessage( "refresh_list_event", ('xml_list',self.pos,gConfigCache,self.data) )
		#self.nav_list['vars'][self.current_list] = event.m_item.m_text.strip('[]')
		self.parent.RecreateList(None,(self.parent.list,self.parent.filter))
		self.parent.list.Thaw()

		
		
		
		
	def GetSelected(self):
		return self.GetItemText(self.GetFirstSelected())
	def setVars(self,vars):
		#print 'VARS::::', vars
		
		
		for var in vars: 
			#if self.nav_list[var].has_key('value_col'):
			#	value=
			value=self.nav_list['vars'][var]
			exec("self._%s = '%s'" % (var,value))
	def getVarsFromPath(self,path, sep):
		print path, sep
		return path.split(sep)
		#sys.exit(1)
		#for var in vars: exec("self._%s = '%s'" % (var,self.nav_list['vars'][var]))	
	def initVarsFromPath0(self,path, sep):
		vars=self.getVarsFromPath(path,sep)[1:]
		print 'new vars:'
		print vars
		nav_keys=self.nav_list.keys()[:-1]
		print  'nav_keys'
		print nav_keys
		print 'before'
		print self.nav_list['vars']
		for loc_id in range(len(nav_keys)):
			loc=nav_keys[loc_id]
			if loc_id<len(vars): #init only vars in the path
				self.nav_list['vars'][loc]=vars[loc_id]
			else:
				#self.nav_list['vars'][vloc]=None
				if self.nav_list['vars'].has_key(loc):
					self.nav_list['vars'].pop(loc)
		print 'after'
		print self.nav_list['vars']
		#sys.exit(1)
	def initVarsFromPath(self,path, sep):
		vars=self.getVarsFromPath(path,sep)[1:]
		print 'new vars:'
		print vars
		if len(vars)>3:
			self.connect_type=self.getConnectType(path)
			print self.connect_type
			print self.nav_list.keys()
			self.extendNavlist(self.connect_type)
			print self.nav_list.keys()
		#sys.exit(1)
		#conn_type=self.getConnectInfo()
		nav_keys=self.nav_list.keys()[:-1]
		print  'nav_keys'
		print nav_keys
		print 'before'
		print self.nav_list['vars']
		for loc_id in range(len(nav_keys)):
			loc=nav_keys[loc_id]
			if loc_id<len(vars): #init only vars in the path
				self.nav_list['vars'][loc]=vars[loc_id]
			else:
				#self.nav_list['vars'][vloc]=None
				if self.nav_list['vars'].has_key(loc):
					self.nav_list['vars'].pop(loc)
		print 'after'
		print self.nav_list['vars']
		#sys.exit(1)
		
	def setEnvironmentList(self, vars):
		#self.current_list='EnvironmentList'	
		#print self.nav_list['vars']
		#print vars
		self.ClearAll()
		# setting config file name and location 
		# self._ConfigList, self._configDirLoc
		self.setVars(vars)
		#print '>>>>>>',self._ConfigList
		config_file= '%s.xml' % os.path.join(self._configDirLoc, '%s' % self._ConfigList)
		print config_file
		#sys.exit(1)
		#print config_file
		self.InsertColumn(0, 'Environment')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Server')
		self.InsertColumn(3, 'Desription')

		self.SetColumnWidth(0, 220)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 100)
		self.SetColumnWidth(3, 420)
		self.img_col = 1
		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgstart+3)
		
		self.data[self.current_list]=self.db.getEnvironments(config_file)
		#print dbs
		#sys.exit(1)
		self.parent.RecreateList(None,(self.parent.list,self.parent.filter))
		self.parent.list.Thaw()
		if 0:
			for  key,i in self.data[self.current_list].items():
				#print i
				#sys.exit(1)
				if  1:
					index=self.InsertStringItem(sys.maxint, str(i[0]))
					self.SetStringItem(index, 1, str(i[1]))
					self.SetStringItem(index, 2, str(i[2]))
					self.SetStringItem(index, 3, str(i[3]))
					self.SetItemData(index, key)

					if i[1] == 'DEV':
						self.img[key]=self._imgstart+11
						self.SetItemImage(index, self.img[key])					
					else:
						self.img[key]=self._imgstart+11
						self.SetItemImage(index, self.img[key])	

					if i[1] == 'PROD':
						self.img[key]=self._imgstart+10
						self.SetItemImage(index, self.img[key])	
					if i[1] == 'UAT':
						self.img[key]=self._imgstart+12
						self.SetItemImage(index, self.img[key])	
					if i[1] == 'QA':
						self.img[key]=self._imgstart+13
						self.SetItemImage(index, self.img[key])	
						
					if (j % 2) == 0:
						self._bg='#e6f1f5'
						self.SetItemBackgroundColour(j, self._bg)
					j += 1		
					#sys.exit(1)		

	def setConnectList(self, vars):
		self.ClearAll()
		self.setVars(vars)
		#self.current_list='ConnectList'	
		
		config_file= '%s.xml' % os.path.join(self._configDirLoc, '%s' % self._ConfigList)
		#(database, owner) = location
		self.InsertColumn(0, 'Alias')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'User')
		self.InsertColumn(3, 'Server')

		self.SetColumnWidth(0, 150)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 150)
		self.SetColumnWidth(3, 70)
		self.img_col = 1
		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		if 0:
			env=self._EnvironmentList.upper()
			
			if 'DEV' in env:
				self.SetItemImage(0, self._imgid+11)
				self._bg='#E3F6CE'
			else:
				self.SetItemImage(0, self._imgid+11)
				self._bg='#e6f1f5'

			if 'PROD' in env:
				self.SetItemImage(0, self._imgid+10)
				self._bg='#F5A9A9'
			if 'UAT' in env:
				self.SetItemImage(0, self._imgid+12)
				self._bg='#E6E0F8'
			if 'QA' in env:
				self.SetItemImage(0, self._imgid+13)
				self._bg='#E6E6E6'
					
		#self.SetItemImage(0, 3)
		#print config_file,self._EnvironmentList
		#sys.exit(1)
		
		self.data[self.current_list]=self.db.getConnectList(config_file,self._EnvironmentList)
		#pprint(self.data[self.current_list])
		#sys.exit(1)
		if len(self.data[self.current_list])>0:
			if len(self.data[self.current_list][0])>4:
				self.InsertColumn(4, 'Home')
				self.SetColumnWidth(4, 350)
				
		self.parent.RecreateList(None,(self.parent.list,self.parent.filter))
		#reset buttons
		#if self.current_list=='TableList':
		#btns={'F3':'New','F4':disabledBtn,'F5':disabledBtn,'F6':disabledBtn,'F7':disabledBtn,'F8':disabledBtn,'F9':disabledBtn}
		if not self.buttons_set:
			btns=self.nav_list[self.current_list]['hot_keys']
			#Publisher().sendMessage( "set_buttons", (self.pos,btns) )
			send("set_buttons", (self.pos,btns) )
			self.buttons_set=True
		self.parent.list.Thaw()

	
	def setDatabaseList(self, vars):
		self.ClearAll()
		self.setVars(vars)	
		#self.current_list='DatabaseList'	
		self.InsertColumn(0, 'Database')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Size, MB', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Created')

		self.SetColumnWidth(0, 180)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 100)
		self.SetColumnWidth(3, 420)
		self.img_col = 1
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+6)
		#print vars, self._ConnectList
		#sys.exit(1)
		self.img_offset=4
		(user,db,pwd,host,port) = self.getConnectInfo()
		self.data[self.current_list]=self.db.getDatabases((user,db,pwd,host,port))
		#pprint(self.data)
		#sys.exit(1)
	def setRootDirList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='TableList'
		(user,host,pwd, home,file_filter) = self.getConnectInfo()
		#dbs=getTables((db,user),location)
		self.ClearAll()
		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Ext')
		self.InsertColumn(3, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(4, 'Permissions')
		self.InsertColumn(5, 'Changed')

		self.SetColumnWidth(0, 200)
		self.SetColumnWidth(1, 50)
		self.SetColumnWidth(2, 50)
		self.SetColumnWidth(3, 60)
		self.SetColumnWidth(4, 100)	
		self.SetColumnWidth(5, 200)		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+7)	
		self.img_offset=5		
		#self.data[self.current_list]=self.db.getRootDir((user,db,pwd),(self._DatabaseList,self._OwnerList))
		
		self.data[self.current_list]= self.file.getFileDirs((user,host,pwd), home,file_filter)
		#self.data[self.current_list]=self.db.getDatabases((user,db,pwd))
		pprint(self.data)
		#sys.exit(1)	
	def setLevel1DirList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='TableList'
		(user,host,pwd, home,file_filter) = self.getConnectInfo()
		#dbs=getTables((db,user),location)
		self.ClearAll()
		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Ext')
		self.InsertColumn(3, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(4, 'Permissions')
		self.InsertColumn(5, 'Changed')

		self.SetColumnWidth(0, 200)
		self.SetColumnWidth(1, 50)
		self.SetColumnWidth(2, 50)
		self.SetColumnWidth(3, 60)
		self.SetColumnWidth(4, 100)	
		self.SetColumnWidth(5, 200)		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+7)	
		#self.img_offset=5		
		#self.data[self.current_list]=self.db.getRootDir((user,db,pwd),(self._DatabaseList,self._OwnerList))
		#root='/home/zkqfas6/tab_copy/tmp/logs/lines/20130926_143534'
		#root=self.nav_list['vars']['RootDirList']
		#pprint()
		path='%s/%s' %(home,self.nav_list['vars']['RootDirList'])
		self.data[self.current_list]= self.file.getFileDirs((user,host,pwd), path,file_filter)
		#self.data[self.current_list]=self.db.getDatabases((user,db,pwd))
		#pprint(self.data)
		#sys.exit(1)	
	def setLeafDirList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='TableList'
		(user,host,pwd, home,file_filter) = self.getConnectInfo()
		#dbs=getTables((db,user),location)
		self.ClearAll()
		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Ext')
		self.InsertColumn(3, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(4, 'Permissions')
		self.InsertColumn(5, 'Changed')

		self.SetColumnWidth(0, 200)
		self.SetColumnWidth(1, 50)
		self.SetColumnWidth(2, 50)
		self.SetColumnWidth(3, 60)
		self.SetColumnWidth(4, 100)	
		self.SetColumnWidth(5, 200)		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+7)	
		#self.img_offset=5		
		#self.data[self.current_list]=self.db.getRootDir((user,db,pwd),(self._DatabaseList,self._OwnerList))
		#root='/home/zkqfas6/tab_copy/tmp/logs/lines/20130926_143534'
		#root=self.nav_list['vars']['RootDirList']
		#pprint()
		path='%s/%s/%s' %(home,self.nav_list['vars']['RootDirList'],self.nav_list['vars']['Level1DirList'])
		#level2=Level1DirList
		self.data[self.current_list]= self.file.getFileDirs((user,host,pwd), path,file_filter)
		#self.data[self.current_list]=self.db.getDatabases((user,db,pwd))
		#pprint(self.data)
		#sys.exit(1)	
		
	def getConnectInfo0(self):
		print self.parent.getVarsToPath()
		xpath=self.parent.getVarsToPath().split('/')[1:4]
		print xpath
		assert len(xpath)==3, 'Cannot set xpath connect filter.'
		specfile_from =os.path.join(configDirLoc, xpath[0])
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)

		
			connector=doc.getElementsByTagName("connector")[0]
			#assert len(connector), 'Cannot find connector tag in %s.' % xpath[0]
			print connector
			print xpath
			print xpath[1].split('.')
			env_type=xpath[1].split('.')[0]
			env=connector.getElementsByTagName(env_type)[0]
			alias_name=xpath[1].split('.')[1]
			alias=env.getElementsByTagName(alias_name)[0]
			print alias
			conn_name=xpath[2]
			conn=alias.getElementsByTagName(conn_name)[0]
			pprint (dir( conn))
			#sys.exit(1)
		if conn.hasAttribute('schema'):
			return (conn.getAttribute("schema"),conn.getAttribute("sid"),conn.getAttribute("pword"))
		if conn.hasAttribute('user'):
			return (conn.getAttribute("user"),conn.getAttribute("host"),conn.getAttribute("pword"),conn.getAttribute("home"))
		return (None, None, None)
	def getConnectInfo(self,varsToPath=None):
		if not varsToPath:
			varsToPath=self.parent.getVarsToPath()
		#print self.parent.getVarsToPath()
		xpath=varsToPath.split('/')[1:4]
		print xpath
		assert len(xpath)==3, 'Cannot set xpath connect filter.'
		specfile_from ='%s.xml' % os.path.join(configDirLoc, xpath[0])
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)

		
			connector=doc.getElementsByTagName("connector")[0]
			#assert len(connector), 'Cannot find connector tag in %s.' % xpath[0]
			print connector
			print xpath
			print xpath[1].split('.')
			env_type=xpath[1].split('.')[0]
			env=connector.getElementsByTagName(env_type)[0]
			alias_name=xpath[1].split('.')[1]
			alias=env.getElementsByTagName(alias_name)[0]
			print alias
			conn_name=xpath[2]
			print conn_name
			conn=alias.getElementsByTagName(conn_name)[0]
			print conn
			#pprint (dir( conn))
			#sys.exit(1)
		if conn.hasAttribute('schema'):
			if self.current_list=='TableList':
				object_filter=None
				if conn.hasAttribute('object_filter'):
					object_filter=conn.getAttribute("object_filter")
					return (conn.getAttribute("schema"),conn.getAttribute("sid"),conn.getAttribute("pword"),conn.getAttribute("HOST"),conn.getAttribute("PORT"),object_filter)
				else:
					return (conn.getAttribute("schema"),conn.getAttribute("sid"),conn.getAttribute("pword"),conn.getAttribute("HOST"),conn.getAttribute("PORT"),object_filter)
			else:
				return (conn.getAttribute("schema"),conn.getAttribute("sid"),conn.getAttribute("pword"),conn.getAttribute("HOST"),conn.getAttribute("PORT"))
		if conn.hasAttribute('user'):
			file_filter=None
			if conn.hasAttribute('file_filter'):
				file_filter=conn.getAttribute("file_filter")
			return (conn.getAttribute("user"),conn.getAttribute("host"),conn.getAttribute("pword"),conn.getAttribute("home"),file_filter)
		return (None, None, None, None, None )

	def getConnectType(self,varsToPath=None):
		if not varsToPath:
			varsToPath=self.parent.getVarsToPath()
		#print self.parent.getVarsToPath()
		print 'varsToPath:'
		print varsToPath
		xpath=varsToPath.split('/')[1:4]
		print xpath
		assert len(xpath)==3, 'Cannot set xpath connect filter.'
		specfile_from ='%s.xml' %os.path.join(configDirLoc, xpath[0])
		print specfile_from
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)

		
			connector=doc.getElementsByTagName("connector")[0]
			#assert len(connector), 'Cannot find connector tag in %s.' % xpath[0]
			print connector
			print 'xpath',xpath
			print xpath[1].split('.')
			env_type=xpath[1].split('.')[0]
			env=connector.getElementsByTagName(env_type)[0]
			alias_name=xpath[1].split('.')[1]
			alias=env.getElementsByTagName(alias_name)[0]
			print alias
			conn_name=xpath[2]
			print 'conn_name', conn_name
			print alias.getElementsByTagName(conn_name)
			conn=alias.getElementsByTagName(conn_name)[0]
			print conn
			#pprint (dir( conn))
			#sys.exit(1)
			if conn.hasAttribute('schema'):
				return 'db_connect'
			if conn.hasAttribute('user'):
				return 'host_connect'
		assert 1==2, 'Unknown connect type'
		return (None)
		
	def setListData(self):
		j = 0
		for key,i in self.data[self.current_list].items():
			#print i
			#sys.exit(1)
			if  1:
				
				index=self.InsertStringItem(sys.maxint, str(i[0]))
				for col in range(1,self.GetColumnCount()):
					self.SetStringItem(j, col, str(i[col]))
					#self.SetStringItem(j, 2, str(i[2]))
					#self.SetStringItem(j, 3, str(i[3]) #time.strftime('%Y-%m-%d %H:%M', time.localtime(sec))
					#)
				self.SetItemData(index, key)

				#if i[1] == 'database':
				if 1:
					self.img[key]=self._imgstart+self.img_offset
					self.SetItemImage(index, self.img[key])	
	
				if (j % 2) == 0:
					self.SetItemBackgroundColour(j, self._bg)
				j += 1		
				#sys.exit(1)	
		self.parent.itemDataMap=self.data[self.current_list]
		#listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())
	def setOwnerList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#print vars
		cl = self.parent.getVarsToPath()
		#sys.exit(1)
		#self.current_list='OwnerList'	
		self.InsertColumn(0, 'Owner')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Quota, MB', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Created')

		self.SetColumnWidth(0, 220)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 120)
		self.SetColumnWidth(3, 420)
		self.img_col = 1
		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		self.img_offset=7
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+4)
		login=(user,db,pwd,host,port) = self.getConnectInfo()
		#if imitateOracle
		val=None
		if  not ( user and db and pwd and host and port):
			print 'something is mising'
						
			dlg = EditOracleConnectDialog(self.parent, -1, "Edit Oracle connect.", size=(450, 450),login=login,
							 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
							 style=wx.SYSTEM_MENU | wx.CAPTION | wx.MAXIMIZE_BOX | wx.FRAME_NO_TASKBAR| wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN,
							 #style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
							 useMetal=False, ifOpenConnect=True,
							 )
			
			dlg.CenterOnScreen()
			val = dlg.Show()
			# this does not return until the dialog is closed.
			#val = dlg.ShowModal()
			#print 'val=================',val
			#if val == wx.ID_OK:
			#	print("You pressed OK\n")
			#else:				
			#	print("You pressed Cancel %s" % val)
				#break
			#table_to=None
			#login=(user,db,pwd,host,port)=dlg.out
		else:
			self.data[self.current_list]=self.db.getOwners(login,cache_loc=cl)
			#print 'setOwnerList done'
		#if dlg:
		#	print '|'*60
		#	print dlg
		#	print dlg.out
		#	#dlg.Destroy()
		#print login
		#if val == wx.ID_OK:
		#
	def onSetOwnerList(self,evt):
		( pos,login) = evt.data
		if pos==self.pos:
			#self.ClearAll()
			cl = self.parent.getVarsToPath()
			self.data[self.current_list]=self.db.getOwners(login,cache_loc=cl)
	def __onSetEnvList(self, data, extra1, extra2=None):
		(pos)=data	
		if pos==self.pos:
			self.ClearAll()

			send("go_up", (self.pos) )
			self.Thaw()			
	def onSetEnvList(self,evt):
		(pos) = evt.data
		if pos==self.pos:
			self.ClearAll()
			# setting config file name and location 
			# self._ConfigList, self._configDirLoc
			#self.setVars(vars)
			#print '>>>>>>',self._ConfigList
			#config_file= '%s.xml' % os.path.join(self._configDirLoc, '%s' % self._ConfigList)
			#print config_file
			#self.setEnvironmentList(('configDirLoc','ConfigList',))
			#self.parent.RecreateList(None,(self.parent.list,self.parent.filter))
			#self.parent.list.Thaw()
			#self.data[self.current_list]=self.db.getEnvironments(config_file)
			#print self.data[self.current_list]
			#self._ConfigList=None
			#self._EnvironmentList=None
			#self.execList('EnvironmentList')
			#self.parent.list.Thaw()
			#Publisher().sendMessage( "go_up", (self.pos) )
			send("go_up", (self.pos) )
			self.Thaw()
				
	def setTableList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='TableList'
		(user,db,pwd,host,port, object_filter) = self.getConnectInfo()
		#dbs=getTables((db,user),location)
		self.ClearAll()
		self.InsertColumn(0, 'Table')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Part')
		self.InsertColumn(3, 'Size, MB', wx.LIST_FORMAT_RIGHT)
		
		self.InsertColumn(4, 'Created')

		self.SetColumnWidth(0, 250)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 60)
		self.SetColumnWidth(3, 100)
		self.SetColumnWidth(4, 140)		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+7)	
		self.img_offset=8	
		cl = self.parent.getVarsToPath()		
		
		self.data[self.current_list]=self.db.getTables((user,db,pwd,host,port),(self._OwnerList), object_filter, cache_loc=cl)

	def setPartitionList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='TableList'
		(user,db,pwd,host,port) = self.getConnectInfo()
		#dbs=getTables((db,user),location)
		self.ClearAll()
		self.InsertColumn(0, 'Partition')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Subpart')
		self.InsertColumn(3, 'Size, MB', wx.LIST_FORMAT_RIGHT)
		
		self.InsertColumn(4, 'Created')

		self.SetColumnWidth(0, 150)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)
		self.SetColumnWidth(4, 140)		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+7)	
		self.img_offset=8		
		cl = self.parent.getVarsToPath()
		self.data[self.current_list]=self.db.getPartitions((user,db,pwd,host,port),(self._OwnerList, self._TableList), cache_loc=cl)
		#self.data[self.current_list]=self.db.getTableColumns(login,(self._OwnerList, self._TableList))
		#print dbs
		#sys.exit(1)
	def setSubPartitionList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='TableList'
		(user,db,pwd,host,port) = self.getConnectInfo()
		#dbs=getTables((db,user),location)
		self.ClearAll()
		self.InsertColumn(0, 'Subpartition')
		self.InsertColumn(1, 'Type')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		
		self.InsertColumn(3, 'Created')

		self.SetColumnWidth(0, 200)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 140)		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+7)	
		self.img_offset=8		
		cl = self.parent.getVarsToPath()
		self.data[self.current_list]=self.db.getSubPartitions((user,db,pwd,host,port),(self._OwnerList, self._TableList, self._PartitionList), cache_loc=cl)
		#self.data[self.current_list]=self.db.getTableColumns(login,(self._OwnerList, self._TableList))
		#print dbs
		#sys.exit(1)
		
	def setColumnList(self, vars):
		self.ClearAll()
		self.setVars(vars)		
		#self.current_list='ColumnList'
		self.InsertColumn(0, 'Column')
		self.InsertColumn(1, 'Format')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Type')
		self.InsertColumn(4, 'Id')
		self.InsertColumn(5, 'Created')
		self.img_col = 3

		self.SetColumnWidth(0, 200)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 40)
		self.SetColumnWidth(3, 60)
		self.SetColumnWidth(4, 40)		
		self.SetColumnWidth(5, 180)
		#self.parent.listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())
		self.img_offset=9		
		#self.il = uListCtrl.PyImageList(22,22)	
		#files = os.listdir('.')
		j = 0
		#self.idx_first=self.InsertStringItem(0, '[..]')
		#self.SetItemImage(0, self._imgid+8)
		login = self.getConnectInfo()
		cl = self.parent.getVarsToPath()
		self.data[self.current_list]=self.db.getTableColumns(login,(self._OwnerList, self._TableList), cache_loc=cl)

			
			
	def getItemInfo(self, idx):
		"""Collect all relevant data of a listitem, and put it in a list"""
		l = []
		#print idx
		l.append(idx) # We need the original index, so it is easier to eventualy delete it
		l.append(self.GetItemData(idx)) # Itemdata
		l.append(self.GetItemText(idx)) # Text first column
		for i in range(1, self.GetColumnCount()): # Possible extra columns
			l.append(self.GetItem(idx, i).GetText())
		return l	
		
	def _startDrag(self, e):
		""" Put together a data object for drag-and-drop _from_ this list. """
		print '_startDrag'
		blog.log('Started drag.',self.pos)
		if not self.current_list in self.draggable_lists:			
			print 'source not draggable!',self.current_list
			side=self.parent.getSide(self.pos)
			_msg="Drag: You have to drag a Table to Table to initiate data copy.\n"  
			if 1:
				blog.err(_msg,self.pos)
				btnStyle = wx.OK

				dlgStyle = wx.ICON_WARNING

				
				dlg = GMD.GenericMessageDialog(self, _msg,
											   "Table Copy",
											   btnStyle | dlgStyle)
				dlg.SetIcon(images.Mondrian.GetIcon())
				dlg.ShowModal()
				dlg.Destroy()

				self.parent.Status('Drag cancelled.')
		else:
			print 'source draggable',self.current_list
			l = []
			idx = -1
			while True: # find all the selected items and put them in a list
				idx = self.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
				if idx == -1:
					break
				l.append(self.getItemInfo(idx))
			print l
			#reject partitioned
			for tab in l:
				if tab[4] in 'YES' and self.current_list in 'TableList':
					print 'Partitoned table is not draggable!',self.current_list
					side=self.parent.getSide(self.pos)
					_msg="You cannot copy partitioned table (but only partition).\n"  
					if 1:
						blog.err(_msg,self.pos)
						btnStyle = wx.OK

						dlgStyle = wx.ICON_WARNING

						
						dlg = GMD.GenericMessageDialog(self, _msg,
													   "Table Copy",
													   btnStyle | dlgStyle)
						dlg.SetIcon(images.Mondrian.GetIcon())
						dlg.ShowModal()
						dlg.Destroy()

						self.parent.Status('Drag cancelled for partitioned table.')
						return
			#sys.exit(1)
			# Pickle the items list.
			itemdata = cPickle.dumps((self.pos,l), 1)
			# create our own data format and use it in a
			# custom data object
			ldata = wx.CustomDataObject("ListCtrlItems")
			ldata.SetData(itemdata)
			# Now make a data object for the  item list.
			data = wx.DataObjectComposite()
			data.Add(ldata)

			# Create drop source and begin drag-and-drop.
			dropSource = wx.DropSource(self)
			dropSource.SetData(data)
			res = dropSource.DoDragDrop(flags=wx.Drag_DefaultMove)
			#print '@@@@@@@@@@@@@@@ after dd:', res,wx.DragMove
			# If move, we want to remove the item from this list.
			#pprint(dir(dropSource))
			#pprint (dir(dropSource.GetDataObject()))
			if res == wx.DragMove:
				# It's possible we are dragging/dropping from this list to this list.  In which case, the
				# index we are removing may have changed...

				# Find correct position.
				l.reverse() # Delete all the items, starting with the last item
				#pprint (l)
				if self.current_list=='ColumnList':
					item_key=('QUERY')
					conn_type = self.getConnectType()
					#Publisher().sendMessage( "show_copy_pipeline", (self.pos,l,conn_type,item_key) )
					send("show_copy_pipeline", (self.pos,l,conn_type,item_key) )
				else:
					for i in l:
						item_key=(i[2].strip('[').strip(']'))
						#print item_key
						#sys.exit(0)
						pos = self.FindItem(i[0], i[2])
						#self.DeleteItem(pos)
						self.SetItemImage(pos, 0)
						if self.current_list!='ColumnList':
							conn_type = self.getConnectType()					
							#Publisher().sendMessage( "show_copy_pipeline", (self.pos,l,conn_type,item_key) )
							send("show_copy_pipeline", (self.pos,l,conn_type,item_key) )
						#print self.pos,l,conn_type,item_key
						#sys.exit(0)
					
				if 0:
					if self.current_list=='TableList':
						Publisher().sendMessage( "show_table_copy_dialog", (self.pos,l,conn_type) )
					if self.current_list=='PartitionList':
						Publisher().sendMessage( "show_partition_copy_dialog", (self.pos,l,conn_type) )
					if self.current_list=='SubPartitionList':
						Publisher().sendMessage( "show_subpartition_copy_dialog", (self.pos,l,conn_type) )
					if self.current_list=='ColumnList':
						Publisher().sendMessage( "show_query_copy_dialog", (self.pos,l,conn_type) )
					
	def checkDragStatus(self,data):
		status=1
		print self.current_list
		print		self.droppable_lists
		blog.log('Started drop.',self.pos)
		l = cPickle.loads(data)
		(pos_from, items_from)=l
		print pos_from
		print		items_from 
		from_list=self.parent.getListFromPos(pos_from)
		from_loc = self.parent.getListFromPos(pos_from).current_list
		#conn_type_from = from_list.getConnectType()
		#sys.exit(1)
		assert self.droppable_lists.has_key(from_loc), 'Source list %s is not defined as droppable source.' % from_loc
		_msg='Drop: You have to drop a Table to Table to initiate data copy.\n' 
		if from_loc =='ColumnList':
			_msg='Drop: You have to drop a Column(s) to Table or Column list to initiate Query Copy.\n' 
		if from_loc =='SubPartitionList':
			_msg='Drop: You have to drop a Sub-Partition to Sub-Partition list to initiate Query Copy.\n' 
		if from_loc =='PartitionList':
			_msg='Drop: You have to drop a Partition to Partition list to initiate Query Copy.\n' 

		#print self.parent.getVarsToPath()
		to_env=None
		vpath=self.parent.getVarsToPath().split('/')
		if  len(vpath)>2:
			to_env=vpath[2].split('.')[0]
			if to_env=='PROD':
				_msg='Drop: You cannot copy to PROD.\n'			
		else:
			_msg='Zoom into Table level to start Drag-n-Drop.\n'
		#print to_env

		if not self.current_list in self.droppable_lists[from_loc] or len(vpath)<3 or to_env=='PROD':
			print 'target not droppable!',from_loc,self.current_list
			print self.droppable_lists[from_loc]
			pprint(self.droppable_lists)
			# A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
			side=self.parent.getSide(self.pos)
			
			if 0:
				dlg = wx.MessageDialog( self, _msg,  "Table Copy", wx.OK)
				dlg.ShowModal() # Show it
				dlg.Destroy() # finally destroy it when finished.
			else:
				blog.err(_msg,self.pos)
				btnStyle = wx.OK

				dlgStyle = wx.ICON_WARNING

				
				dlg = GMD.GenericMessageDialog(self, _msg,
											   "Table Copy",
											   btnStyle | dlgStyle)
				dlg.SetIcon(images.Mondrian.GetIcon())
				dlg.ShowModal()
				dlg.Destroy()	
			#clear drug start
			#Publisher().sendMessage( "clear_drug_start", (seq) )
			status=0
			self.parent.Status('Drop cancelled.')
		else:
			pass
			#print from_loc
			#print self.pos
			#print self.parent.getVarsToPath().split('/')[2].split('.')[0]
			#sys.exit(1)
			#sys.exit(1)
			
		return status
	def _insert(self, x, y, seq):
		""" Insert text at given x, y coordinates --- used with drag-and-drop. """

		# Find insertion point.
		index, flags = self.HitTest((x, y))
		if 1:
			print 'target draggable',self.current_list
			if index == wx.NOT_FOUND: # not clicked on an item
				if flags & (wx.LIST_HITTEST_NOWHERE|wx.LIST_HITTEST_ABOVE|wx.LIST_HITTEST_BELOW): # empty list or below last item
					index = self.GetItemCount() # append to end of list
				elif self.GetItemCount() > 0:
					if y <= self.GetItemRect(0).y: # clicked just above first item
						index = 0 # append to top of list
					else:
						index = self.GetItemCount() + 1 # append to end of list
			else: # clicked on an item
				# Get bounding rectangle for the item the user is dropping over.
				rect = self.GetItemRect(index)

				# If the user is dropping into the lower half of the rect, we want to insert _after_ this item.
				# Correct for the fact that there may be a heading involved
				if y > rect.y - self.GetItemRect(0).y + rect.height/2:
					index += 1
			
			for i in seq: # insert the item data
				idx = self.InsertStringItem(index, i[2])
				self.SetItemImage(idx, 1)
				#print i
				#pprint(dir(self))
				self.SetItemData(idx, i[1])
				for j in range(1, self.GetColumnCount()):
					try: # Target list can have more columns than source
						self.SetStringItem(idx, j, i[2+j])
					except:
						pass # ignore the extra columns
				index += 1	
		self.parent.Status('Drop completed.')
		
		#show data copy dialog

	def setFileList(self):
		files = os.listdir('.')
		j = 1
		self.InsertStringItem(0, '[..]')
		self.SetItemImage(0, self._imgid+5)
		for i in files:
			(name, ext) = os.path.splitext(i)
			ex = ext[1:]
			size = os.path.getsize(i)
			sec = os.path.getmtime(i)
			self.InsertStringItem(j, name)
			self.SetStringItem(j, 1, ex)
			self.SetStringItem(j, 2, str(size) + ' B')
			self.SetStringItem(j, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))

			if os.path.isdir(i):
				self.SetItemImage(j, self._imgid+1)
			elif ex == 'py':
				self.SetItemImage(j, self._imgid+2)
			elif ex == 'jpg':
				self.SetItemImage(j, self._imgid+3)
			elif ex == 'pdf':
				self.SetItemImage(j, self._imgid+4)
			else:
				self.SetItemImage(j, self._imgid+0)

			if (j % 2) == 0:
				self.SetItemBackgroundColour(j, self._bg)
			j += 1	


		
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ListDrop

class ListDrop(wx.PyDropTarget):
	""" Drop target for simple lists. """

	def __init__(self, source, pos):
		""" Arguments:
		 - source: source listctrl.
		"""
		wx.PyDropTarget.__init__(self)

		self.dv = source
		self.pos=pos
		# specify the type of data we will accept
		self.data = wx.CustomDataObject("ListCtrlItems")
		self.SetDataObject(self.data)

	# Called when OnDrop returns True.  We need to get the data and
	# do something with it.
	def OnData(self, x, y, d):
		# copy the data from the drag source to our data object
		print 'OnData'
		if self.GetData():
			# convert it back to a list and give it to the viewer
			
			status=self.dv.checkDragStatus(self.data.GetData())
			print '==========================status:', status
			if status:
				ldata = self.data.GetData()
				l = cPickle.loads(ldata)
				(pos_from, items_from)=l
				print 1,l
				#sys.exit(1)
				self.dv.parent.frame.setDragDrop((pos_from,self.pos,items_from))
				print (pos_from,self.pos,items_from)
				#sys.exit(1)
				print 2,items_from
				self.dv._insert(x, y, items_from)
			else:
				d=-1
				

		# what is returned signals the source what to do
		# with the original data (move, copy, etc.)  In this
		# case we just return the suggested value given to us.
		#print 'OnData:', d
		print 'returning', d
		return d

		
class del_EditableTextListCtrl(wx.ListCtrl, TextEditMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition,
				size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		TextEditMixin.__init__(self) 
		self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
		#self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
	def OnBeginLabelEdit(self, event):
		print  event.m_col
		print event.m_itemIndex
		if event.m_col ==0:
			
			event.Skip()
		else:
			print 'selected',  event.m_col, event.m_itemIndex
			self.flipItemValue(event.m_col, event.m_itemIndex)
			event.Veto()
			if event.m_itemIndex==0:
				#self.SetFocus(0)
				self.SetItemState ( event.m_itemIndex, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED) 
		
	def flipItemValue(self, col, index):
		#val=self.GetItemText(col)

		#print val
		#print truncate_id
		#index = -1 
		#selected_items = [] 
		
		offset=2
		colcnt=self.GetColumnCount()
		shrd_col=6
		if col in range(offset,colcnt) and col!=shrd_col:
			self.SetStringItem(index, 1, 'Custom')
			#if index==-1: 
			#	break 

			#

			#pprint(dir(item))
			#print item.GetData()
			item = self.GetItem(index, col)
			val = item.GetText() 
			print val
			#selected_items.append(index) 
			if col==2:
				
				item = self.GetItem(index)
				#attr=wx.ListItemAttr()
				#attr.SetTextColour( wx.RED )
				if val=='OFF':
					item.SetTextColour( wx.RED)
				else:
					item.SetTextColour( wx.BLACK)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				#print dir(font)
				#font.SetColour("red")
				item.SetFont(font)
				# This does the trick:
				#item.SetText('test')
				self.SetItem(item)			
			tr={'OFF':'ON','ON':'OFF'}
			self.SetStringItem(index, col, tr[val])
			
	def OnItemSelected1(self, event):
		##print event.GetItem().GetTextColour()
		self.currentItem = event.m_itemIndex
		print self.GetItemText(self.currentItem)
		#msg='%s %s ' % (self.current_list[:-4], self.list.GetItemText(self.currentItem).strip('[]'))
		#self.Status(msg)
		event.Skip()
	def OnColClick(self, event):
		print "OnColClick: %d\n" % event.GetColumn(), event.m_itemIndex
		#self.log.WriteText("OnColClick: %d\n" % event.GetColumn())
		#print(dir(self.list))
		#if self.list.idx_first != None:
		#	self.list.DeleteItem(self.list.idx_first)		
	def OnRightClick(self, event):
		print 'OnRightClick' #,  event.m_itemIndex
		#print dir(event)
		#self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))
		#print(dir(self.list))
		#print GetSelectedItemCount
		# only do this part the first time so the events are only bound once
		disabled_favs=False
		if self.GetSelectedItemCount()==0:
			disabled_favs =True
		#else:
		#	print "OnRightClick %s\n" % self.GetItemText(self.currentItem),self.GetSelectedItemCount()
		self.show_in={}
		if 1:
			menu = wx.Menu()
			if 1: #not hasattr(self, "add_to_favorites"):
				self.shards_id = wx.NewId()
				#self.remove_from_favorites = wx.NewId()
				self.profile_id = wx.NewId()



			# make a menu
			
			# add some items
			menu3 = wx.Menu()
			for i in range(2,21):
				menu3.Append(1300+i,str(i))
				self.Bind(wx.EVT_MENU, self.OnShards, id=1300+i)
			
			menu_cp = wx.Menu()
			for i in range(len(cp)):
				menu_cp.Append(1400+i,cp.keys()[i])
				self.Bind(wx.EVT_MENU, self.OnCopyProfile, id=1400+i)				
			menu.AppendMenu(self.profile_id, "Copy Profile", menu_cp)
			menu.AppendMenu(self.shards_id , "Shards", menu3)
			#menu_t = wx.Menu()
			#menu_t.Append(0,'Yes')
			#menu_t.Append(1,'No')
			self.Bind(wx.EVT_MENU, self.OnTruncateChange, id=0)
			self.Bind(wx.EVT_MENU, self.OnTruncateChange, id=1)
			self.Bind(wx.EVT_MENU, self.OnCompressChange, id=3)
			self.Bind(wx.EVT_MENU, self.OnCompressChange, id=4)
			self.Bind(wx.EVT_MENU, self.OnStatsChange, id=5)
			self.Bind(wx.EVT_MENU, self.OnStatsChange, id=6)
			self.Bind(wx.EVT_MENU, self.OnIdxRebuildChange, id=7)
			self.Bind(wx.EVT_MENU, self.OnIdxRebuildChange, id=8)
			#menu.AppendMenu(self.shards_id, "Truncate", menu_t)
			menu.Append(0,'Truncate ON')
			menu.Append(1,'Truncate OFF')
			menu.Append(3,'Compress ON')
			menu.Append(4,'Compress OFF')
			menu.Append(5,'Stats ON')
			menu.Append(6,'Stats OFF')
			menu.Append(7,'Index Rebuild ON')
			menu.Append(8,'Index Rebuild OFF')			
			
			#menu.Append(self.add_to_favorites, "Shards")
			#menu.Append(self.remove_from_favorites, "Remove from Favorites.")

			if disabled_favs:
				menu.Enable(self.shards_id, False)
				#menu.Enable(self.remove_from_favorites, False)
			self.PopupMenu(menu)
			
			menu.Destroy()
	def OnShards(self, event):
		print 'OnShards'
		shard_id=event.GetId()-1300
		print shard_id
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			if 0:
				item = self.GetItem(index)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				# This does the trick:
				#item.SetText('test')
				self.SetItem(item)
			#

			#pprint(dir(item))
			#print item.GetData()
			self.SetStringItem(index, 6, str(shard_id))
		print selected_items
	def OnCopyProfile(self, event):
		print 'OnShards'
		cp_id=event.GetId()-1400
		#print shard_id
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			if 0:
				item = self.GetItem(index)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				# This does the trick:
				#item.SetText('test')
				self.SetItem(item)
			#

			#pprint(dir(item))
			#print item.GetData()
			self.SetStringItem(index, 1, cp.keys()[cp_id])
			offset=2
			flags=cp[cp.keys()[cp_id]]
			print flags
			for c in range(offset,self.GetColumnCount()):
				colname= self.GetColumn(c).GetText()
				#print colname, c, offset, c-offset
				self.SetStringItem(index, c, flags[colname])
			#sys.exit(1)
			#for i in range(offset,cp.keys()[cp_id]
		print selected_items
		
		#self.addToFavorites(selected_items)
	def OnTruncateChange(self, event):
		print 'OnTruncateChange'
		truncate_id=event.GetId()
		print truncate_id
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			item = self.GetItem(index)
			if truncate_id:
				item.SetTextColour( wx.BLACK)
			else:
				item.SetTextColour( wx.RED)
			font = item.GetFont()
			font.SetWeight(wx.FONTWEIGHT_BOLD)
			item.SetFont(font)
			# This does the trick:
			#item.SetText('test')
			self.SetItem(item)
			#

			#pprint(dir(item))
			#print item.GetData()
			tr=('ON','OFF')
			self.SetStringItem(index, 2, tr[truncate_id])
		print selected_items
		#self.addToFavorites(selected_items)
	def OnCompressChange(self, event):
		print 'OnShards'
		truncate_id=event.GetId()
		print truncate_id
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			if 0:
				item = self.GetItem(index)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				# This does the trick:
				#item.SetText('test')
				self.SetItem(item)
			#

			#pprint(dir(item))
			#print item.GetData()
			tr={3:'ON',4:'OFF'}
			self.SetStringItem(index, 3, tr[truncate_id])
		print selected_items
		#self.addToFavorites(selected_items)
	def OnIdxRebuildChange(self, event):
		print 'OnShards'
		truncate_id=event.GetId()
		print truncate_id
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			if 0:
				item = self.GetItem(index)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				# This does the trick:
				#item.SetText('test')
				self.SetItem(item)
			#

			#pprint(dir(item))
			#print item.GetData()
			tr={7:'ON',8:'OFF'}
			print tr
			print truncate_id
			self.SetStringItem(index, 5, tr[truncate_id])
		print selected_items
		#self.addToFavorites(selected_items)		
	def OnStatsChange(self, event):
		print 'OnShards'
		truncate_id=event.GetId()
		print truncate_id
		index = -1 
		selected_items = [] 
		while 1: 
			index = self.GetNextItem(index, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED) 
			if index==-1: 
				break 
			selected_items.append(index) 
			if 0:
				item = self.GetItem(index)
				font = item.GetFont()
				font.SetWeight(wx.FONTWEIGHT_BOLD)
				item.SetFont(font)
				# This does the trick:
				#item.SetText('test')
				self.SetItem(item)
			#

			#pprint(dir(item))
			#print item.GetData()
			tr={5:'ON',6:'OFF'}
			self.SetStringItem(index, 4, tr[truncate_id])
		print selected_items
		#self.addToFavorites(selected_items)	
class del_TCD_Tab1(wx.Panel):
	"""Panel for copy config"""
	def __init__(self, parent, frame,style,data):
		wx.Panel.__init__(self, parent, -1, style=style)
		self.data=data
		self.parentFrame=frame
		ID_TC_MODE = wx.NewId()
		ID_RUN_AT = wx.NewId()
		sizer = wx.BoxSizer(wx.VERTICAL)

		suffix=''
		if len(self.data)>1:
			suffix='s'
		label = wx.StaticText(self, -1, "Copy %d table%s." % (len(self.data),suffix))
		label.SetHelpText('Number of tables to copy. \nPless "Cancel" button to do do modifications.')
		self.mode_btn = wx.Button(self, ID_TC_MODE, "Mode(SYNC/sequential copy)",style=wx.BU_EXACTFIT)
		self.mode_btn.Enable(True) 
		self.runat_btn = wx.Button(self, ID_RUN_AT, "Run at %s (%s)" % (tc_host[tc_srv][2],tc_home),style=wx.BU_EXACTFIT)
		self.runat_btn.Enable(True)
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(self.mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(self.runat_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
		
		self.Bind(wx.EVT_BUTTON,self.OnTCModeButton, id=ID_TC_MODE)
		self.Bind(wx.EVT_BUTTON,self.OnRunAtButton, id=ID_RUN_AT)
		
		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "From:",size=(50,-1))
		label.SetHelpText("Table copy source schema.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		text = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_from)[4:], size=(300,-1))
		text.Enable(False)
		#text.SetLabel()
		text.SetHelpText("Table copy SOURCE schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "To:",size=(50,-1))
		label.SetHelpText("Table copy target schema.")
		box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
		print 'TableCopyDialog/pos_to:', parent.pos_to
		text = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_to)[4:], size=(300,-1))
		text.Enable(False)
		text.SetHelpText("Table copy TARGET schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}

		self.listCtrl_t = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES,size=(200, 250))
		self.listCtrl_t.InsertColumn(0, 'From Table')
		self.listCtrl = EditableTextListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(650, 250))
		self.listCtrl.InsertColumn(0, 'To Table')
		self.listCtrl.InsertColumn(1, 'Copy Profile')
		offset=1
		for id in range(len(_headers)):
			self.listCtrl.InsertColumn(offset+id+1, _headers[id])
		if 0:
			self.listCtrl.InsertColumn(offset+1, 'Truncate')
			self.listCtrl.InsertColumn(offset+2, 'Compress')
			self.listCtrl.InsertColumn(offset+3, 'Stats')
			self.listCtrl.InsertColumn(offset+4, 'Rebuild Indexes')
			self.listCtrl.InsertColumn(offset+5, 'Shards')
		self.listCtrl_t.SetColumnWidth(0, 200)
		self.listCtrl.SetColumnWidth(0, 220)
		self.listCtrl.SetColumnWidth(1, 200)
		self.listCtrl.SetColumnWidth(offset+1, 55)
		self.listCtrl.SetColumnWidth(offset+2, 59)
		self.listCtrl.SetColumnWidth(offset+3, 40)
		self.listCtrl.SetColumnWidth(offset+4, 100)
		self.listCtrl.SetColumnWidth(offset+5, 45)
		prof=def_w_prof
		for i in range(len(self.data)):
			item = self.data[i]
			
			#box.Add((10,5),0)
			tname=item[2].strip('[]')
			self.listCtrl_t.InsertStringItem(0, tname)
			self.listCtrl.InsertStringItem(0, tname)
			self.listCtrl.SetStringItem(0, 1, prof)
			flags=_flags[prof]
			#print prof
			#print flags
			for pid in range(len(flags)):
				print pid
				self.listCtrl.SetStringItem(0, offset+pid+1, flags[pid])
			#sys.exit(1)
			if 0:
				self.listCtrl.SetStringItem(0, offset+1, 'OFF')
				self.listCtrl.SetStringItem(0, offset+2, 'OFF')
				self.listCtrl.SetStringItem(0, offset+3, 'OFF')
				self.listCtrl.SetStringItem(0, offset+4, 'OFF')
				self.listCtrl.SetStringItem(0, offset+5, 'OFF')		

		lists = wx.BoxSizer(wx.HORIZONTAL)
		
		lists.Add(self.listCtrl_t, 0, wx.GROW|wx.EXPAND, 0)
		lists.Add(self.listCtrl, 1, wx.GROW|wx.EXPAND|wx.ALL, 0)
		sizer.Add(lists, 1, wx.GROW|wx.EXPAND|wx.ALL, 5)
		self.tcmodes={'SYNC':'SYNC/sequential copy', 'ASYNC': 'ASYNC/parallel copy'}
		self._tcmode='SYNC'
		self._runat='%s.%s' % (tc_srv, tc_home)
		self.SetSizer(sizer)
		sizer.Fit(self)
		
	def OnTCModeButton(self, event):
		#(loc)=params
		#print (loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateTcModeMenu()

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._tcmodeMenu.SetOwnerHeight(btnSize.y)
		self._tcmodeMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
	def OnRunAtButton(self, event):
		#(loc)=params
		#print (loc)
		#print dir(event)
		#btn=event.GetEventObject()
		#print btn.GetPosition()
		#print btn.GetSize()
		#print btn.GetPosition()[0]
		btn = event.GetEventObject()
		#import flat_menu2
		# Create the popup menu
		#self.CreateLongPopupMenu()
		self.CreateRunAtMenu()

		# Postion the menu:
		# The menu should be positioned at the bottom left corner of the button.
		btnSize = btn.GetSize()

		# btnPt is returned relative to its parent 
		# so, we need to convert it to screen 
		btnPt  = btn.GetPosition()
		btnPt = btn.GetParent().ClientToScreen(btnPt)
		#self._longPopUpMenu.SetOwnerHeight(btnSize.y)
		#self._longPopUpMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)
		self._runatMenu.SetOwnerHeight(btnSize.y)
		self._runatMenu.Popup(wx.Point(btnPt.x, btnPt.y), self)		
	def CreateTcModeMenu(self):

		if 1 :
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._tcmodeMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			
			for id, label in self.tcmodes.items():
				
				itype=wx.ITEM_NORMAL
				#print '>>>>>>>>>>>>>>',relative_path,path
				if id==self._tcmode:
					itype=wx.ITEM_CHECK
				menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( label), "", itype)
				pmenu.AppendItem(menuItem)				
				if id==self._tcmode:
					menuItem.Check(True)
				self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnTcModeMenu ,(id, label))	
	def CreateRunAtMenu(self):

		if 1 :
			#print self.list.data[loc]
			pmenu=FM.FlatMenu()
			self._runatMenu = pmenu
			#-----------------------------------------------
			# Flat Menu test
			#-----------------------------------------------

			# First we create the sub-menu item
			#subMenu = FM.FlatMenu()
			#subSubMenu = FM.FlatMenu()
			id=wx.ID_ANY
			# Create the menu items
			
			for id, info in tc_runat.items():
				label='%s (%s)' % (info[0], info[1])
				btn_label='%s (%s)' % (info[0], info[2])
				itype=wx.ITEM_NORMAL
				#print '>>>>>>>>>>>>>>',relative_path,path
				if id==self._runat:
					itype=wx.ITEM_CHECK
				menuItem = FM.FlatMenuItem(pmenu, wx.ID_ANY, '%s' % ( label), "", itype)
				pmenu.AppendItem(menuItem)				
				if id==self._runat:
					menuItem.Check(True)
				self.gen_bind(FM.EVT_FLAT_MENU_SELECTED,menuItem, self.OnRunAtMenu ,(id, btn_label))	
				
	def gen_bind(self, type, instance, handler, *args, **kwargs):
		self.Bind(type, lambda event: handler(event, *args, **kwargs), instance)			
				
	def OnTcModeMenu(self, event, params):
		(id, label) = params
		print 'OnTcModeMenu', id, label
		self.mode_btn.SetLabel('Mode(%s)' % label)
		self._tcmode=id	
	def OnRunAtMenu(self, event, params):
		(id, label) = params
		print 'OnRunAtMenu', id, label
		self.runat_btn.SetLabel("Run at %s" % label)
		self._runat=id	
		
class del_DeployXmlLogPanel(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent, style):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parentFrame=parent
		suffix=''
		self.label = wx.StaticText(self, -1, 'Started code deployment.')
		#self.label.SetLabel("Hello World!")
		self.label.SetHelpText('Deployment status.')

		self.sizer.Add(self.label, 0, wx.GROW|wx.ALL, 5)

		#self.nb = fnb.FlatNotebook(self, -1,size=(600,600), agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST)

			
		if 1:
			self.logger = TacoTextEditor(self)
			#self.nb.AddPage(self.logger, 'Table Copy Log')
			#self.config = TacoCodeEditor(self)
			#self.nb.AddPage(self.config, 'pipeline_config.xml')
			#self.worker = TacoCodeEditor(self)
			#self.nb.AddPage(self.worker, 'pipeline_worker.xml')

		self.sizer.Add(self.logger, 1, wx.GROW|wx.EXPAND|wx.ALL, 5)
		if 0:	
			btnsizer = wx.BoxSizer(wx.HORIZONTAL)
			#self.btn_backgr = wx.Button(self, ID_BACKGROUND, "Background",size=(-1,20))
			#self.btn_backgr.Disable()
			self.btn_stop = wx.Button(self, ID_STOP, "Stop", size=(50,15))

			#button2.Disable()
			#self.btn_close = wx.Button(self, ID_EXIT, "Close", size=(50,20))
			#self.btn_close.Disable()
			self.count=0
			self.gauge = wx.Gauge(self, -1, size=(-1, 15),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
			if 1:
				i=wx.NewId()			
				self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
				
				self.timer=wx.Timer(self, id=i)
								
			#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
			#self.gauge[pos].SetPosition((1,1))
			btnsizer.Add((1,1),0)
			btnsizer.Add(self.gauge, 1,wx.EXPAND)		
			btnsizer.Add((3,3),0)
			#btnsizer.Add(self.btn_backgr, 0)
			#btnsizer.Add((10,5),0)
			btnsizer.Add(self.btn_stop, 0)
			btnsizer.Add((1,1),0)
			#btnsizer.Add((25,5),1)
			#btnsizer.Add(self.btn_trial, 0)
			#btnsizer.Add((5,5),1, wx.EXPAND)		
			#btnsizer.Add(self.btn_close, 0 , wx.RIGHT)
			
			#self.Bind(wx.EVT_BUTTON, self.OnBackground, id=ID_BACKGROUND)
			#self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
			self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
			
			#self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
			
			self.sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 5)
			self.SetSizer(self.sizer)
			self.sizer.Fit(self)
			self.timer.Start(100)
		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		

	def Status(self, msg):
		self.label.SetLabel(msg)
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)

		
	def OnExit(self,e):
		#Publisher().sendMessage( "refresh_list", (None) )
		send("refresh_list", (None) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'
		
class del_TcCodePanel(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent, style):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parentFrame=parent
		#suffix=''
		#self.label = wx.StaticText(self, -1, 'Started code deployment.')
		#self.label.SetLabel("Hello World!")
		#self.label.SetHelpText('Deployment status.')

		#self.sizer.Add(self.label, 0, wx.GROW|wx.ALL, 5)
		if 1:
			self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_NO_X_BUTTON)				
			if 1:
				self.specs = TacoCodeEditor(self)
				self.nb.AddPage(self.specs, 'Specs')
				self.worker = TacoCodeEditor(self)
				self.nb.AddPage(self.worker, 'Worker')
				self.shell = TacoCodeEditor(self)
				self.nb.AddPage(self.shell, 'Shell')

			self.sizer.Add(self.nb, 1, wx.GROW|wx.EXPAND|wx.ALL, 5)
			#self.sizer.Add(self.nb, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
	def Shell(self, msg):
		#self.label.SetLabel(msg)
		self.shell.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)	
	
		
class del_TableCopyDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size, 
			style, useMetal=False,pos=wx.DefaultPosition, 
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		
		self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_NO_X_BUTTON)	
		#self.initParams()
		if 1:
			(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
			print 'init:', self.parent.drag_pos
			print 'init:', 		self.parent.drop_pos
			print 'init:', 		self.parent.dd_data
			
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)

		
		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.config_panel=TCD_Tab1(self,parent,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, data=self.data)
		self.nb.AddPage(self.config_panel, 'Configuration')
		self.code_panel=TcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		self.nb.AddPage(self.code_panel, 'Code')
		self.deploy_panel=DeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		self.nb.AddPage(self.deploy_panel, 'Log')		
		sizer.Add(self.nb, 1, wx.EXPAND|wx.GROW|wx.ALL, 5)
		#line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		#sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		
		if 1:
			btnsizer = wx.BoxSizer(wx.HORIZONTAL)
			#self.btn_backgr = wx.Button(self, ID_BACKGROUND, "Background",size=(-1,20))
			#self.btn_backgr.Disable()
			self.btn_stop = wx.Button(self, ID_STOP, "Stop", size=(50,15))

			#button2.Disable()
			#self.btn_close = wx.Button(self, ID_EXIT, "Close", size=(50,20))
			#self.btn_close.Disable()
			self.count=0
			self.gauge = wx.Gauge(self, -1, size=(-1, 15),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
			if 1:
				i=wx.NewId()			
				self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
				
				self.timer=wx.Timer(self, id=i)
								
			#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
			#self.gauge[pos].SetPosition((1,1))
			btnsizer.Add((1,1),0)
			btnsizer.Add(self.gauge, 1,wx.EXPAND)		
			btnsizer.Add((3,3),0)
			#btnsizer.Add(self.btn_backgr, 0)
			#btnsizer.Add((10,5),0)
			btnsizer.Add(self.btn_stop, 0)
			btnsizer.Add((1,1),0)
			#btnsizer.Add((25,5),1)
			#btnsizer.Add(self.btn_trial, 0)
			#btnsizer.Add((5,5),1, wx.EXPAND)		
			#btnsizer.Add(self.btn_close, 0 , wx.RIGHT)
			
			#self.Bind(wx.EVT_BUTTON, self.OnBackground, id=ID_BACKGROUND)
			#self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
			self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
			
			#self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
			
			sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 5)
			#self.SetSizer(self.sizer)
			#self.sizer.Fit(self)
			#self.timer.Start(100)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_start = wx.Button(self, ID_START, "Start copy")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		button2.Disable()
		ID_TRIAL = wx.NewId()
		self.btn_trial = wx.Button(self, ID_TRIAL, "Deploy xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()
		ID_TEST= wx.NewId()
		self.btn_test = wx.Button(self, ID_TEST, "Test")
		self.btn_cancel = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(self.btn_start, 0)
		btnsizer.Add((10,5),0)
		btnsizer.Add(button2, 0)
		btnsizer.Add((35,5),0)
		btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(self.btn_test, 0 , wx.LEFT)		
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(self.btn_cancel, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnTest, id=ID_TEST)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		self.Bind(wx.EVT_BUTTON, self.OnDeployXml, id=ID_TRIAL)
		sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
		#self.deploy_panel=None
		#self.code_panel=None
		#self.tcmodes=OrderedDict({'SYNC':'SYNC/sequential copy', 'ASYNC': 'ASYNC/parallel copy'})

		#print self.tcmodes.keys()
		#sys.exit(1)
		#Publisher().subscribe(self.onTcDeploymentCompleted,'tc_deployment_completed')
		#Publisher().subscribe(self.onCreatedConfigFile, "created_config_file")
		#Publisher().subscribe(self.onCreatedWorkerFile, "created_worker_file")
		#Publisher().subscribe(self.onCopyDone, "copy_done")
		#Publisher().subscribe(self.onCopyStatus, "copy_status")
		#Publisher().subscribe(self.onShellCode, "shell_code")
		sub(self.onTcDeploymentCompleted,'tc_deployment_completed')
		sub(self.onCreatedConfigFile, "created_config_file")
		sub(self.onCreatedWorkerFile, "created_worker_file")
		sub(self.onCopyDone, "copy_done")
		sub(self.onCopyStatus, "copy_status")
		sub(self.onShellCode, "shell_code")
		
		self._action=None
		self.SetSize((850,650))
	def OnTest(self,event):		
		print 'OnTest'
		if 1:
			#Publisher().sendMessage( "test_manager_panes", (1) )
			send("test_manager_panes", (1) )
			
	def onCopyStatus(self, evt):
		print 'onTableCopyStatus'
		(out,err) = evt.data

		self.Log(out)
		#Publisher().sendMessage( "tc_deployment_completed", () )	
	def onShellCode(self, evt):
		print 'onTableCopyStatus'
		(out,err) = evt.data
		if err:
			self.code_panel.Shell(err)
		self.code_panel.Shell(out)
		#Publisher().sendMessage( "tc_deployment_completed", () )		
	def Log(self, msg):
		self.deploy_panel.Status(msg)
		
	def onCreatedConfigFile(self, evt):
		print 'onCreatedConfigFile'
		(file_loc) = evt.data
		print file_loc
		if 0 or not self.code_panel:
			self.code_panel=TcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
			self.nb.AddPage(self.code_panel, 'Code')
			self.nb.SetSelection(2)			
		if os.path.isfile(file_loc):
			f = open(file_loc, 'r')			
			self.code_panel.specs.SetValue(f.read())
			f.close()
	def onCreatedWorkerFile(self, evt):
		print 'onCreatedWorkerFile'
		(file_loc) = evt.data		
		print file_loc
		if 0 or not self.code_panel:
			self.code_panel=TcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
			self.nb.AddPage(self.code_panel, 'Code')
			self.nb.SetSelection(2)		
		if os.path.isfile(file_loc):
			f = open(file_loc, 'r')			
			self.code_panel.worker.SetValue(f.read()) 
			f.close()	
	def onCopyDone(self, evt):
		print 'onCopyDone'
		(out,err,pos_to) = evt.data
		
		status='successfully'
		
		if 1: 
			if err:
				print '#'*40
				print err
				print '#'*40
				status='with errors'
				self.Status(err)
			#self.deploy_panel.Status(status)
			self.keepGoing = False
			self.btn_cancel.Enable(True)
			self.btn_stop.Enable(False)
			self.gauge.SetValue(100)
			self.timer.Stop()
			if out or out==0:
				self.deploy_panel.Status(out)
				self.deploy_panel.Status('Copy completed %s.' % status)

			
	def TimerHandler0(self, event,the_id):
		#(pos)=params
		#pos=self.timer_xref[the_id]
		#print 'the_id', the_id,pos
		self.count = self.count + 1

		if self.count >= 100:
			self.count = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		
		self.gauge.SetValue(self.count)
		#self.gauge.Pulse()		
	def OnStop(self,e):
		assert self._action in ('D','S'), 'Unknown action %s' % self._action
		
		
		self.timer.Stop()
		#self.btn_backgr.Disable()
		self.btn_stop.Disable()
		#self.btn_close.Enable(True)
		print 'OnStop'
		if self._action=='D':
			self.deploy_panel.Status('Process stopped.')
			#Publisher().sendMessage( "stop_deploy_xml_process", ('Kill deployment thread') )
			send( "stop_deploy_xml_process", ('Kill deployment thread') )
		
	def onTcDeploymentCompleted(self,e):
		self.btn_start.Enable(True)
		self.btn_trial.Enable(True)

	def OnTrial(self,e):
		self.table_to={}	
		if 1:
			for i in range(len(self.data)):
				row=[self.config_panel.listCtrl.GetItem(i, col).GetText() for col in range(self.config_panel.listCtrl.GetColumnCount())]
				#self.table_to[row[0]]=row
				self.table_to[row[0]]=(self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
		self.status='Trial'
		self.Close(True)
	def OnDeployXml(self,e):
		self.table_to={}
		self._action='D'
		self.code_panel.shell.SetValue('')
		self.timer.Start(100)
		self.btn_trial.Enable(False)
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.config_panel.listCtrl.GetItem(i, col).GetText() for col in range(self.config_panel.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=(self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
				#print  self.table_to[tname]
		self.status='DeployXml'

			
		if 0 or not self.deploy_panel:
			self.deploy_panel=DeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
			self.nb.AddPage(self.deploy_panel, 'Deployment log')
		self.nb.SetSelection(2)
		if 1:
			#table_to=dlg.table_to	
			self.btn_start.Enable(False)
			#Publisher().sendMessage( "deploy_tc_xml", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )
			send("deploy_tc_xml", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )

	def initParams1(self):		
		if 1:
			(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
			print 'init:', self.parent.drag_pos
			print 'init:', 		self.parent.drop_pos
			print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def OnStart(self,e):
		
		self._action='S'
		self.timer.Start(100)
		self.code_panel.shell.SetValue('')
		self.table_to={}
		self.btn_trial.Enable(False)
		self.btn_start.Enable(False)
		self.btn_stop.Enable(True)
		self.btn_cancel.Enable(False)
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.config_panel.listCtrl.GetItem(i, col).GetText() for col in range(self.config_panel.listCtrl.GetColumnCount())]
				#self.table_to[row[0]]=row
				self.table_to[row[0]]=(self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
				#print  self.table_to[tname]
		#self.status='Start'
		#self.Close(True)
		self.nb.SetSelection(2)
		if 1:
			#table_to=dlg.table_to	
			self.btn_start.Enable(False)
			#Publisher().sendMessage( "start_table_copy", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )
			send("start_table_copy", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )
		

class del_PartitionCopyDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.initParams()
		suffix=''
		if len(self.data)>1:
			suffix='s'
		label = wx.StaticText(self, -1, "Copy %d table%s." % (len(self.data),suffix))
		label.SetHelpText('Number of table to copy. \nPless "Cancel" button to ddo do modifications.')
		mode_btn = wx.Button(self, ID_BUTTON + 3, "Mode(SYNC)")
	
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "From:",size=(50,-1))
		label.SetHelpText("Table copy source schema.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_from)[4:], size=(300,-1))
		text.Enable(False)
		#text.SetLabel()
		text.SetHelpText("Table copy SOURCE schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "To:",size=(50,-1))
		label.SetHelpText("Table copy target schema.")
		box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
		print 'TableCopyDialog/pos_to:', self.pos_to
		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_to)[4:], size=(300,-1))
		text.Enable(False)
		text.SetHelpText("Table copy TARGET schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}
		if 0:
		
			box = wx.BoxSizer(wx.HORIZONTAL)
			fgs = wx.FlexGridSizer(len(self.data), 3)

			for i in range(len(self.data)):
				item = self.data[i]
				tablezilla
				#box.Add((10,5),0)
				tname=item[2].strip('[]')
				tlabel= "From %s to:" % tname
				label = wx.StaticText(self, -1,tlabel,size=(300,20))
				label.SetHelpText("Target table.")
				#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

				self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
				self.tc_tables[tname].Enable(True)
				self.tc_tables[tname].SetHelpText("Target table name")
				self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
				fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
				#box.Add(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT)
				#box.Add((10,5),0)
				#box.Add(self.shards_btn[tname], 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)
				#box.Add((10,5),0)
			box.Add((7,5),0)	
			box.Add(fgs, 0, wx.ALIGN_CENTER_VERTICAL, 1)
			box.Add((4,5),0)
		self.listCtrl = EditableTextListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(650, 250))
		self.listCtrl.InsertColumn(0, 'From Table')
		self.listCtrl.InsertColumn(1, 'To Table (Editable)')
		self.listCtrl.InsertColumn(2, '# of Shards')
		self.listCtrl.SetColumnWidth(0, 240)
		self.listCtrl.SetColumnWidth(1, 300)
		self.listCtrl.SetColumnWidth(2, 100)
		for i in range(len(self.data)):
			item = self.data[i]
			
			#box.Add((10,5),0)
			tname=item[2].strip('[]')
			#tlabel= "From %s to:" % tname
			#label = wx.StaticText(self, -1,tlabel,size=(300,20))
			#label.SetHelpText("Target table.")
			#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

			#self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
			#self.tc_tables[tname].Enable(True)
			#self.tc_tables[tname].SetHelpText("Target table name")
			#self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
			#fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
			self.listCtrl.InsertStringItem(0, tname)
			self.listCtrl.SetStringItem(0, 1, tname)
			self.listCtrl.SetStringItem(0, 2, 'OFF')



			
		sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_START, "Start")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		button2.Disable()
		ID_TRIAL = wx.NewId()
		self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		button4 = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(button1, 0)
		btnsizer.Add((10,5),0)
		btnsizer.Add(button2, 0)
		btnsizer.Add((35,5),0)
		btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(button4, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		self.Bind(wx.EVT_BUTTON, self.OnDeployXml, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			btnsizer = wx.StdDialogButtonSizer()
			
			if wx.Platform != "__WXMSW__":
				btn = wx.ContextHelpButton(self)
				btnsizer.AddButton(btn)
			
			btn = wx.Button(self, wx.ID_OK)
			btn.SetHelpText("The OK button completes the dialog")
			btn.SetDefault()
			btnsizer.AddButton(btn)

			btn = wx.Button(self, wx.ID_CANCEL)
			btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
			btnsizer.AddButton(btn)
			btnsizer.Realize()

			sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
	def OnDeployXml(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='DeployXml'
		self.Close(True)		
	def initParams(self):
		(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
		print 'init:', self.parent.drag_pos
		print 'init:', 		self.parent.drop_pos
		print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def OnStart(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Start'
		self.Close(True)
class del_SubpartitonCopyDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.initParams()
		suffix=''
		if len(self.data)>1:
			suffix='s'
		label = wx.StaticText(self, -1, "Copy %d table%s." % (len(self.data),suffix))
		label.SetHelpText('Number of table to copy. \nPless "Cancel" button to ddo do modifications.')
		mode_btn = wx.Button(self, ID_BUTTON + 3, "Mode(SYNC)")
	
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "From:",size=(50,-1))
		label.SetHelpText("Table copy source schema.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_from)[4:], size=(300,-1))
		text.Enable(False)
		#text.SetLabel()
		text.SetHelpText("Table copy SOURCE schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "To:",size=(50,-1))
		label.SetHelpText("Table copy target schema.")
		box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
		print 'TableCopyDialog/pos_to:', self.pos_to
		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_to)[4:], size=(300,-1))
		text.Enable(False)
		text.SetHelpText("Table copy TARGET schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}
		if 0:
		
			box = wx.BoxSizer(wx.HORIZONTAL)
			fgs = wx.FlexGridSizer(len(self.data), 3)

			for i in range(len(self.data)):
				item = self.data[i]
				
				#box.Add((10,5),0)
				tname=item[2].strip('[]')
				tlabel= "From %s to:" % tname
				label = wx.StaticText(self, -1,tlabel,size=(300,20))
				label.SetHelpText("Target table.")
				#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

				self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
				self.tc_tables[tname].Enable(True)
				self.tc_tables[tname].SetHelpText("Target table name")
				self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
				fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
				#box.Add(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT)
				#box.Add((10,5),0)
				#box.Add(self.shards_btn[tname], 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)
				#box.Add((10,5),0)
			box.Add((7,5),0)	
			box.Add(fgs, 0, wx.ALIGN_CENTER_VERTICAL, 1)
			box.Add((4,5),0)
		self.listCtrl = EditableTextListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(650, 250))
		self.listCtrl.InsertColumn(0, 'From Table')
		self.listCtrl.InsertColumn(1, 'To Table (Editable)')
		self.listCtrl.InsertColumn(2, '# of Shards')
		self.listCtrl.SetColumnWidth(0, 240)
		self.listCtrl.SetColumnWidth(1, 300)
		self.listCtrl.SetColumnWidth(2, 100)
		for i in range(len(self.data)):
			item = self.data[i]
			
			#box.Add((10,5),0)
			tname=item[2].strip('[]')
			#tlabel= "From %s to:" % tname
			#label = wx.StaticText(self, -1,tlabel,size=(300,20))
			#label.SetHelpText("Target table.")
			#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

			#self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
			#self.tc_tables[tname].Enable(True)
			#self.tc_tables[tname].SetHelpText("Target table name")
			#self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
			#fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
			self.listCtrl.InsertStringItem(0, tname)
			self.listCtrl.SetStringItem(0, 1, tname)
			self.listCtrl.SetStringItem(0, 2, 'OFF')



			
		sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_START, "Start")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		button2.Disable()
		ID_TRIAL = wx.NewId()
		self.btn_trial = wx.Button(self, ID_TRIAL, "Deploy xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		button4 = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(button1, 0)
		btnsizer.Add((10,5),0)
		btnsizer.Add(button2, 0)
		btnsizer.Add((35,5),0)
		btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(button4, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		self.Bind(wx.EVT_BUTTON, self.OnDeployXml, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			btnsizer = wx.StdDialogButtonSizer()
			
			if wx.Platform != "__WXMSW__":
				btn = wx.ContextHelpButton(self)
				btnsizer.AddButton(btn)
			
			btn = wx.Button(self, wx.ID_OK)
			btn.SetHelpText("The OK button completes the dialog")
			btn.SetDefault()
			btnsizer.AddButton(btn)

			btn = wx.Button(self, wx.ID_CANCEL)
			btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
			btnsizer.AddButton(btn)
			btnsizer.Realize()

			sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
	def OnDeployXml(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='DeployXml'
		self.Close(True)		
	def initParams(self):
		(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
		print 'init:', self.parent.drag_pos
		print 'init:', 		self.parent.drop_pos
		print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def OnStart(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Start'
		self.Close(True)		
class F2FCopyDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.initParams()
		suffix=''
		if len(self.data)>1:
			suffix='s'
		label = wx.StaticText(self, -1, "Copy %d table%s." % (len(self.data),suffix))
		label.SetHelpText('Number of table to copy. \nPless "Cancel" button to ddo do modifications.')
		mode_btn = wx.Button(self, ID_BUTTON + 3, "Mode(SYNC)")
	
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "From:",size=(50,-1))
		label.SetHelpText("Table copy source schema.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_from)[4:], size=(300,-1))
		text.Enable(False)
		#text.SetLabel()
		text.SetHelpText("Table copy SOURCE schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "To:",size=(50,-1))
		label.SetHelpText("Table copy target schema.")
		box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)

		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_to)[4:], size=(300,-1))
		text.Enable(False)
		text.SetHelpText("Table copy TARGET schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}

		self.listCtrl = EditableTextListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(650, 250))
		self.listCtrl.InsertColumn(0, 'From File')
		self.listCtrl.InsertColumn(1, 'To File (Editable)')
		#self.listCtrl.InsertColumn(2, '# of Shards')
		self.listCtrl.SetColumnWidth(0, 240)
		self.listCtrl.SetColumnWidth(1, 300)
		#self.listCtrl.SetColumnWidth(2, 100)
		for i in range(len(self.data)):
			item = self.data[i]
			
			#box.Add((10,5),0)
			tname=item[2].strip('[]')
			#tlabel= "From %s to:" % tname
			#label = wx.StaticText(self, -1,tlabel,size=(300,20))
			#label.SetHelpText("Target table.")
			#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

			#self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
			#self.tc_tables[tname].Enable(True)
			#self.tc_tables[tname].SetHelpText("Target table name")
			#self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
			#fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
			self.listCtrl.InsertStringItem(0, tname)
			self.listCtrl.SetStringItem(0, 1, tname)
			#self.listCtrl.SetStringItem(0, 2, 'Not sharded')



			
		sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_START, "Start")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		button2.Disable()
		ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		button4 = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(button1, 0)
		btnsizer.Add((10,5),0)
		btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(button4, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnTrial, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			btnsizer = wx.StdDialogButtonSizer()
			
			if wx.Platform != "__WXMSW__":
				btn = wx.ContextHelpButton(self)
				btnsizer.AddButton(btn)
			
			btn = wx.Button(self, wx.ID_OK)
			btn.SetHelpText("The OK button completes the dialog")
			btn.SetDefault()
			btnsizer.AddButton(btn)

			btn = wx.Button(self, wx.ID_CANCEL)
			btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
			btnsizer.AddButton(btn)
			btnsizer.Realize()

			sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
	def _OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
		
	def initParams(self):
		(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
	def OnExit(self,e):
		self.Close(True)
	def OnStart(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Start'
		self.Close(True)
		
class delete_TacoExecLogPanel(wx.Panel):
	"""Panel for the Taco exec log"""
	def __init__(self, parent, style,size):
		wx.Panel.__init__(self, parent, -1, style=style, size=size)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parentFrame=parent
		suffix=''
		self.label = wx.StaticText(self, -1, 'Started table copy.')
		#self.label.SetLabel("Hello World!")
		self.label.SetHelpText('Table copy status.')

		self.sizer.Add(self.label, 0, wx.GROW|wx.ALL, 5)

		self.nb = fnb.FlatNotebook(self, -1,size=(600,600), agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST)

			
		if 1:
			self.logger = TacoTextEditor(self)
			self.nb.AddPage(self.logger, 'Table Copy Log')
			self.config = TacoCodeEditor(self)
			self.nb.AddPage(self.config, 'pipeline_config.xml')
			self.worker = TacoCodeEditor(self)
			self.nb.AddPage(self.worker, 'pipeline_worker.xml')

		self.sizer.Add(self.nb, 1, wx.GROW|wx.EXPAND|wx.ALL, 5)
			
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_backgr = wx.Button(self, ID_BACKGROUND, "Background",size=(-1,20))
		self.btn_backgr.Disable()
		self.btn_stop = wx.Button(self, ID_STOP, "Stop", size=(50,20))

		#button2.Disable()
		self.btn_close = wx.Button(self, ID_EXIT, "Close", size=(50,20))
		self.btn_close.Disable()
		self.count=0
		self.gauge = wx.Gauge(self, -1, size=(200, 20),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
		if 1:
			i=wx.NewId()			
			self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
			
			self.timer=wx.Timer(self, id=i)
							
		#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
		#self.gauge[pos].SetPosition((1,1))
		btnsizer.Add((3,3),0)
		btnsizer.Add(self.gauge, 0)		
		btnsizer.Add((3,3),0)
		btnsizer.Add(self.btn_backgr, 0)
		btnsizer.Add((10,5),0)
		btnsizer.Add(self.btn_stop, 0)
		#btnsizer.Add((25,5),1)
		#btnsizer.Add(self.btn_trial, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)		
		btnsizer.Add(self.btn_close, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnBackground, id=ID_BACKGROUND)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
		
		#self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
		
		self.sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		self.timer.Start(100)
		
	def TimerHandler0(self, event,the_id):
		#(pos)=params
		#pos=self.timer_xref[the_id]
		#print 'the_id', the_id,pos
		self.count = self.count + 1

		if self.count >= 100:
			self.count = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		
		self.gauge.SetValue(self.count)
		#self.gauge.Pulse()
	def Status(self, msg):
		self.label.SetLabel(msg)
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)
	def OnExit(self,e):
		#Publisher().sendMessage( "refresh_list", (None) )
		send( "refresh_list", (None) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)
	def OnStop(self,e):
		#self.timer.Stop()
		self.btn_backgr.Disable()
		self.btn_stop.Disable()
		#self.btn_close.Enable(True)
		print 'OnStop'
		#Publisher().sendMessage( "stop_table_copy_process", ('Kill TC thread') )
		send("stop_table_copy_process", ('Kill TC thread') )
		
	def OnBackground(self,e):
		print 'OnBackground'
		
class F2FExecLogPanel(wx.Panel):
	"""Panel for the Taco exec log"""
	def __init__(self, parent, style,size,drop_pos):
		wx.Panel.__init__(self, parent, -1, style=style, size=size)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parentFrame=parent
		suffix=''
		self.label = wx.StaticText(self, -1, 'Started file copy.')
		#self.label.SetLabel("Hello World!")
		self.label.SetHelpText('Table copy status.')
		
		self.sizer.Add(self.label, 0, wx.GROW|wx.ALL, 5)

		self.nb = fnb.FlatNotebook(self, -1,size=(600,400), agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST)
		self.drop_pos=drop_pos
			
		if 1:
			self.logger = TacoCodeEditor(self)
			self.nb.AddPage(self.logger, 'File Copy Log')
			#self.config = TacoCodeEditor(self)
			#self.nb.AddPage(self.config, 'pipeline_config.xml')
			#self.worker = TacoCodeEditor(self)
			#self.nb.AddPage(self.worker, 'pipeline_worker.xml')

		self.sizer.Add(self.nb, 1, wx.GROW|wx.EXPAND|wx.ALL, 5)
			
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_backgr = wx.Button(self, ID_BACKGROUND, "Background",size=(-1,20))
		self.btn_backgr.Disable()
		self.btn_stop = wx.Button(self, ID_STOP, "Stop", size=(50,20))

		#button2.Disable()
		self.btn_close = wx.Button(self, ID_EXIT, "Close", size=(50,20))
		self.btn_close.Disable()
		self.count=0
		self.gauge = wx.Gauge(self, -1, size=(200, 20),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
		if 1:
			i=wx.NewId()			
			self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
			
			self.timer=wx.Timer(self, id=i)
							
		#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
		#self.gauge[pos].SetPosition((1,1))
		btnsizer.Add((3,3),0)
		btnsizer.Add(self.gauge, 0)		
		btnsizer.Add((3,3),0)
		btnsizer.Add(self.btn_backgr, 0)
		btnsizer.Add((10,5),0)
		btnsizer.Add(self.btn_stop, 0)
		#btnsizer.Add((25,5),1)
		#btnsizer.Add(self.btn_trial, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)		
		btnsizer.Add(self.btn_close, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnBackground, id=ID_BACKGROUND)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
		
		#self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
		
		self.sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 5)
		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		self.timer.Start(100)
		
	def TimerHandler0(self, event,the_id):
		#(pos)=params
		#pos=self.timer_xref[the_id]
		#print 'the_id', the_id,pos
		self.count = self.count + 1

		if self.count >= 100:
			self.count = 0
		#print self.count
		#self.gauge.Show()
		#print '||||||||||||||||| setting count', self.count
		
		self.gauge.SetValue(self.count)
		#self.gauge.Pulse()
	def Status(self, msg):
		self.label.SetLabel(msg)
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)
	def OnExit(self,e):
		#Publisher().sendMessage( "refresh_list", (self.drop_pos) )
		send("refresh_list", (self.drop_pos) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)
	def OnStop(self,e):
		#self.timer.Stop()
		self.btn_backgr.Disable()
		self.btn_stop.Disable()
		#self.btn_close.Enable(True)
		print 'OnStop'
		#Publisher().sendMessage( "stop_f2f_copy_process", ('Kill f2f thread') )
		send( "stop_f2f_copy_process", ('Kill f2f thread') )
		
	def OnBackground(self,e):
		print 'OnBackground'
		
class delete_TableCopyProgressDialog(wx.MiniFrame):
	def __init__(
			self, parent, ID, title ,   size, pos=wx.DefaultPosition,
                 
                 style=wx.SYSTEM_MENU | wx.CAPTION | wx.MAXIMIZE_BOX | wx.FRAME_NO_TASKBAR| wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN
			):
		wx.MiniFrame.__init__(self, parent, ID, title, pos, size, style)
		#wx.Frame.__init__(self, parent, -1, title, size=size)
		
		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		#self.parent=parent
		#pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		#pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		#self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		#if 'wxMac' in wx.PlatformInfo and useMetal:
		#	self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		
		panel = TacoExecLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
		self.panel=panel

		#self.status='Exit'
		#self.gauge[pos].Show()
		#self.btn_stop[pos].Show()
		self.bs = wx.BoxSizer(wx.VERTICAL)
		self.bs.Add(self.panel, 1, wx.EXPAND|wx.ALL)
		self.SetSizer(self.bs)
		self.bs.Fit(self)
		self.SetSize((750, 500))
		self.CenterOnScreen()
		self.Update()
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.MakeModal()

	def onClose(self, event):
		"""
		Make the frame non-modal as it closes to re-enable other windows
		"""
		self.MakeModal(False)
		self.Destroy()
		
	def Status(self, msg):
		self.panel.Status(msg)		
class F2FCopyProgressDialog(wx.MiniFrame):
	def __init__(
			self, parent, ID, title , style, drop_pos, pos=wx.DefaultPosition,
                 size=(750, 500)
                # style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.FRAME_NO_TASKBAR| wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN
			):
		wx.MiniFrame.__init__(self, parent, ID, title, pos, size, style)
		#wx.Frame.__init__(self, parent, -1, title, size=size)
		
		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		#self.parent=parent
		#pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		#pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		#self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		#if 'wxMac' in wx.PlatformInfo and useMetal:
		#	self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		
		panel = F2FExecLogPanel(self, drop_pos=drop_pos,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 500))
		self.panel=panel

		#self.status='Exit'
		#self.gauge[pos].Show()
		#self.btn_stop[pos].Show()
		self.bs = wx.BoxSizer(wx.VERTICAL)
		self.bs.Add(self.panel, 1, wx.EXPAND|wx.ALL)
		self.SetSizer(self.bs)
		self.bs.Fit(self)
		self.SetSize((750, 500))
		self.CenterOnScreen()
		self.Update()
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.MakeModal()

	def onClose(self, event):
		"""
		Make the frame non-modal as it closes to re-enable other windows
		"""
		self.MakeModal(False)
		self.Destroy()
		
	def Status(self, msg):
		self.panel.Status(msg)	

#----------------------------------------------------------------------
# Thread class that executes processing
class ExecThread(Thread):
	"""Exec Table Copy Thread Class."""
	def __init__(self,create_spec,create_worker, is_trial=False):
		"""Init Exec Table Copy Thread Class."""
		Thread.__init__(self)
		(self.cfrom,self.cto,self.pos_from,self.pos_to,self.xml_config) = create_spec
		(self.xml_worker, self.table_to, self._tcmode) = create_worker
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		self.is_trial=is_trial
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()

	def run(self):
		"""Run Exec Table Copy Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable
		#print self.q, self.user,self.limit
		
		#self.result=dbu.query(self.q, (self.user,self.sid,self.pwd), self.limit)
		if 1:		
			(username, password, hostname) = tc_host[tc_srv]
			#Publisher().sendMessage( "copy_status", ('Connected to %s.' % (hostname),0) )
			send("copy_status", ('Connected to %s.' % (hostname),0) )
			(local_path,remote_path, config_file)= createPipelineConfig(self.cfrom,self.cto,self.xml_config)
			config_loc='%s%s' % (remote_path, config_file)
			#Publisher().sendMessage( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
			send( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
			#Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
			send( "created_config_file", (os.path.join(local_path,config_file)) )
			
			#count += 10
			#dlg.Update(count)
			xml_worker='tc_copy_test.xml'
			(out_dir,worker_file,remote_loc)= createPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker, self.table_to, self._tcmode )
			worker_loc='%s%s' % (remote_loc,worker_file)
			#Publisher().sendMessage( "copy_status", ('Created worker file at %s.' %  worker_loc,0) )
			send( "copy_status", ('Created worker file at %s.' %  worker_loc,0) )
			#Publisher().sendMessage( "created_worker_file", (os.path.join(out_dir,worker_file)) )
			send( "created_worker_file", (os.path.join(out_dir,worker_file)) )
			
			#count += 10
			#dlg.Update(count)
			#print self.getVarsToPath(self.drag_pos)
			#print self.getVarsToPath(self.drop_pos)
			#pprint (self.dd_data)
			#pprint(self.table_to)
			#Publisher().sendMessage( "show_tc_progress_dialog", ('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file)) )
			(out,err) =('',None)
			if not self.is_trial:
				#Publisher().sendMessage( "copy_status", ('Executing table copy...',0) )
				send("copy_status", ('Executing table copy...',0) )
				(out,err)=execTaCo(config_loc,worker_loc)
				#Publisher().sendMessage( "table_copy_done",  (out,err) )
			else:
				#(out,err)=('Trial run completed.', 0)				
				#Publisher().sendMessage( "copy_status", ('Deployment completed.',0) )
				send("copy_status", ('Deployment completed.',0) )
				#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
				
				#Publisher().sendMessage( "copy_status", ('#Execute at %s' % ( hostname) ,0) )
				
				(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
				#Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
				send("shell_code", ('cd %s' % tc_path,0) )
				#Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
				send("shell_code", ('. ./.ora_profile',0) )
				#Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )
				send("shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )
				#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
			if err and err.strip().startswith('real'):
				err=[]
				out='%s\n%s' % (out, err)
				
				True
			if self.is_trial:
				#Publisher().sendMessage( "tc_deployment_completed", (out,err,self.pos_to))
				send("tc_deployment_completed", (out,err,self.pos_to))
			#Publisher().sendMessage( "copy_done", (out,err,self.pos_to))
			send( "copy_done", (out,err,self.pos_to))
			
				
				

		# Here's where the result would be returned (this is an
		# example fixed result of the number 10, but it could be
		# any Python object)
		#self.db.result=42
		#Publisher().sendMessage( "table_copy_done", ('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file)) )

	def abort1(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		print 'DbThread aborted'
		#Publisher().sendMessage( "db_thread_event", ('aborted') )
		self.result=None
		#pprint(dir(Thread))
		#self.abort()
		#Thread.abort(self)
		#return
		#self._Thread__stop()

	def _get_my_tid(self):
		"""determines this (self's) thread id"""
		if not self.isAlive():
			raise threading.ThreadError("the thread is not active")
		
		# do we have it cached?
		if hasattr(self, "_thread_id"):
			return self._thread_id
		
		# no, look for it in the _active dict
		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = tid
				return tid
		
		raise AssertionError("could not determine the thread's id")
	
	def raise_exc(self, exctype):
		"""raises the given exception type in the context of this thread"""
		_async_raise(self._get_my_tid(), exctype)
	
	def terminate(self):
		"""raises SystemExit in the context of the given thread, which should 
		cause the thread to exit silently (unless caught)"""
		self.raise_exc(SystemExit)

def execF2FCopy(file_from,file_to, conn_from,conn_to):
	#print specs
	#print worker
	#plink_loc=r'C:\Users\zkqfas6\Installs\putty'
	#command = r"C:\Users\zkqfas6\Installs\putty\plink.exe -ssh zkqfas6@lrche25546 -pw %s cd tab_copy;time python tc.py --pipeline_spec=%s --pipeline=%s" % (lpwd, specs,worker)
	#status=os.popen(command).read()

	#remote_loc='/home/zkqfas6/tab_copy/pipeline/posix'
	#from_file ='/home/zkqfas6/in/10d_test.MRR_ETL_USER.TCL_baG3d0.data'
	#to_file=r'C:\Temp\TC\data\in'
	#os.system(r'echo %s|C:\Users\zkqfas6\Installs\putty\pscp.exe -C zkqfas6@lrche25546:%s %s' % (lpwd, from_file,to_file))
	#from_file ='C:\Temp\TC\data\10d_test.MRR_ETL_USER.TCL_baG3d0.data'
	print file_from
	print file_to
	print conn_from
	print conn_to	
	server_from='%s@%s:' % (conn_from[0],conn_from[1])
	if conn_from[1]=='localhost':
		server_from=''
	server_to='%s@%s:' % (conn_to[0],conn_to[1])
	if conn_to[1]=='localhost':
		server_to=''		
	#from_file ='C:\Temp\TC\data\proclamation.txt'	
	#to_file=r'zkqfas6@lrche25546:/home/zkqfas6/in'
	cmd='C:\Users\zkqfas6\Installs\putty\pscp.exe -C %s%s %s%s'  % (server_from,file_from,server_to,file_to)
	Publisher().sendMessage( "copy_status", ('Executing command:',0) )
	Publisher().sendMessage( "copy_status", (cmd,0) )
	Publisher().sendMessage( "copy_status", (file_from,0) )
	Publisher().sendMessage( "copy_status", (file_to,0) )

	out=os.system(r'echo %s|%s' % (lpwd,cmd ))
	err=''
	if 0:
		proc = subprocess.Popen(["C:\Users\zkqfas6\Installs\putty\plink.exe", "-ssh", "zkqfas6@lrche25546", "-pw", lpwd, "cd tab_copy;time python tc.py --pipeline_spec=%s --pipeline=%s" % (specs,worker)], stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
		output=' '
		out=[]
		status=0
		while output:
			output = proc.stdout.readline() #string.replace(p2.stdout.readline(),'SQL>','')
			print output
			out.append(output)
		error=' '
		err=[]
		while error:
			error = proc.stderr.readline()						
			err.append(error)
		print 'after communicate'
		print out
		print err
		if err:
			print '#'*20, ' ERROR ','#'*20
			print '###'.join(err)
			print '#'*20, ' ERROR ','#'*20
		#print "program output:", out

	return (out,err)
	
#----------------------------------------------------------------------
# Thread class that executes processing
class ExecF2FThread(Thread):
	"""Exec F2F Copy Thread Class."""
	def __init__(self,args, is_trial=False):
		"""Init Exec F2F Copy Thread Class."""
		Thread.__init__(self)
		(from_loc,to_loc, self.conn_from,self.conn_to,self.pos_to, self.fset) = args
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		self.is_trial=is_trial
		(fn_from, fn_to)=self.fset
		self.file_from='/'.join((from_loc,fn_from))
		self.file_to='/'.join((to_loc,fn_to))
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()

	def run(self):
		"""Run Exec F2F Copy Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable
		#print self.q, self.user,self.limit
		
		#self.result=dbu.query(self.q, (self.user,self.sid,self.pwd), self.limit)
		if 1:		
			#(local_path,remote_path, config_file)= createPipelineConfig(self.cfrom,self.cto,self.xml_config)
			#config_loc='%s/%s' % (remote_path, config_file)
			Publisher().sendMessage( "copy_status", ('Starting file copy.',0) )
			#Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
			
			#count += 10
			#dlg.Update(count)
			#xml_worker='tc_copy_test.xml'
			#(out_dir,worker_file,remote_loc)= createPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker, self.table_to )
			#worker_loc='%s/%s' % (remote_loc,worker_file)
			#Publisher().sendMessage( "copy_status", ('Created worker file.',0) )
			#Publisher().sendMessage( "created_worker_file", (os.path.join(out_dir,worker_file)) )
			
			#count += 10
			#dlg.Update(count)
			#print self.getVarsToPath(self.drag_pos)
			#print self.getVarsToPath(self.drop_pos)
			#pprint (self.dd_data)
			#pprint(self.table_to)
			#Publisher().sendMessage( "show_tc_progress_dialog", ('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file)) )
			(out,err) =('',None)
			(out,err)=execF2FCopy(self.file_from,self.file_to, self.conn_from,self.conn_to)
			#if not self.is_trial:
				#(out,err)=execTaCo(config_loc,worker_loc)
				#Publisher().sendMessage( "table_copy_done",  (out,err) )
			#else:
				#(out,err)=('Trial run completed.', 0)
			#	Publisher().sendMessage( "copy_status", ('Trial run completed.',0) )
			#Publisher().sendMessage( "copy_done", (self.pos_to))  
			Publisher().sendMessage( "copy_done", (out,err,self.pos_to))
				

		# Here's where the result would be returned (this is an
		# example fixed result of the number 10, but it could be
		# any Python object)
		#self.db.result=42
		#Publisher().sendMessage( "table_copy_done", ('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file)) )

	def abort1(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		print 'DbThread aborted'
		#Publisher().sendMessage( "db_thread_event", ('aborted') )
		self.result=None
		#pprint(dir(Thread))
		#self.abort()
		#Thread.abort(self)
		#return
		#self._Thread__stop()

	def _get_my_tid(self):
		"""determines this (self's) thread id"""
		if not self.isAlive():
			raise threading.ThreadError("the thread is not active")
		
		# do we have it cached?
		if hasattr(self, "_thread_id"):
			return self._thread_id
		
		# no, look for it in the _active dict
		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = tid
				return tid
		
		raise AssertionError("could not determine the thread's id")
	
	def raise_exc(self, exctype):
		"""raises the given exception type in the context of this thread"""
		_async_raise(self._get_my_tid(), exctype)
	
	def terminate(self):
		"""raises SystemExit in the context of the given thread, which should 
		cause the thread to exit silently (unless caught)"""
		self.raise_exc(SystemExit)
		
class OracleConnectDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		#self.initParams()
		suffix=''
		#if len(self.data)>1:
		#	suffix='s'
		label = wx.StaticText(self, -1, "Environment:" )
		label.SetHelpText('Use dropdown to set environment.')
		env=self.parent.getVarsToPath().split('/')[2]
		print env
		#sys.exit(1)
		
		mode_btn = wx.Button(self, ID_BUTTON + 3, env)
		mode_btn.Enable(False)
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
		#alias
		self.login_form=OrderedDict()
		self.login_form['username']=[('Username:', 50,"Username/schema."),('',100,"Type name of the user/schema")]
		self.login_form['password']=[('Password:', 50,"User Password."),('',80,"Type in user's password.",wx.TE_PASSWORD)]
		self.login_form['sid']=[('SID:', 50,"Oracle SID."),('',100,"Oracle server name (SID)")]
		self.login_form['host']=[('Host:', 50,"Host Name."),('',140,"Type Oracle host name (server).")]
		self.login_form['port']=[('Port:', 50,"Port number."),('',50,"Type connect port number.")]
		self.loginFormTxt={}
		#username
		for key, form in self.login_form.items():
			box = wx.BoxSizer(wx.HORIZONTAL)
			label = wx.StaticText(self, -1, form[0][0],size=(form[0][1],-1))
			label.SetHelpText(form[0][2])
			box.Add(label, 0, wx.ALIGN_LEFT, 0)
			if len(form[1])>3:
				self.loginFormTxt[key] = wx.TextCtrl(self, -1, form[1][0], size=(form[1][1],-1),style=form[1][3])
			else:
				self.loginFormTxt[key] = wx.TextCtrl(self, -1, form[1][0], size=(form[1][1],-1))
			self.loginFormTxt[key].Enable(True)
			#text.SetLabel()
			self.loginFormTxt[key].SetHelpText(form[1][2])
			box.Add(self.loginFormTxt[key], 0, wx.ALIGN_LEFT, 0)

			sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.tc_tables={}
		self.shards_btn={}





			
		#sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		btnAdd = wx.Button(self, ID_START, "Add")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		#ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		btnCancel = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		#btnsizer.Add((3,3),0)
		btnsizer.Add(btnAdd, 0)
		btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		#btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(btnCancel, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnAdd, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnTrial, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
		self.SetSize((210,-1))
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
		
	def initParams(self):
		pass
		#(self.pos_from)=(self.parent.focused_pos)
		#print 'init:', self.parent.focused_pos
		#print 'init:', 		self.parent.drop_pos
		#print 'init:', 		self.parent.dd_data
		
	def OnExit(self,e):
		self.Close(True)
	def OnAdd(self,e):
		self.table_to={}
		
		vals=OrderedDict()
		for key, form in self.login_form.items():
			vals[key] = self.loginFormTxt[key].GetLabel()
		#pprint (vals)
		#pprint(vals.keys())
		#pprint(vals.values())
		if 0:
			userTxt= self.userTxt.GetLabel()
			passwordTxt= self.passwordTxt.GetLabel()
			serverTxt = self.serverTxt.GetLabel()
			portTxt = self.serverTxt.GetLabel()
		config_file='%s.xml' % self.parent.getVarsToPath().split('/')[1]
		env=self.parent.getVarsToPath().split('/')[2]
		if self.parent.frame.ifConnectDups(config_file,env,vals,self.parent.pos):
			pass
		else:
			if not self.parent.frame.ifConnectValsSet(vals,self.parent.pos):
				pass
			else:
				self.parent.frame.addOracleConnect(config_file,env,vals,self.parent.pos)
				if 0:
					for i in range(len(self.data)):
						#item=self.data[i]
						#tname=item[2].strip('[]')				
						row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
						self.table_to[row[0]]=row
						#print  self.table_to[tname]
				self.status='Add'
				self.Close(True)

class EditOracleConnectDialog(wx.MiniFrame):
	def __init__(
			self, parent, ID, title, size,login, pos=wx.DefaultPosition, 
			style=wx.SYSTEM_MENU | wx.CAPTION | wx.MAXIMIZE_BOX | wx.FRAME_NO_TASKBAR| wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN,
			useMetal=False,	ifOpenConnect=False		
			):
		wx.MiniFrame.__init__(self, parent, ID, title, pos, size, style)
		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		self.login=login
		self.ifOpenConnect=ifOpenConnect
		self.SetBackgroundColour('#FFFFFF')
		if 0:
			pre = wx.PreDialog()
			pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
			pre.Create(parent, ID, title, pos, size, style)

			# This next step is the most important, it turns this Python
			# object into the real wrapper of the dialog (instead of pre)
			# as far as the wxPython extension is concerned.
			self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)
		
		self.statusbar = self.CreateStatusBar()
		#self.statusbar.SetWindowStyle(self.statusbar.GetWindowStyle() ^ wx.ST_SIZEGRIP)

		#font=self.statusbar.GetFont()
		#self.statusbar.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False))
		self.statusbar.SetForegroundColour(wx.RED)
		#self.statusbar.SetDefaultStyle(wx.TextAttr("red") )
		self.SetStatusBar(self.statusbar)
		#statictext = wx.StaticText(self.statusbar, -1, "Welcome To")
		
		if 0:
			font = self.GetStatusBar().GetFont() 
			font.SetWeight (wx.BOLD) 
			self.parent.GetStatusBar().SetFont(font) 
			self.parent.GetStatusBar().SetForegroundColour(wx.RED) 
		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		#self.initParams()
		suffix=''
		#if len(self.data)>1:
		#	suffix='s'
		label = wx.StaticText(self, -1, "Environment:" )
		label.SetHelpText('Use dropdown to set environment.')
		env=self.parent.getVarsToPath().split('/')[2]
		print env
		#sys.exit(1)
		(user,db,pwd,host,port)=login
		mode_btn = wx.Button(self, ID_BUTTON + 3, env)
		mode_btn.Enable(False)
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
		#alias
		self.login_form=OrderedDict()
		self.login_form['alias']=[('Title:', 50,"Connect title."),('%s_%s' %(user.strip(),db.strip()),100,"Title of a connect")]
		self.login_form['username']=[('Username:', 50,"Username/schema."),(user,100,"Type name of the user/schema")]
		self.login_form['password']=[('Password:', 50,"User Password."),(pwd,80,"Type in user's password.",wx.TE_PASSWORD)]
		self.login_form['sid']=[('SID:', 50,"Oracle SID."),(db,100,"Oracle server name (SID)")]
		self.login_form['host']=[('Host:', 50,"Host Name."),(host,140,"Type Oracle host name (server).")]
		self.login_form['port']=[('Port:', 50,"Port number."),(port,50,"Type connect port number.")]
		self.loginFormTxt={}
		#username
		for key, form in self.login_form.items():
			box = wx.BoxSizer(wx.HORIZONTAL)
			label = wx.StaticText(self, -1, form[0][0],size=(form[0][1],-1))
			label.SetHelpText(form[0][2])
			box.Add(label, 0, wx.ALIGN_LEFT, 0)
			if not form[1][0]:
				pass
				#self.statusbar.SetStatusText('"%s" is not set!' % key)
				statictext = wx.StaticText(self.statusbar, -1, '"%s" is not set!' % key)
			if len(form[1])>3:
				self.loginFormTxt[key] = wx.TextCtrl(self, -1, form[1][0].strip(), size=(form[1][1],-1),style=form[1][3])
			else:
				self.loginFormTxt[key] = wx.TextCtrl(self, -1, form[1][0], size=(form[1][1],-1))
			print self.loginFormTxt[key].GetLabel()
			self.loginFormTxt[key].Enable(True)
			#text.SetLabel()
			self.loginFormTxt[key].SetHelpText(form[1][2])
			box.Add(self.loginFormTxt[key], 0, wx.ALIGN_LEFT, 0)

			sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.loginFormTxt['alias'].Enable(False)
		self.tc_tables={}
		self.shards_btn={}





			
		#sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		ttl='Save'
		if self.ifOpenConnect:
			ttl='Save and Connect'
		btnAdd = wx.Button(self, wx.OK, ttl)
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		#ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		btnCancel = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		#btnsizer.Add((3,3),0)
		btnsizer.Add(btnAdd, 0)
		btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		#btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(btnCancel, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnSet, id=wx.OK)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnTrial, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
		self.SetSize((210,-1))
		self.out=self.login
		self.MakeModal()

	def onClose(self, event):
		"""
		Make the frame non-modal as it closes to re-enable other windows
		"""
		self.MakeModal(False)
		self.Destroy()
		
	#def Status(self, msg):
	#	self.panel.Status(msg)		
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
		
	def initParams(self):
		pass
		#(self.pos_from)=(self.parent.focused_pos)
		#print 'init:', self.parent.focused_pos
		#print 'init:', 		self.parent.drop_pos
		#print 'init:', 		self.parent.dd_data
		
	def OnExit(self,e):
		self.MakeModal(False)
		#Publisher().sendMessage( "set_env_list", (self.parent.pos) )
		send("set_env_list", (self.parent.pos) )
		self.Destroy()
		#self.Close(True)
		
	def OnSet(self,e):
		self.table_to={}
		
		vals={} #OrderedDict()
		for key, form in self.login_form.items():
			vals[key] = self.loginFormTxt[key].GetLabel()
		#pprint (vals)
		#pprint(vals.keys())
		#pprint(vals.values())
		if 0:
			userTxt= self.userTxt.GetLabel()
			passwordTxt= self.passwordTxt.GetLabel()
			serverTxt = self.serverTxt.GetLabel()
			portTxt = self.serverTxt.GetLabel()
		config_file='%s.xml' % self.parent.getVarsToPath().split('/')[1]
		env=self.parent.getVarsToPath().split('/')[2]
		self.parent.frame.setOracleConnect(config_file,env,vals,self.parent.pos)
		if 0:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print  self.table_to[tname]
		self.status='Add'
		self.MakeModal(False)
		self.out=(vals['username'],vals['password'],vals['sid'], vals['host'],vals['port'])
		#	
		#self.Close(True)
		if self.ifOpenConnect:
			#Publisher().sendMessage( "set_owner_list", (self.parent.pos,self.out) )
			send("set_owner_list", (self.parent.pos,self.out) )
		self.Destroy()	
		
class DeleteConnectDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.initParams()
		suffix=''
		if len(self.data)>1:
			suffix='s'
		label = wx.StaticText(self, -1, "Delete %d connection%s." % (len(self.data),suffix))
		label.SetHelpText('Number of connects to delete. \nPless "Cancel" button to exit.')
		#mode_btn = wx.Button(self, ID_BUTTON + 3, "Mode(SYNC)")
	
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		#mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "From:",size=(50,-1))
		label.SetHelpText("Table copy source schema.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath()[4:], size=(300,-1))
		text.Enable(False)
		#text.SetLabel()
		text.SetHelpText("Table copy SOURCE schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			box = wx.BoxSizer(wx.HORIZONTAL)

			label = wx.StaticText(self, -1, "To:",size=(50,-1))
			label.SetHelpText("Table copy target schema.")
			box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
			#print 'TableCopyDialog/pos_to:', self.pos_to
			text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_to)[4:], size=(300,-1))
			text.Enable(False)
			text.SetHelpText("Table copy TARGET schema")
			box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

			sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}
		if 0:
		
			box = wx.BoxSizer(wx.HORIZONTAL)
			fgs = wx.FlexGridSizer(len(self.data), 3)

			for i in range(len(self.data)):
				item = self.data[i]
				
				#box.Add((10,5),0)
				tname=item[2].strip('[]')
				tlabel= "From %s to:" % tname
				label = wx.StaticText(self, -1,tlabel,size=(300,20))
				label.SetHelpText("Target table.")
				#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

				self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
				self.tc_tables[tname].Enable(True)
				self.tc_tables[tname].SetHelpText("Target table name")
				self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
				fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
				#box.Add(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT)
				#box.Add((10,5),0)
				#box.Add(self.shards_btn[tname], 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)
				#box.Add((10,5),0)
			box.Add((7,5),0)	
			box.Add(fgs, 0, wx.ALIGN_CENTER_VERTICAL, 1)
			box.Add((4,5),0)
		self.listCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(250, 250))
		self.listCtrl.InsertColumn(0, 'Alias')
		self.listCtrl.InsertColumn(1, 'Username')
		self.listCtrl.InsertColumn(2, 'Oracle SID')
		self.listCtrl.SetColumnWidth(0, 140)
		self.listCtrl.SetColumnWidth(1, 100)
		self.listCtrl.SetColumnWidth(2, 100)
		for i in range(len(self.data)):
			item = self.data[i]
			
			#box.Add((10,5),0)
			tname=item[2].strip('[]')
			#tlabel= "From %s to:" % tname
			#label = wx.StaticText(self, -1,tlabel,size=(300,20))
			#label.SetHelpText("Target table.")
			#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

			#self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
			#self.tc_tables[tname].Enable(True)
			#self.tc_tables[tname].SetHelpText("Target table name")
			#self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
			#fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
			self.listCtrl.InsertStringItem(0, tname)
			self.listCtrl.SetStringItem(0, 1, item[4])
			self.listCtrl.SetStringItem(0, 2, item[5])



			
		sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		btnDelete = wx.Button(self, ID_START, "Delete")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		#ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		button4 = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(btnDelete, 0)
		btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(button4, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnDelete, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnTrial, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			btnsizer = wx.StdDialogButtonSizer()
			
			if wx.Platform != "__WXMSW__":
				btn = wx.ContextHelpButton(self)
				btnsizer.AddButton(btn)
			
			btn = wx.Button(self, wx.ID_OK)
			btn.SetHelpText("The OK button completes the dialogue")
			btn.SetDefault()
			btnsizer.AddButton(btn)

			btn = wx.Button(self, wx.ID_CANCEL)
			btn.SetHelpText("The Cancel button cancels the dialogue. (Cool, huh?)")
			btnsizer.AddButton(btn)
			btnsizer.Realize()

			sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				(config,env)=self.parent.getVarsToPath(self.pos_from).split('/')
				self.parent.deleteConnect('%s.xml' % config,env,row,self.parent.pos)
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
		
	def initParams(self):		
		if 1:
			(self.pos_from, self.data)=(self.parent.pos, self.parent.delete_conn)
			#print 'init:', self.parent.drag_pos
			#print 'init:', 		self.parent.drop_pos
			#print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def OnDelete(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				print self.parent.getVarsToPath().strip('/').split('/')
				(root,config,env)=self.parent.getVarsToPath().strip('/').split('/')
				print row
				self.parent.frame.deleteConnect('%s.xml' % config,env,row,self.parent.pos)
				
		self.status='Delete'
		self.Close(True)
		
		#Publisher().sendMessage( "refresh_list", (self.parent.pos) )
		send("refresh_list", (self.parent.pos) )
#import wx.aui

class ClearPasswordDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title, size, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE,
			useMetal=False,
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)


		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.initParams()
		suffix=''
		if len(self.data)>1:
			suffix='s'
		label = wx.StaticText(self, -1, "Clear %d password%s." % (len(self.data),suffix))
		label.SetHelpText('Number of passwords to clear. \nPless "Cancel" button to exit.')
		#mode_btn = wx.Button(self, ID_BUTTON + 3, "Mode(SYNC)")
	
		mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		mode_sizer.Add((6,6),0)
		#mode_sizer.Add(mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "From:",size=(50,-1))
		label.SetHelpText("Table copy source schema.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		text = wx.TextCtrl(self, -1, self.parent.getVarsToPath()[4:], size=(300,-1))
		text.Enable(False)
		#text.SetLabel()
		text.SetHelpText("Table copy SOURCE schema")
		box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			box = wx.BoxSizer(wx.HORIZONTAL)

			label = wx.StaticText(self, -1, "To:",size=(50,-1))
			label.SetHelpText("Table copy target schema.")
			box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
			#print 'TableCopyDialog/pos_to:', self.pos_to
			text = wx.TextCtrl(self, -1, self.parent.getVarsToPath(self.pos_to)[4:], size=(300,-1))
			text.Enable(False)
			text.SetHelpText("Table copy TARGET schema")
			box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 0)

			sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}
		if 0:
		
			box = wx.BoxSizer(wx.HORIZONTAL)
			fgs = wx.FlexGridSizer(len(self.data), 3)

			for i in range(len(self.data)):
				item = self.data[i]
				
				#box.Add((10,5),0)
				tname=item[2].strip('[]')
				tlabel= "From %s to:" % tname
				label = wx.StaticText(self, -1,tlabel,size=(300,20))
				label.SetHelpText("Target table.")
				#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

				self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
				self.tc_tables[tname].Enable(True)
				self.tc_tables[tname].SetHelpText("Target table name")
				self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
				fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
				#box.Add(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT)
				#box.Add((10,5),0)
				#box.Add(self.shards_btn[tname], 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)
				#box.Add((10,5),0)
			box.Add((7,5),0)	
			box.Add(fgs, 0, wx.ALIGN_CENTER_VERTICAL, 1)
			box.Add((4,5),0)
		self.listCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(250, 250))
		self.listCtrl.InsertColumn(0, 'Alias')
		self.listCtrl.InsertColumn(1, 'Username')
		self.listCtrl.InsertColumn(2, 'Oracle SID')
		self.listCtrl.SetColumnWidth(0, 140)
		self.listCtrl.SetColumnWidth(1, 100)
		self.listCtrl.SetColumnWidth(2, 100)
		for i in range(len(self.data)):
			item = self.data[i]
			
			#box.Add((10,5),0)
			tname=item[2].strip('[]')
			#tlabel= "From %s to:" % tname
			#label = wx.StaticText(self, -1,tlabel,size=(300,20))
			#label.SetHelpText("Target table.")
			#box.Add(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT)

			#self.tc_tables[tname] = wx.TextCtrl(self, -1, tname, size=(250,20))
			#self.tc_tables[tname].Enable(True)
			#self.tc_tables[tname].SetHelpText("Target table name")
			#self.shards_btn[tname] = wx.Button(self, 3000+i, "Shards(N/A)") #, size=(70,25)
			#fgs.AddMany([(label, 0, wx.GROW|wx.RIGHT|wx.ALIGN_RIGHT,3),(self.tc_tables[tname], 1,  wx.GROW|wx.LEFT|wx.ALIGN_LEFT,3),(self.shards_btn[tname], 0,wx.RIGHT| wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 1)])
			self.listCtrl.InsertStringItem(0, tname)
			self.listCtrl.SetStringItem(0, 1, item[4])
			self.listCtrl.SetStringItem(0, 2, item[5])



			
		sizer.Add(self.listCtrl, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)

		btnDelete = wx.Button(self, ID_START, "Clear")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		#ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Generate xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		button4 = wx.Button(self, ID_EXIT, "Cancel")
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(btnDelete, 0)
		btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		btnsizer.Add(button4, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnClear, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnTrial, id=ID_TRIAL)
		sizer.Add(btnsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			btnsizer = wx.StdDialogButtonSizer()
			
			if wx.Platform != "__WXMSW__":
				btn = wx.ContextHelpButton(self)
				btnsizer.AddButton(btn)
			
			btn = wx.Button(self, wx.ID_OK)
			btn.SetHelpText("The OK button completes the dialogue")
			btn.SetDefault()
			btnsizer.AddButton(btn)

			btn = wx.Button(self, wx.ID_CANCEL)
			btn.SetHelpText("The Cancel button cancels the dialogue. (Cool, huh?)")
			btnsizer.AddButton(btn)
			btnsizer.Realize()

			sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
	def OnTrial(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				(config,env)=self.parent.getVarsToPath(self.pos_from).split('/')
				self.parent.deleteConnect('%s.xml' % config,env,row,self.parent.pos)
				#print  self.table_to[tname]
		self.status='Trial'
		self.Close(True)
		
	def initParams(self):		
		if 1:
			(self.pos_from, self.data)=(self.parent.pos, self.parent.delete_conn)
			#print 'init:', self.parent.drag_pos
			#print 'init:', 		self.parent.drop_pos
			#print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def OnClear(self,e):
		self.table_to={}
	
		if 1:
			for i in range(len(self.data)):
				#item=self.data[i]
				#tname=item[2].strip('[]')				
				row=[self.listCtrl.GetItem(i, col).GetText() for col in range(self.listCtrl.GetColumnCount())]
				self.table_to[row[0]]=row
				#print self.parent.getVarsToPath().strip('/').split('/')
				(root,config,env)=self.parent.getVarsToPath().strip('/').split('/')
				#print '%s.xml' % config
				#print row
				#print env
				#sys.exit(1)
				self.parent.frame.clearConnectPassword('%s.xml' % config,env,row,self.parent.pos)
				#blog.log('Password cleared for %s/%s/%s' % (config,env,row[0]), self.parent.pos)		
		self.status='Delete'
		self.Close(True)
#import wx.aui

class AUIManager(aui.AuiManager):
	""" from MikeDriscoll's AUI AGW tutorial on wxPyWiki 
	suggested as a way to run multiple AUI instances """
	def __init__(self, managed_window):
		aui.AuiManager.__init__(self)
		self.SetManagedWindow(managed_window)
		
########################################################################
class TzPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent, panels,panel_pos):
		""""""

		wx.Panel.__init__(self, parent,  id=wx.ID_ANY)

		self._mgr = AUIManager(self)
		# create several text controls
		#text1 = wx.TextCtrl(self, -1, 'Pane 1 - sample text',
		#					wx.DefaultPosition, wx.Size(500,500),
		#					wx.NO_BORDER | wx.TE_MULTILINE)
		self.panel_pos=panel_pos
		self.panels=panels
		#self.qp=QueryPanel(self, ignore_change)
		#self.rp=ResultsNbPanel(self)
		self.parent=parent
		#text2 = wx.TextCtrl(self, -1, 'Pane 2 - sample text',
		#					wx.DefaultPosition, wx.Size(50,300),
		#					wx.NO_BORDER | wx.TE_MULTILINE)
		#self.grid = SimpleGrid(self, sys.stdout)
		#text3 = wx.TextCtrl(self, -1, 'Main content window',
		#					wx.DefaultPosition, wx.Size(50,100),
		#					wx.NO_BORDER | wx.TE_MULTILINE)
		
		# add the panes to the manager
		#self._mgr.AddPane(self.qp, wx.CENTER)
		#self._mgr.AddPane(self.rp, wx.CENTER)
		#self._mgr.AddPane(text3, wx.CENTER)
		self._mgr.AddPane(self.panels[self.panel_pos[0]], AuiPaneInfo().Left().Caption("Pane Number One"))
		self._mgr.AddPane(self.panels[self.panel_pos[1]], AuiPaneInfo().Left().Caption("Pane Number One"))
		# tell the manager to 'commit' all the changes just made
		self._mgr.Update()
	def OnMaximize(self, evt):
		info = self.mgr.GetPane("Notebook")
		if info.IsMaximized():
			self.mgr.RestorePane(info)
		else:
			self.mgr.RestoreMaximizedPane()
			self.mgr.MaximizePane(info)
		self.mgr.Update()		
	def UnChange(self):
		print 'unchanging tp'
		self.qp.UnChange()
	def NoticeChange(self):
		self.qp.NoticeChange()

class EmptyPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, id=wx.NewId())	

class TransferListCtrl(ULC.UltimateListCtrl):

	def __init__(self, parent, log):

		ULC.UltimateListCtrl.__init__(self, parent, -1,
									  agwStyle=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|ULC.ULC_SHOW_TOOLTIPS|ULC.ULC_SINGLE_SEL) # |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT

		self.log = log
		self.InsertColumn(0, 'Id')
		self.InsertColumn(1, 'Time')
		self.InsertColumn(2, 'File')
		offset=3
		self.InsertColumn(0+offset, 'Source Name')
		self.InsertColumn(1+offset, 'Source Type')
		self.InsertColumn(2+offset, 'Source Object')
		self.InsertColumn(3+offset, 'Destination Object')
		self.InsertColumn(4+offset, 'Size')
		self.InsertColumn(5+offset, 'Status')
		self.InsertColumn(6+offset, 'Speed')
		self.InsertColumn(7+offset, 'Elapsed')
		#self.SetColumnWidth(0, 50)
		#self.SetColumnWidth(1, 600)
		self.SetColumnWidth(0, 30)
		self.SetColumnWidth(1, 75)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(0+offset, 150)
		self.SetColumnWidth(1+offset, 80)
		self.SetColumnWidth(2+offset, 310)
		self.SetColumnWidth(3+offset, 310)
		self.SetColumnWidth(4+offset, 50)
		self.SetColumnWidth(5+offset, 70)
		self.SetColumnWidth(6+offset, 70)
		self.SetColumnWidth(7+offset, 70)
		
		if 0:
			self.SetColumnWidth(0+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(1+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(2+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(3+offset, ULC.ULC_AUTOSIZE_FILL)	
			self.SetColumnWidth(4+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(5+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(6+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(7+offset, ULC.ULC_AUTOSIZE_FILL)		
		self.SetColumnToolTip(0,"Timestamp")
		self.SetColumnToolTip(1,"Log Message")
		#self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.id=1
		if 0:
			#self.listCtrl_t.InsertStringItem(0, '/'.join(spath.split('/')[3:5]))
			self.InsertStringItem(0, '1')
			#self.listCtrl.InsertStringItem(0, prof)
			self.SetStringItem(0, 1, 'test message')		
		if 0:
			self.il = wx.ImageList(16, 16)
			self.il.Add(images.Smiles.GetBitmap())
			self.il.Add(images.core.GetBitmap())
			self.il.Add(images.custom.GetBitmap())
			self.il.Add(images.exit.GetBitmap())
			self.il.Add(images.expansion.GetBitmap())

			self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

			self.InsertColumn(0, "First")
			self.InsertColumn(1, "Second")
			self.InsertColumn(2, "Third")
			self.SetColumnWidth(0, 175)
			self.SetColumnWidth(1, 175)
			self.SetColumnWidth(2, 175)
			self.SetColumnToolTip(0,"First Column Tooltip!")
			self.SetColumnToolTip(1,"Second Column Tooltip!")
			self.SetColumnToolTip(2,"Third Column Tooltip!")

			# After setting the column width you can specify that 
			# this column expands to fill the window. Only one
			# column may be specified.
			self.SetColumnWidth(2, ULC.ULC_AUTOSIZE_FILL)

			self.SetItemCount(1000000)
			
			self.attr1 = ULC.UltimateListItemAttr()
			self.attr1.SetBackgroundColour(wx.NamedColour("yellow"))

			self.attr2 = ULC.UltimateListItemAttr()
			self.attr2.SetBackgroundColour(wx.NamedColour("light blue"))

		#self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

		#self.randomLists = [GenerateRandomList(self.il) for i in xrange(5)] 
		self.idx={}
	def append(self,  msg):
		#items=self.GetItemCount()
		print msg[0]
		run_id=msg[0][0][1]
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		if len(msg)>0:
			self.appendList(run_id,now,msg)

		self._mainWin.MoveToItem(self.GetItemCount()-1)
	def update(self, msg):
		((panel_ID, run_id), elapsed,err,status)=msg
		print self.idx
		print (panel_ID, run_id)
		print 		elapsed,err
		#self.idx[run_id]
		#status='Completed'
		print status
		#sys.exit(1)
		
						
		#self.SetItem(item)
		if 1:
			item=self.GetItem(self.idx[run_id], 10)
			item.SetHyperText(False)
			item.SetText(elapsed)
			
			self.SetItem(item)
			
		#self.SetStringItem(self.idx[run_id], 9, elapsed)

		item=self.GetItem(self.idx[run_id], 8)
		item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
		if err:		
			clr=wx.Colour(255, 168, 168, 255)
			status='Error'
		else:
			clr=wx.Colour(128, 255, 128, 255) # wx.Colour(128, 255, 255, 255)
		item.SetBackgroundColour(clr)
		self.SetItem(item)
		if 0:
			item=self.GetItem(self.idx[run_id], 7)
			item.SetText(status)
			#item.SetHyperText(True)
			self.SetItem(item)
			#self.SetHyperTextItem(self.idx[run_id], 7, 'Completed')
		item=self.GetItem(self.idx[run_id], 8)
		item.SetText('')
		item.SetHyperText(True)
		#self.SetItem(item)
		#print 
		if status in 'Completed':
			elapsed=self.GetItem(self.idx[run_id], 1)
			print 'elapsed=',elapsed
			url='%s_%s_%s' % (panel_ID,run_id,elapsed.GetText())
			print url
			ul=hl.HyperLinkCtrl(self, -1, status,  URL=url)
			ul.AutoBrowse(False)
			ul.SetColours("BLUE", "BLUE", "BLUE")
			
			ul.EnableRollover(True)
			ul.SetUnderlines(False, False, True)
			#ul.SetBold(True)
			ul.OpenInSameWindow(False)
			ul.SetToolTip(wx.ToolTip('Click to see XML files'))
			ul.UpdateLink()
			#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
			ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)	
			item.SetWindow(ul)
			
			self.SetItem(item)	
		#item = self.list.GetItem(11, 0)
		#textctrl = wx.TextCtrl(self.list, -1, "I Am A Simple\nMultiline wx.TexCtrl", style=wx.TE_MULTILINE)
		
		#self.list.SetItem(item) 
		print 'status =',status
			
	def OnLink(self, event):
		#ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
		#print dir(event)
		loc=event.GetEventObject().GetURL()
		var=event.GetEventObject().GetLabel()
		
		#print 'aaaaaaaaaaaaaaaaaaaaaaa', loc, var
		#item=self.GetItem(self.idx[run_id], 7)
		send('open_xml_viewer',loc.split('_'))
		#event.Skip()				
	def appendErr(self, msg):
		#items=self.GetItemCount()
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		
		if type(msg) == types.ListType:
			self.appendList(run_id,now,msg, True)
		else:
			charge=msg.split(r'\n')
			self.appendList(run_id,now,charge, True)
		self._mainWin.MoveToItem(self.GetItemCount()-1)	
	def appendList(self, run_id,now,charge, if_error=False):
		#pprint(charge)
		items=self.GetItemCount()
		self.idx[run_id]=items
		print run_id
		print self.idx
		#sys.exit(1)
		if len(charge)>1:
			for m in charge:
				self.InsertStringItem(items, str(items+1))
				self.SetStringItem(items, 1, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				#msg = m.strip('\n')
				msg=m
				if msg:
					self.SetStringItem(items, 2, msg)
					if 0 and if_error:
						item = self.GetItem(items,1)
						item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
						pink=wx.Colour(255, 168, 168, 255)
						item.SetBackgroundColour(pink)
						self.SetItem(item)
					items +=1
		else:

			#msg =charge[0].strip()
			msg =charge[0]
			
			if msg:	
				index=self.InsertStringItem(items, '%s/%s' % ((items+1),run_id))
				self.SetStringItem(index, 1, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				#self.InsertStringItem(items, )
				offset=2
				#run_id=index #msg[0]
				#self.idx[run_id]=items
				for mid in range(len(msg)-1):
					m=msg[mid+1]
					self.SetStringItem(index, offset+mid, str(m))
				if 1:
					item=self.GetItem(index, 8)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					clr=wx.Colour(128, 255, 255, 255)
					item.SetBackgroundColour(clr)
					self.SetItem(item)
					#self.SetItemHyperText(item)
					#item=self.GetItem(index, 7)
					#self.SetItemText(item,'test')
				if 0 and if_error:
					item = self.GetItem(items,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					item.SetBackgroundColour('#FAAFBE')
					self.SetItem(item)
			
	def scrollDown(self):
		if self.logList.GetItemCount():
			self.logList._mainWin.MoveToItem(self.logList.GetItemCount()-1)

class DeploymentListCtrl(ULC.UltimateListCtrl):

	def __init__(self, parent, log):

		ULC.UltimateListCtrl.__init__(self, parent, -1,
									  agwStyle=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|ULC.ULC_SHOW_TOOLTIPS|ULC.ULC_SINGLE_SEL) # |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT

		self.log = log
		self.InsertColumn(0, 'Id')
		self.InsertColumn(1, 'Time')
		self.InsertColumn(2, 'File')
		offset=3
		self.InsertColumn(0+offset, 'Source Name')
		self.InsertColumn(1+offset, 'Source Type')
		self.InsertColumn(2+offset, 'Source Object')
		self.InsertColumn(3+offset, 'Destination Object')
		#self.InsertColumn(4+offset, 'Size')
		self.InsertColumn(4+offset, 'Status')
		#self.InsertColumn(6+offset, 'Speed')
		self.InsertColumn(5+offset, 'Elapsed')
		#self.SetColumnWidth(0, 50)
		#self.SetColumnWidth(1, 600)
		self.SetColumnWidth(0, 30)
		self.SetColumnWidth(1, 75)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(0+offset, 150)
		self.SetColumnWidth(1+offset, 80)
		self.SetColumnWidth(2+offset, 310)
		self.SetColumnWidth(3+offset, 310)
		#self.SetColumnWidth(4+offset, 50)
		self.SetColumnWidth(4+offset, 70)
		#self.SetColumnWidth(6+offset, 70)
		self.SetColumnWidth(5+offset, 70)
		
		if 0:
			self.SetColumnWidth(0+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(1+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(2+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(3+offset, ULC.ULC_AUTOSIZE_FILL)	
			self.SetColumnWidth(4+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(5+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(6+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(7+offset, ULC.ULC_AUTOSIZE_FILL)		
		self.SetColumnToolTip(0,"Timestamp")
		self.SetColumnToolTip(1,"Log Message")
		#self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.id=1
		if 0:
			#self.listCtrl_t.InsertStringItem(0, '/'.join(spath.split('/')[3:5]))
			self.InsertStringItem(0, '1')
			#self.listCtrl.InsertStringItem(0, prof)
			self.SetStringItem(0, 1, 'test message')		
		if 0:
			self.il = wx.ImageList(16, 16)
			self.il.Add(images.Smiles.GetBitmap())
			self.il.Add(images.core.GetBitmap())
			self.il.Add(images.custom.GetBitmap())
			self.il.Add(images.exit.GetBitmap())
			self.il.Add(images.expansion.GetBitmap())

			self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

			self.InsertColumn(0, "First")
			self.InsertColumn(1, "Second")
			self.InsertColumn(2, "Third")
			self.SetColumnWidth(0, 175)
			self.SetColumnWidth(1, 175)
			self.SetColumnWidth(2, 175)
			self.SetColumnToolTip(0,"First Column Tooltip!")
			self.SetColumnToolTip(1,"Second Column Tooltip!")
			self.SetColumnToolTip(2,"Third Column Tooltip!")

			# After setting the column width you can specify that 
			# this column expands to fill the window. Only one
			# column may be specified.
			self.SetColumnWidth(2, ULC.ULC_AUTOSIZE_FILL)

			self.SetItemCount(1000000)
			
			self.attr1 = ULC.UltimateListItemAttr()
			self.attr1.SetBackgroundColour(wx.NamedColour("yellow"))

			self.attr2 = ULC.UltimateListItemAttr()
			self.attr2.SetBackgroundColour(wx.NamedColour("light blue"))

		#self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

		#self.randomLists = [GenerateRandomList(self.il) for i in xrange(5)] 
		self.idx={}
	def append(self,  msg):
		#items=self.GetItemCount()
		print msg[0]
		run_id=msg[0][0][1]
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		if len(msg)>0:
			self.appendList(run_id,now,msg)

		self._mainWin.MoveToItem(self.GetItemCount()-1)
	def update(self, msg):
		((panel_ID, run_id), elapsed,err,status)=msg
		print self.idx
		print (panel_ID, run_id)
		print 		elapsed,err
		#self.idx[run_id]
		#status='Completed'

		
						
		#self.SetItem(item)
		if 1:
			print self.idx
			print run_id
			print panel_ID
			item=self.GetItem(self.idx[run_id], 8)
			item.SetHyperText(False)
			item.SetText(elapsed)
			
			self.SetItem(item)
			
		#self.SetStringItem(self.idx[run_id], 9, elapsed)

		item=self.GetItem(self.idx[run_id], 7)
		item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
		if err:		
			clr=wx.Colour(255, 168, 168, 255)
			status='Error'
		else:
			clr=wx.Colour(128, 255, 128, 255) # wx.Colour(128, 255, 255, 255)
		item.SetBackgroundColour(clr)
		self.SetItem(item)
		if 0:
			item=self.GetItem(self.idx[run_id], 7)
			item.SetText(status)
			#item.SetHyperText(True)
			self.SetItem(item)
			#self.SetHyperTextItem(self.idx[run_id], 7, 'Completed')
		item=self.GetItem(self.idx[run_id], 7)
		item.SetText('')
		item.SetHyperText(True)
		#self.SetItem(item)	
		if 1:
			elapsed=self.GetItem(self.idx[run_id], 1)
			
			ul=hl.HyperLinkCtrl(self, -1, status,  URL='%s_%s_%s' % (panel_ID,run_id,elapsed.GetText()))
			ul.AutoBrowse(False)
			ul.SetColours("BLUE", "BLUE", "BLUE")
			
			ul.EnableRollover(True)
			ul.SetUnderlines(False, False, True)
			#ul.SetBold(True)
			ul.OpenInSameWindow(False)
			ul.SetToolTip(wx.ToolTip('Click to see XML files'))
			ul.UpdateLink()
			#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
			ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)	
			item.SetWindow(ul)
			
			self.SetItem(item)	
		#item = self.list.GetItem(11, 0)
		#textctrl = wx.TextCtrl(self.list, -1, "I Am A Simple\nMultiline wx.TexCtrl", style=wx.TE_MULTILINE)
		
		#self.list.SetItem(item) 
			
	def OnLink(self, event):
		#ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)
		#print dir(event)
		loc=event.GetEventObject().GetURL()
		var=event.GetEventObject().GetLabel()
		
		#print 'aaaaaaaaaaaaaaaaaaaaaaa', loc, var
		#item=self.GetItem(self.idx[run_id], 7)
		send('open_xml_viewer',loc.split('_'))
		#event.Skip()				
	def appendErr(self, msg):
		#items=self.GetItemCount()
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		
		if type(msg) == types.ListType:
			self.appendList(run_id,now,msg, True)
		else:
			charge=msg.split(r'\n')
			self.appendList(run_id,now,charge, True)
		self._mainWin.MoveToItem(self.GetItemCount()-1)	
	def appendList(self, run_id,now,charge, if_error=False):
		#pprint(charge)
		items=self.GetItemCount()
		self.idx[run_id]=items
		print items
		print self.idx
		#sys.exit(1)
		if len(charge)>1:
			for m in charge:
				self.InsertStringItem(items, str(items+1))
				self.SetStringItem(items, 1, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				#msg = m.strip('\n')
				msg=m
				if msg:
					self.SetStringItem(items, 2, msg)
					if 0 and if_error:
						item = self.GetItem(items,1)
						item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
						pink=wx.Colour(255, 168, 168, 255)
						item.SetBackgroundColour(pink)
						self.SetItem(item)
					items +=1
		else:

			#msg =charge[0].strip()
			msg =charge[0]
			
			if msg:	
				index=self.InsertStringItem(items, '%s/%s' % ((items+1),run_id))
				self.SetStringItem(index, 1, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				#self.InsertStringItem(items, )
				offset=2
				#run_id=index #msg[0]
				
				for mid in range(len(msg)-1):
					m=msg[mid+1]
					self.SetStringItem(index, offset+mid, str(m))
				if 1:
					item=self.GetItem(index, 7)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					clr=wx.Colour(128, 255, 255, 255)
					item.SetBackgroundColour(clr)
					self.SetItem(item)
					#self.SetItemHyperText(item)
					#item=self.GetItem(index, 7)
					#self.SetItemText(item,'test')
				if 0 and if_error:
					item = self.GetItem(items,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					item.SetBackgroundColour('#FAAFBE')
					self.SetItem(item)
			
	def scrollDown(self):
		if self.logList.GetItemCount():
			self.logList._mainWin.MoveToItem(self.logList.GetItemCount()-1)
			
class DeploymentListCtrl_del(ULC.UltimateListCtrl):

	def __init__(self, parent, log):

		ULC.UltimateListCtrl.__init__(self, parent, -1,
									  agwStyle=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|ULC.ULC_SHOW_TOOLTIPS|ULC.ULC_SINGLE_SEL) # |ULC.ULC_HAS_VARIABLE_ROW_HEIGHT

		self.log = log
		self.InsertColumn(0, 'Id')
		self.InsertColumn(1, 'Time')
		offset=2
		self.InsertColumn(0+offset, 'Source Name')
		self.InsertColumn(1+offset, 'Source Type')
		self.InsertColumn(2+offset, 'Source Object')
		self.InsertColumn(3+offset, 'Destination Object')
		self.InsertColumn(4+offset, 'Size')
		self.InsertColumn(5+offset, 'Status')
		self.InsertColumn(6+offset, 'Speed')
		self.InsertColumn(7+offset, 'Elapsed')
		#self.SetColumnWidth(0, 50)
		#self.SetColumnWidth(1, 600)
		self.SetColumnWidth(0, 30)
		self.SetColumnWidth(1, 85)
		self.SetColumnWidth(0+offset, 150)
		self.SetColumnWidth(1+offset, 80)
		self.SetColumnWidth(2+offset, 310)
		self.SetColumnWidth(3+offset, 310)
		self.SetColumnWidth(4+offset, 50)
		self.SetColumnWidth(5+offset, 70)
		self.SetColumnWidth(6+offset, 70)
		self.SetColumnWidth(7+offset, 70)
		
		if 0:
			self.SetColumnWidth(0+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(1+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(2+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(3+offset, ULC.ULC_AUTOSIZE_FILL)	
			self.SetColumnWidth(4+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(5+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(6+offset, ULC.ULC_AUTOSIZE_FILL)
			self.SetColumnWidth(7+offset, ULC.ULC_AUTOSIZE_FILL)		
		self.SetColumnToolTip(0,"Timestamp")
		self.SetColumnToolTip(1,"Log Message")
		#self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		self.id=1
		if 0:
			#self.listCtrl_t.InsertStringItem(0, '/'.join(spath.split('/')[3:5]))
			self.InsertStringItem(0, '1')
			#self.listCtrl.InsertStringItem(0, prof)
			self.SetStringItem(0, 1, 'test message')		
		if 0:
			self.il = wx.ImageList(16, 16)
			self.il.Add(images.Smiles.GetBitmap())
			self.il.Add(images.core.GetBitmap())
			self.il.Add(images.custom.GetBitmap())
			self.il.Add(images.exit.GetBitmap())
			self.il.Add(images.expansion.GetBitmap())

			self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

			self.InsertColumn(0, "First")
			self.InsertColumn(1, "Second")
			self.InsertColumn(2, "Third")
			self.SetColumnWidth(0, 175)
			self.SetColumnWidth(1, 175)
			self.SetColumnWidth(2, 175)
			self.SetColumnToolTip(0,"First Column Tooltip!")
			self.SetColumnToolTip(1,"Second Column Tooltip!")
			self.SetColumnToolTip(2,"Third Column Tooltip!")

			# After setting the column width you can specify that 
			# this column expands to fill the window. Only one
			# column may be specified.
			self.SetColumnWidth(2, ULC.ULC_AUTOSIZE_FILL)

			self.SetItemCount(1000000)
			
			self.attr1 = ULC.UltimateListItemAttr()
			self.attr1.SetBackgroundColour(wx.NamedColour("yellow"))

			self.attr2 = ULC.UltimateListItemAttr()
			self.attr2.SetBackgroundColour(wx.NamedColour("light blue"))

		#self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		#self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

		#self.randomLists = [GenerateRandomList(self.il) for i in xrange(5)] 
		self.idx={}
	def append(self, msg):
		run_id=msg[0][0][1]
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		if len(msg)>0:
			self.appendList(run_id,now,msg)

		self._mainWin.MoveToItem(self.GetItemCount()-1)
	def update(self, msg):
		((panel_ID, run_id), elapsed,err)=msg
		print self.idx
		#self.idx[run_id]
		status='Completed'
		item=self.GetItem(self.idx[run_id], 7)
		item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
		if err:		
			clr=wx.Colour(255, 168, 168, 255)
			status='Error'
		else:
			clr=wx.Colour(128, 255, 128, 255) # wx.Colour(128, 255, 255, 255)
		item.SetBackgroundColour(clr)
		self.SetItem(item)
			
		#item=self.GetItem(self.idx[run_id], 7)
		item.SetText('')
		item.SetHyperText(True)
		self.SetItem(item)
		
		print item
		
		if 1:
			ul=hl.HyperLinkCtrl(self, -1, 'Completed',  URL='test')
			ul.AutoBrowse(False)
			ul.SetColours("BLUE", "BLUE", "BLUE")
			ul.EnableRollover(True)
			ul.SetUnderlines(False, False, True)
			#ul.SetBold(True)
			ul.OpenInSameWindow(True)
			ul.SetToolTip(wx.ToolTip("Click to explore %s" % 'Test'))
			ul.UpdateLink()
			#self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
			#ul.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLink)					
		#self.SetItem(item)
		#pprint(dir(item))
		item=self.GetItem(self.idx[run_id], 9)
		item.SetText(elapsed)
		item.SetHyperText(False)
		self.SetItem(item)
		
		print panel_ID, run_id

				
	def appendErr(self,run_id, msg):
		#items=self.GetItemCount()
		now=datetime.datetime.now()
		
		#self.listCtrl.InsertStringItem(0, prof)
		#print diR(t
		
		if type(msg) == types.ListType:
			self.appendList(run_id,now,msg, True)
		else:
			charge=msg.split(r'\n')
			self.appendList(run_id,now,charge, True)
		self._mainWin.MoveToItem(self.GetItemCount()-1)	
	def appendList(self, run_id,now,charge, if_error=False):
		#pprint(charge)
		items=self.GetItemCount()
		if len(charge)>1:
			for m in charge:
				self.InsertStringItem(items, str(items+1))
				self.SetStringItem(items, 1, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				#msg = m.strip('\n')
				msg=m
				if msg:
					self.SetStringItem(items, 2, msg)
					if 0 and if_error:
						item = self.GetItem(items,1)
						item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
						pink=wx.Colour(255, 168, 168, 255)
						item.SetBackgroundColour(pink)
						self.SetItem(item)
					items +=1
		else:

			#msg =charge[0].strip()
			msg =charge[0]
			
			if msg:	
				index=self.InsertStringItem(items, '%s/%s' % ((items+1),run_id))
				self.SetStringItem(index, 1, "%02d:%02d:%02d.%02d" % (now.hour,now.minute,now.second,now.microsecond/100))
				#self.InsertStringItem(items, )
				offset=2
				#run_id=index #msg[0]
				self.idx[run_id]=items
				for mid in range(len(msg)-1):
					m=msg[mid+1]
					self.SetStringItem(index, offset+mid, str(m))
				if 1:
					item=self.GetItem(index, 7)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					clr=wx.Colour(128, 255, 255, 255)
					item.SetBackgroundColour(clr)
					self.SetItem(item)
				if 0 and if_error:
					item = self.GetItem(items,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					item.SetBackgroundColour('#FAAFBE')
					self.SetItem(item)
			
	def scrollDown(self):
		if self.logList.GetItemCount():
			self.logList._mainWin.MoveToItem(self.logList.GetItemCount()-1)

			
class TransferLogger(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent,  style=1):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent=parent
		#self.pos=pos
		#self.parentFrame=parent.frame
		#suffix=''
		#self.label = wx.StaticText(self, -1, 'Started code deployment.')
		#self.label.SetLabel("Hello World!")
		#self.label.SetHelpText('Deployment status.')
		self.log=cu.NullLog()
		self.logList = TransferListCtrl(self,self.log)
		#print dir(self.logList)
		if 0:
			for i in range(100):
				self.logList.append('test %d' % i)
		self.sizer.Add(self.logList, 1, wx.GROW|wx.ALL, 1)

		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		print self.logList._mainWin
		#Publisher().subscribe(self.OnAppendTransferLog, "append_transfer_log")
		#Publisher().subscribe(self.OnUpdateTransferLog, "update_transfer_log")
		sub(self.__OnAppendTransferLog, "append_transfer_log")
		sub(self.__OnUpdateTransferLog, "update_transfer_log")
		#sub(self.__OnAppendDeploymentLog, "append_deployment_log")
		#sub(self.__OnUpdateDeploymentLog, "update_deployment_log")
		
		#Publisher().subscribe(self.OnAppendErr, "append_err")
	def Status(self, msg):
		self.label.SetLabel(msg)
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)
	def OnAppendTransferLog_del(self, evt):
		(msg) = evt.data
		if 1: # or pos==self.pos:
			self.logList.append(msg)
	def OnUpdateTransferLog_del(self, evt):
		(msg) = evt.data
		if 1: # or pos==self.pos:
			self.logList.update(msg)
	def __OnAppendTransferLog(self, data, extra1, extra2=None):
		(msg) = data
		#run_id=msg[0][0][1]
		print msg
		#print run_id
		#sys.exit(1)
		if 1: # or pos==self.pos:
			self.logList.append(msg)
	def __OnUpdateTransferLog(self, data, extra1, extra2=None):
		print '__OnUpdateTransferLog'
		(msg) = data
		#run_id=msg[0][0][1]
		#print msg
		#sys.exit(1)
		if 1: # or pos==self.pos:
			self.logList.update(msg)			
	def OnAppendErr_(self, evt):
		(msg,pos) = evt.data
		if pos==self.pos:
			self.logList.appendErr(msg)			
	def OnExit_(self,e):
		#Publisher().sendMessage( "refresh_list", (None) )
		send("refresh_list", (None) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'

class DeploymentLogger(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent,  style=1):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent=parent
		#self.pos=pos
		#self.parentFrame=parent.frame
		#suffix=''
		#self.label = wx.StaticText(self, -1, 'Started code deployment.')
		#self.label.SetLabel("Hello World!")
		#self.label.SetHelpText('Deployment status.')
		self.log=cu.NullLog()
		self.logList = DeploymentListCtrl(self,self.log)
		#print dir(self.logList)
		if 0:
			for i in range(100):
				self.logList.append('test %d' % i)
		self.sizer.Add(self.logList, 1, wx.GROW|wx.ALL, 1)

		self.SetSizer(self.sizer)
		self.sizer.Fit(self)
		print self.logList._mainWin
		#Publisher().subscribe(self.OnAppendTransferLog, "append_transfer_log")
		#Publisher().subscribe(self.OnUpdateTransferLog, "update_transfer_log")
		#sub(self.__OnAppendTransferLog, "append_transfer_log")
		#sub(self.__OnUpdateTransferLog, "update_transfer_log")
		sub(self.__OnAppendDeploymentLog, "append_deployment_log")
		sub(self.__OnUpdateDeploymentLog, "update_deployment_log")
		
		#Publisher().subscribe(self.OnAppendErr, "append_err")
	def Status(self, msg):
		self.label.SetLabel(msg)
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)
	def OnAppendTransferLog_del(self, evt):
		(msg) = evt.data
		if 1: # or pos==self.pos:
			self.logList.append(msg)
	def OnUpdateTransferLog_del(self, evt):
		(msg) = evt.data
		#run_id=msg[0][0][1]
		if 1: # or pos==self.pos:
			self.logList.update(msg)
	def __OnAppendDeploymentLog(self, data, extra1, extra2=None):
		(msg) = data
		#run_id=msg[0][0][1]
		if 1: # or pos==self.pos:
			self.logList.append(msg)
	def __OnUpdateDeploymentLog(self, data, extra1, extra2=None):
		(msg) = data
		#run_id=msg[0][0][1]
		if 1: # or pos==self.pos:
			self.logList.update(msg)			
	def OnAppendErr_(self, evt):
		(msg,pos) = evt.data
		if pos==self.pos:
			self.logList.appendErr(msg)			
	def OnExit_(self,e):
		#Publisher().sendMessage( "refresh_list", (None) )
		send("refresh_list", (None) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'
	
class TransferPannel(wx.Panel):
	"""Panel for copy config"""
	def __init__(self, parent,style):
		wx.Panel.__init__(self, parent, -1, style=style)
		#self.data=data
		#self.frame=parent.frame
		#self.pos=pos
		#self.panel_pos
		#ID_TC_MODE = wx.NewId()
		#ID_RUN_AT = wx.NewId()
		sizer = wx.BoxSizer(wx.VERTICAL)
		#(self.source, self.target)=sides
		#box = wx.BoxSizer(wx.HORIZONTAL)

		#self.spath=spath
		#self.tpath=tpath
		#print dir(fnb)
		#self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_NO_X_BUTTON|fnb.FNB_NO_NAV_BUTTONS)
		#self.nb = wx.aui.AuiNotebook(self, -1, style=wx.aui.AUI_NB_TAB_SPLIT |wx.aui.AUI_NB_RIGHT	)
		self.nb = wx.Notebook(self, -1, style=wx.NB_RIGHT	)

		#NB_RIGHT
		#wx.aui.AUI_NB_LEFT		

		self.log = TransferLogger(self.nb) 
		self.nb.AddPage(self.log, 'Copy')
		self.dlog = DeploymentLogger(self.nb) 
		self.nb.AddPage(self.dlog, 'Deploy')
			
		sizer.Add(self.nb,1,wx.EXPAND)
		
		self.SetSizer(sizer)
		sizer.Fit(self)
		#Publisher().subscribe(self.OnTableNameChanged, "table_name_changed")
	def setFocus(self, panel_id):
		selected_page = self.nb.GetPage(panel_id)
		#print (dir(self.nb))
		self.nb.SetFocus()
		selected_page.SetFocus()
		selected_num = self.nb.GetSelection() 
		#pprint(dir(self.nb))
		selected = self.nb.GetPage(selected_num)
		#value=selected.GetText()
		print type(selected)
		self.nb.SetSelection(panel_id)
		
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# main


class TabZilla(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, -1, title)
		global prog
		#self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
		self.splitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
		#self.splitter.SetMinimumPaneSize(50)
		#panel layout
		self.panel_pos=[(0,i) for i in range(3)]
		print self.panel_pos
		
		self.panels={}		
		self.focused_pos=None
		pnl = wx.Panel(self)
		self.pnl = pnl		

		#p1 = DragListCtrlPanel(self.splitter,(0,0))
		#p2 = DragListCtrlPanel(self.splitter,(0,1)) 
		#DragList(self.splitter, -1)
		msplitter = MultiSplitterWindow(self.splitter, style=wx.SP_LIVE_UPDATE)
		self.msplitter = msplitter
		self.designer_pos=(0,1) #form designer pane (midle)
		self.panels ={pos:DragListCtrlPanelManager(msplitter,self,pos,self.panel_pos) for pos in self.panel_pos  if self.designer_pos!=pos}
		#self.panels[self.designer_pos]=DesignPanelManager(self.splitter, self, self.designer_pos,self.panels) #
		self.panels[self.designer_pos]=EmptyPanel(self.msplitter) #TableCopyPanel(self, self.designer_pos)
		if 0:
			for pos in self.panel_pos:
				print pos
				self.panels[pos] = DragListCtrlPanelManager(msplitter,pos,self.panel_pos)		
				#self.panels[pos] = DragListCtrlPanel(splitter,pos,self.panel_pos)		
		if 0:
			for pos in self.panel_pos:
				print pos
				pan=self.panels[pos]
				#pan.SetMinSize(pan.GetBestSize())
				msplitter.AppendWindow(pan,375)
		msplitter.AppendWindow(self.panels[(0,0)],250)				
		msplitter.AppendWindow(self.panels[(0,1)],650)				
		msplitter.AppendWindow(self.panels[(0,2)],200)				
		#sys.exit(1)

		if 0:
		
			self._mgr = wx.aui.AuiManager()
			self._mgr.SetManagedWindow(pnl)
			#self._mgr.AddPane(self.panels[self.panel_pos[0]], wx.CENTER)
			#self._mgr.AddPane(self.panels[self.panel_pos[1]], wx.CENTER)
			self._mgr.SetDockSizeConstraint(0.5, 0.5) 
			if 1:
				self._mgr.AddPane(self.panels[self.panel_pos[0]],
								 wx.aui.AuiPaneInfo().
								 Left().Layer(2).
								 MinSize((300, -1)).BestSize((340, -1)).
								 Floatable(ALLOW_AUI_FLOATING).FloatingSize((240, 700)).
								 Caption("Left").
								 CloseButton(False).
								 Name("FileTree"))		
				self._mgr.AddPane(self.panels[self.panel_pos[1]],
								 wx.aui.AuiPaneInfo().
								 Right().Layer(2).
								 MinSize((100, -1)).BestSize((340, -1)).
								 Floatable(ALLOW_AUI_FLOATING).FloatingSize((240, 700)).
								 Caption("Right").
								 CloseButton(False).
								 Name("FileTree2"))
			if 0:
				desing_pnl = wx.Panel(self)
				self.desing_pnl = desing_pnl	
				TEST_BTN=wx.NewId()
				self.desing_pnl.test = wx.Button(self, TEST_BTN, "Test",size=(200,200))
				#self.desing_pnl.test.SetBackgroundColour('#FFFFFF')
				self.desing_pnl.test.Enable(True)
				self.desing_pnl.sizer2 = wx.BoxSizer(wx.VERTICAL)
				self.desing_pnl.sizer2.Add(self.desing_pnl.test, 1, wx.EXPAND)
				self.desing_pnl.SetSizer(self.desing_pnl.sizer2)
				self.Bind(wx.EVT_BUTTON, self.OnTest, id=TEST_BTN)		
				self.desing_pnl.SetAutoLayout(True)
			self._mgr.AddPane(self.panels[self.panel_pos[2]],
							 wx.aui.AuiPaneInfo().Center().BestSize((200,200)).
							 MinSize((360, -1)).
							 Floatable(True).FloatingSize((240, 700)).
							 Caption("Center").
							 CloseButton(True).
							 Name("Design"))
			#self.auiConfigurations = {}
			#self.auiConfigurations[DEFAULT_PERSPECTIVE] = self.mgr.SavePerspective()
			self._mgr.Update()

			self._mgr.SetFlags(self._mgr.GetFlags() ^ wx.aui.AUI_MGR_TRANSPARENT_DRAG)
		
		#self._mgr.Update()
		#self.splitter.SplitVertically(self.panels[self.panel_pos[0]], self.panels[self.panel_pos[1]])
		self.log=cu.NullLog()
		#self.Bind(wx.EVT_SIZE, self.OnSize)
		#self.Bind(wx.EVT_SPLITTER_DCLICK, self.OnDoubleClick, id=ID_SPLITTER)
		
		filemenu= wx.Menu()
 		menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
		menuSave = filemenu.Append(wx.ID_SAVE, "&Save\tCtrl-S"," Save file")
		menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "&SaveAs\tCtrl-E"," Save As file")
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
		self.Bind(wx.EVT_MENU, self.OnSaveAs, menuSaveAs)		
		#menuSave.Enabled(False)
		#menuSaveAs.Enabled(False)
		#print menuSaveAs
		#dir(menuSaveAs)
		menuSave.Enable(False)
		menuSaveAs.Enable(False)
		filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
		
		editmenu = wx.Menu()
		#netmenu = wx.Menu()
		#showmenu = wx.Menu()
		configmenu = wx.Menu()
		workspacemenu = wx.Menu()
		helpmenu = wx.Menu()

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		#menuBar.Append(editmenu, "&Edit")
		#menuBar.Append(netmenu, "&Net")
		#menuBar.Append(showmenu, "&Show")
		menuBar.Append(configmenu, "&Config")
		menuBar.Append(workspacemenu, "&Workspace")
		menuBar.Append(helpmenu, "&Help")
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
		if 0:
			tb = self.CreateToolBar( wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
			tb.AddSimpleTool(10, wx.Bitmap('images/Class.png'), 'Previous')
			tb.AddSimpleTool(20, wx.Bitmap('images/Class.png'), 'Up one directory')
			tb.AddSimpleTool(30, wx.Bitmap('images/Class.png'), 'Home')
			tb.AddSimpleTool(40, wx.Bitmap('images/Class.png'), 'Refresh')
			tb.AddSeparator()
			tb.AddSimpleTool(50, wx.Bitmap('images/Class.png'), 'Editor')
			tb.AddSimpleTool(60, wx.Bitmap('images/Class.png'), 'Terminal')
			tb.AddSeparator()
			tb.AddSimpleTool(70, wx.Bitmap('images/Class.png'), 'Help')
			tb.Realize()
		if 0:
			self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

			self.buttonF3 = wx.Button(self, ID_BUTTON + 3, "F3 Rename")
			self.buttonF3.SetBackgroundColour('#FFFFFF')
			self.buttonF3.Disable()
			self.buttonF4 = wx.Button(self, ID_BUTTON + 4, "F4 Describe")
			self.buttonF4.SetBackgroundColour('#FFFFFF')
			self.buttonF4.Disable()
			self.buttonF5 = wx.Button(self, ID_BUTTON + 5, "F5 Copy Data")
			self.buttonF5.Disable()
			#rint dir(button3)
			self.buttonF5.SetForegroundColour('#FA5858')
			#SetTextColour(wx.RED)
			self.buttonF5.SetBackgroundColour('#FFFFFF')
			#sys.exit(1)
			#button3.Enable()
			self.buttonF6 = wx.Button(self, ID_BUTTON + 6, "F6 Copy DDL")
			self.buttonF6.SetBackgroundColour('#FFFFFF')
			self.buttonF6.Disable()
			self.buttonF7 = wx.Button(self, ID_BUTTON + 7, "F7 Move")
			self.buttonF7.SetBackgroundColour('#FFFFFF')
			self.buttonF7.Disable()
			self.buttonF8 = wx.Button(self, ID_BUTTON + 8, "F8 Truncate")
			self.buttonF8.SetBackgroundColour('#FFFFFF')
			self.buttonF8.Disable()
			self.buttonF9 = wx.Button(self, ID_BUTTON + 9, "F9 Drop")
			self.buttonF9.SetBackgroundColour('#FFFFFF')
			self.buttonF9.Disable()
			self.buttonF10 = wx.Button(self, ID_EXIT, "F10 Quit")
			#self.buttonF10.SetForegroundColour('#585858')
			#SetTextColour(wx.RED)
			self.buttonF10.SetBackgroundColour('#FFFFFF')		
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF3, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF4, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF5, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF6, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF7, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF8, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF9, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)
			self.sizer2.Add(self.buttonF10, 1, wx.EXPAND)
			self.sizer2.Add((5,5),0,wx.EXPAND)

			self.Bind(wx.EVT_BUTTON, self.OnF3, id=ID_BUTTON+3)
			self.Bind(wx.EVT_BUTTON, self.OnF9, id=ID_BUTTON+9)



		size = wx.DisplaySize()
		self.SetSize(size)
		self.count = {}
		#self.sb = self.CreateStatusBar()
		#self.sb.SetStatusText(os.getcwd())
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		if 0:
			self.statusbar=self.CreateStatusBar(2, wx.ST_SIZEGRIP)
			self.statusbar.SetStatusWidths([-3, -3])
			self.statusbar.SetStatusText(os.getcwd(), 0)
			self.statusbar.SetStatusText("Welcome To %s!" % prog, 1)			
		else:
			if 0:
				self.sb = CustomStatusBar(self)
				self.gauge = wx.Gauge(self.sb, -1, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
				#self.Bind(wx.EVT_TIMER, self.TimerHandler)
				#self.timer = wx.Timer(self)
				#self.timer.Start(100)
				
				rect = self.sb.GetFieldRect(2)
				self.gauge.SetPosition((rect.x+2, rect.y+2))
				self.gauge.SetSize((rect.width-3, rect.height-4))

				#self.gauge.Hide()
				
				self.SetStatusBar(self.sb)
				#self.gauge = gauge
				self.gauge.Show()
				#self.gauge.SetValue(10)
				self.gauge.Pulse()
				
			else:
				if 0:
					self.statusbar = ESB.EnhancedStatusBar(self, -1)
					self.statusbar.SetSize((-1, 23))
					self.statusbar.SetFieldsCount(4)
					self.SetStatusBar(self.statusbar)        
					#self.statusbar.SetStatusWidths([  250, 120, 140])
					if 0:
						bmp = wx.ArtProvider_GetBitmap(wx.ART_ERROR,
													   wx.ART_TOOLBAR, (16,16))
						
						upbmp = wx.StaticBitmap(self.statusbar, -1, bmp)

						bmp = wx.ArtProvider_GetBitmap(wx.ART_HELP,
													   wx.ART_TOOLBAR, (16,16))
						
						downbmp = wx.StaticBitmap(self.statusbar, -1, bmp)
						btnmio = wx.Button(self.statusbar, -1, "Push Me!")
					
					if 0:
						choice = wx.Choice(self.statusbar, -1, size=(100,-1),
										   choices=['Hello', 'World!', 'What', 'A', 'Beautiful', 'Class!'])
						ticker = Ticker(self.statusbar, -1)
						ticker.SetText("Hello World!")
						ticker.SetBackgroundColour(wx.BLUE)
						ticker.SetForegroundColour(wx.NamedColour("YELLOW"))
						ticker.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False))
						statictext = wx.StaticText(self.statusbar, -1, "Welcome To %s!" % prog)
						
						self.ticker = ticker
					gauge={}
					for pos in self.panel_pos:
						gauge[pos] = wx.Gauge(self.statusbar, -1, size=(250, 25), style=wx.GA_HORIZONTAL|wx.GA_SMOOTH) 
					self.gauge = gauge
					self.timer={}
					#self.Bind(wx.EVT_TIMER, self.TimerHandler0)
					#self.gen_bind(wx.EVT_TIMER,self, self.TimerHandler_pos,(self.panel_pos[0]))
					
					
					self.timer_xref={}
					if 1:
						for pos in self.panel_pos:
							i=wx.NewId()
							self.timer_xref[i]=pos
							self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
							self.timer[pos]=wx.Timer(self, id=i)
							#lambda event, i=i: self.Screens(event, the_id=i), id=i
							#self.gen_bind(wx.EVT_TIMER,self, self.TimerHandler,(pos))
					#self.timer={}
					#for pos in self.panel_pos:
					#self.timer = wx.Timer(self)
					#self.gauge.Hide()
					btn_stop={}
					for pos in self.panel_pos:
						btn_stop[pos] = wx.Button(self.statusbar, -1, "Stop", size=(50,100)) 
					self.btn_stop=btn_stop
					for pos in self.panel_pos:
						self.btn_stop[pos].Hide()				
					#statusbarchildren = self.statusbar.GetChildren()
					#for widget in statusbarchildren:
					#	self.statusbar.AddWidget(widget)
					if 0:
						bsizer = wx.BoxSizer(wx.HORIZONTAL)
						bsizer.Add(self.gauge, 0, wx.LEFT)
						bsizer.Add(self.btn_stop, 1, wx.RIGHT|wx.EXPAND)
						self.statusbar.SetSizer(bsizer)

					#self.Bind(wx.EVT_IDLE, self.IdleHandler)
					self.Bind(wx.EVT_CLOSE, self.OnClose)
					#self.Bind(wx.EVT_BUTTON, self.OnStopDbRequest, self.btn_stop)
					for pos in self.panel_pos:
						self.gen_bind(wx.EVT_BUTTON,self, self.OnStopDbRequest,(pos))
					for pos in self.panel_pos:
						self.gauge[pos].Hide()
					self.stt={}
					for p in self.panel_pos:
						self.statusbar.AddWidget(self.gauge[p], horizontalalignment=ESB.ESB_EXACT_FIT,verticalalignment=ESB.ESB_ALIGN_CENTER_VERTICAL,pos=p[1]*2)
						print '*******************', p[1]*2
						self.statusbar.AddWidget(self.btn_stop[p],horizontalalignment=ESB.ESB_ALIGN_LEFT, verticalalignment=ESB.ESB_ALIGN_CENTER_VERTICAL,  pos=p[1]*2+1)
						#statictext =
						self.stt[p[1]] =wx.StaticText(self.statusbar, -1, "Welcome To %s!" % prog)
						self.statusbar.AddWidget(self.stt[p[1]] , horizontalalignment=ESB.ESB_ALIGN_LEFT,verticalalignment=ESB.ESB_ALIGN_CENTER_VERTICAL,pos=p[1]*2)
					#print self.gauge
				
		#Publisher().subscribe(self.onShowProgress, "show_progress")			
		self.Center()
		self.Show(True)
		if 0:
			#Publisher().subscribe(self.onGaugeStop, "stop_db_progress_gauge")
			#Publisher().subscribe(self.onGaugeStart, "start_db_progress_gauge")
			#Publisher().subscribe(self.onUpdateSbLocUrl, "update_status_bar")
			Publisher().subscribe(self.onShowTcDialog, "show_table_copy_dialog")
			Publisher().subscribe(self.__OnDesignPanelManager, "show_copy_pipeline")
			
			Publisher().subscribe(self.onShowPCDialog, "show_partition_copy_dialog")		
			Publisher().subscribe(self.onShowSPCDialog, "show_subpartition_copy_dialog")		
			Publisher().subscribe(self.onShowQueryCopyDialog, "show_query_copy_dialog")		
			Publisher().subscribe(self.onStartTableCopy, "start_table_copy")
			Publisher().subscribe(self.onStartPartitionCopy, "start_partition_copy")
			Publisher().subscribe(self.onStartSubPartitionCopy, "start_subpartition_copy")
			#Publisher().subscribe(self.onStartQueryCopy, "start_query_copy")
			#Publisher().subscribe(self.onTableCopyTrial, "generate_tc_xml")
			Publisher().subscribe(self.onTableCopyDeployXml, "deploy_tc_xml")
			Publisher().subscribe(self.onPartitionCopyDeployXml, "deploy_pc_xml")
			Publisher().subscribe(self.onSubPartitionCopyDeployXml, "deploy_spc_xml")
			Publisher().subscribe(self.onQueryCopyDeployXml, "deploy_qc_xml")
			#file to file copy
			Publisher().subscribe(self.onStartF2FCopy, "start_f2f_copy")
			Publisher().subscribe(self.OnStopF2FCopyProcess, "stop_f2f_copy_process")
			#Publisher().subscribe(self.onF2FCopyDone, "f2f_copy_done")
			
			Publisher().subscribe(self.onCopyStatus, "copy_status")
			Publisher().subscribe(self.onCopyDone, "copy_done")
			Publisher().subscribe(self.OnStopTableCopyProcess, "stop_table_copy_process")
			#Publisher().subscribe(self.onCreatedConfigFile, "created_config_file")
			#Publisher().subscribe(self.onCreatedWorkerFile, "created_worker_file")
			#Publisher().subscribe(self.onSetButtons, "set_buttons")
			Publisher().subscribe(self.onEnableButtons, "enable_buttons")
			#Publisher().subscribe(self.onTestManager, "test_manager_panes")
			Publisher().subscribe(self.__onShowTransferPanel, "show_transfer_log")
			
		sub(self.onShowTcDialog, "show_table_copy_dialog")
		sub(self.__OnDesignPanelManager, "show_copy_pipeline")
		
		sub(self.onShowPCDialog, "show_partition_copy_dialog")
		sub(self.onShowSPCDialog, "show_subpartition_copy_dialog")
		sub(self.onShowQueryCopyDialog, "show_query_copy_dialog")
		sub(self.onStartTableCopy, "start_table_copy")
		sub(self.onStartPartitionCopy, "start_partition_copy")
		sub(self.onStartSubPartitionCopy, "start_subpartition_copy")
		
		sub(self.onTableCopyDeployXml, "deploy_tc_xml")
		sub(self.onPartitionCopyDeployXml, "deploy_pc_xml")
		sub(self.onSubPartitionCopyDeployXml, "deploy_spc_xml")
		sub(self.onQueryCopyDeployXml, "deploy_qc_xml")
		
		sub(self.onStartF2FCopy, "start_f2f_copy")
		sub(self.OnStopF2FCopyProcess, "stop_f2f_copy_process")
		
		sub(self.onCopyStatus, "copy_status")
		sub(self.onCopyDone, "copy_done")
		sub(self.OnStopTableCopyProcess, "stop_table_copy_process")
		
		sub(self.onEnableButtons, "enable_buttons")
		
		sub(self.__onShowTransferPanel, "show_transfer_log")
		sub(self.__onShowDeploymentPanel, "show_deployment_log")
		
		
		
		
		#open_design_form
		#refresh list after copy is done
		#Publisher().subscribe(self.onCopyStatus, "refresh_list")
		self.drag_pos=None
		self.drop_pos=None
		self.dd_data =None
		self.delete_conn = None
		#self.Bind(wx.EVT_KEY_DOWN, self.onTextKeyEvent)	
		#self.SetSize(wnd_size)
		self.t2t_id=1
		#wnd_size=(1300,1050)
		self.transfer=TransferPannel(self.splitter,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		#self.splitter.SplitHorizontally(self.msplitter,transfer)
		#self.splitter.SetMinimumPaneSize(50)
		self.splitter.SetOrientation(wx.VERTICAL)
		self.wnd_size= self.GetSizeTuple()
		self.splitter.AppendWindow(self.msplitter)				
		self.splitter.AppendWindow(self.transfer)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.splitter,1,wx.EXPAND)
		#self.sizer.Add((5,5),0,wx.EXPAND)
		#self.sizer.Add(self.sizer2,0,wx.EXPAND,5)
		#self.sizer.Add((5,5),0,wx.EXPAND)
		self.SetSizer(self.sizer)
		
		
		self.msplitter.SetSashPosition(0, self.wnd_size[0]/2)
		self.msplitter.SetSashPosition(1, 0)
		self.msplitter.SizeWindows()
		#print (dir(self.msplitter))
		self.splitter.SetSashPosition(0,self.wnd_size[1]-56)
		self.splitter.SizeWindows()
		#print self.GetSize()
		self.ssize= self.splitter.GetSizeTuple()
		self.msize=self.msplitter.GetSizeTuple()
	def OnOpen(self,e):
		""" Open a file"""
		self.dirname = ''
		dlg = wx.FileDialog(self, "Open pipleine file", self.dirname, "", "*.ppl", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			print self.filename, self.dirname
			#f = open(os.path.join(self.dirname, self.filename), 'r')
			if 0:
				self.panel.AddNew(self.filename,f.read(), True)	
				selected_num = self.panel.nb.GetSelection()            
				selected = self.panel.nb.GetPage(selected_num)
				print  'after AddNew' , selected.qp.editor.ignore_change
				selected.qp.editor.ignore_change=True
				print selected_num
				#self.panel.nb.SetPageText(selected_num,self.filename)	
				#print dir(tab.qp.page)			
				#tab.qp.page.SetValue()
			

			#f.close()
		dlg.Destroy()
		if 0:
			selected_num = self.panel.nb.GetSelection()            
			selected = self.panel.nb.GetPage(selected_num)
			#selected.UnChange()
			#selected.NoticeChange()
			selected.UnChange()
			print  'end 2' , selected.qp.editor.ignore_change
			print  'selected.Id ' , selected.Id
			#tab.SetFocus()
			#selected_page = self.help_notebook.GetPage(selected_page_number)	
			#self.panel.nb.SetPageText(selected_num,'test')	
	def OnSave(self,e):
		pass
	def OnSaveAs(self,e):
		pass
		
		
	def onShowTransferPanel_del(self, evt):
		print 'onShowTransferPanel'
		(cnt) = evt.data
		print cnt	
		self.splitter.SetSashPosition(0, self.wnd_size[1]-156)
		#self.splitter.SetSashPosition(1, 600)
		self.splitter.SizeWindows()
		
		Publisher().sendMessage( 'adjust_design_logger',(self.msplitter.GetSizeTuple())) 
	def __onShowDeploymentPanel(self, data, extra1, extra2=None):
		print 'onShowTransferPanel'
		(cnt) = data
		print cnt	
		self.splitter.SetSashPosition(0, self.wnd_size[1]-206)
		#self.splitter.SetSashPosition(1, 600)
		self.splitter.SizeWindows()
		#Publisher().sendMessage( 'adjust_design_logger',(self.msplitter.GetSizeTuple())) 
		self.transfer.setFocus(1)		
		send('adjust_design_logger',(self.msplitter.GetSizeTuple()))
		
	def __onShowTransferPanel(self, data, extra1, extra2=None):
		print 'onShowTransferPanel'
		(cnt) = data
		print cnt	
		self.splitter.SetSashPosition(0, self.wnd_size[1]-206)
		#self.splitter.SetSashPosition(1, 600)
		self.splitter.SizeWindows()
		self.transfer.setFocus(0)
		#Publisher().sendMessage( 'adjust_design_logger',(self.msplitter.GetSizeTuple())) 			
		send('adjust_design_logger',(self.msplitter.GetSizeTuple()))		
	def onTestManager_0(self, evt):
		print 'onTestManager'
		(width) = evt.data
		print width	
		self.splitter.SetSashPosition(0, 300)
		self.splitter.SetSashPosition(1, 600)
		self.splitter.SizeWindows()
		
		
	def OnTest(self, event):		
		print 'OnTest'
	def onTextKeyEvent(self, event):
		keycode = event.GetKeyCode()
		print keycode
		if 0:
			controlDown = event.CmdDown()
			#print 'grid ctrl: ',controlDown
			if controlDown and keycode == 65:
				print "Ctrl-A grid"
				#self.page.SetSelection(-1, -1)
				self.SelectAll()
			#if keycode==344: #F5 
			#	self.ExecSQL()
			
			if controlDown and keycode == 67:
				print "grid Ctrl-C"		
				if self.GetSelectedCells():
					print "Selected cells " + str(self.GetSelectedCells())
				 # If selection is block...
				if self.GetSelectionBlockTopLeft():
					print "Selection block top left " + str(self.GetSelectionBlockTopLeft())
				if self.GetSelectionBlockBottomRight():
					print "Selection block bottom right " + str(self.GetSelectionBlockBottomRight())
				
				# If selection is col...
				if self.GetSelectedCols():
					print "Selected cols " + str(self.GetSelectedCols())
				
				# If selection is row...
				if self.GetSelectedRows():
					print "Selected rows " + str(self.GetSelectedRows())
				self.copy()
			print keycode
			if keycode==344: #F5 			
				assert self.surrent_sql, 'Re-exec sql is not set'
				assert self.connect_as, 'Re-exec db is not set'
				Publisher().sendMessage( "re_exec_sql", (self.surrent_sql,self.connect_as) )

			event.Skip()			
	def OnF3(self, event):	
		print 'F3 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = OracleConnectDialog(self, -1, "Add Oracle connect.", size=(450, 450),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None

		dlg.Destroy()
	def OnF9(self, event):	
		print 'F9 is clicked'
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
		list=self.getListFromPos(self.focused_pos)
		self.delete_conn = []
		idx = -1
		while True: # find all the selected items and put them in a list
			idx = list.GetNextItem(idx, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			if idx == -1:
				break
			self.delete_conn.append(list.getItemInfo(idx))
		print self.delete_conn		
		dlg = DeleteConnectDialog(self, -1, "Delete connect.", size=(250, 250),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None

		dlg.Destroy()
	def onSetButtons(self, evt):
		#print 'onSetButtons'
		(self.focused_pos, btns) = evt.data
		#self.setButtons(btns)
	def onEnableButtons(self, evt):
		#print 'onEnableButtons'
		(self.focused_pos,btns) = evt.data
		#self.enableButtons(btns)		
	def setButtons(self, data):	
		global dBtn
		for key, name in data.items():
			btn='button%s' % key
			#print btn
			exec("self.%s.SetLabel('%s %s')" % (btn,key,name), globals(), locals())
			if 1 or name==dBtn:
				exec("self.%s.Disable()" % (btn), globals(), locals())
			else:
				exec("self.%s.Enable()" % (btn), globals(), locals())
	def enableButtons_(self, data):	
		global dBtn
		for key, name in data.items():
			btn='button%s' % key
			#print btn
			#exec("self.%s.SetLabel('%s %s')" % (btn,key,name), globals(), locals())
			if name==dBtn:
				exec("self.%s.Disable()" % (btn), globals(), locals())
			else:
				exec("self.%s.Enable()" % (btn), globals(), locals())				
	#def focusFollowsMouse(self):
	#	self.Bind(wx.EVT_ENTER_WINDOW, lambda event: print 'test';self.SetFocus())			
	def getListFromPos(self,pos):
		return self.panels[pos].list
	def getCurrentList(self,pos):
		return self.getListFromPos(pos).current_list
		
	def OnStopTableCopyProcess(self, event):
		if self.worker:			
			#terminate_thread(self.worker)
			#
			#self.worker.join()
			print self.worker.isAlive()
			if self.worker.isAlive():
				
				print 'it''s alive, aborting...'
				#self.worker.abort()
				#self.worker.terminate()
				terminate_thread(self.worker)

				
		self.dlg.panel.timer.Stop()
		self.dlg.panel.logger.AppendText('Table copy process terminated.\n')
		#self.btn_backgr.Disable()
		#self.btn_stop.Disable()
		self.dlg.panel.btn_close.Enable(True)
	def OnStopF2FCopyProcess(self, event):
		if self.worker:			
			#terminate_thread(self.worker)
			#
			#self.worker.join()
			print self.worker.isAlive()
			if self.worker.isAlive():
				
				print 'it''s alive, aborting...'
				#self.worker.abort()
				#self.worker.terminate()
				terminate_thread(self.worker)

				
		self.dlg.panel.timer.Stop()
		self.dlg.panel.logger.AppendText('File to File copy process terminated.\n')
		#self.btn_backgr.Disable()
		#self.btn_stop.Disable()
		self.dlg.panel.btn_close.Enable(True)
		
	def getVarsToPath(self, pos):
		print 'pos.getVarsToPath: ',pos
		return self.panels[pos].getVarsToPath()
	def setDragDrop(self, dd_info):
		(self.drag_pos,self.drop_pos,self.dd_data) = dd_info
		print 'self.drop_pos=============', self.drop_pos
	def onCopyDone(self, evt):
		print 'onCopyDone'
		(out,err,pos_to) = evt.data
		status='successfully'
		if 0: 
			if err:
				print '#'*40
				print err
				print '#'*40
				status='with errors'
				#self.dlg.panel.logger.AppendText('#'*40+'\n' + '\n'.join(err)+'\n' +'#'*40+'\n')
				self.dlg.Status(err)
			#print out
			#self.status=out
			self.keepGoing = False
			self.dlg.panel.btn_close.Enable(True)
			self.dlg.panel.btn_stop.Enable(False)
			self.dlg.panel.gauge.SetValue(100)
			self.dlg.panel.timer.Stop()
			if out or out==0:
				#self.dlg.Status('Table Copy completed %s.' % status)
				#else:
				self.dlg.Status(out)
				self.dlg.Status('Copy completed %s.' % status)
				#refresh target list
				#self.getListFromPos(pos_to).refreshList()
			#self.dlg.logger.AppendText('Table Copy completed %s.' % status)
		
	def onCreatedConfigFile0(self, evt):
		print 'onCreatedConfigFile'
		(file_loc) = evt.data
		print file_loc
		if os.path.isfile(file_loc):
			f = open(file_loc, 'r')			
			self.dlg.panel.config.SetValue(f.read())
			f.close()
	def onCreatedWorkerFile0(self, evt):
		print 'onCreatedWorkerFile'
		(file_loc) = evt.data		
		print file_loc
		if os.path.isfile(file_loc):
			f = open(file_loc, 'r')			
			self.dlg.panel.worker.SetValue(f.read())
			f.close()
	def onCopyStatus(self, evt):
		print 'onTableCopyStatus'
		(out,err) = evt.data
		if err:
			print '#'*40
			print err
			print '#'*40
		print out
		#self.dlg.Status(out)
		#Publisher().sendMessage( "tc_deployment_completed", () )
		
	def onStartTableCopy(self, evt):
		print 'start_table_copy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
			
		assert len(self.table_to)>0 , 'No tables to copy.'
		print self.table_to
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started table copy.'
		useMetal = False
		if 0:
			self.dlg = TableCopyProgressDialog(self, -1, "Table Copy", size=(750, 750) ,
							 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
							 style =wx.CAPTION|wx.SYSTEM_MENU | wx.THICK_FRAME|wx.MAXIMIZE_BOX  #, # & ~wx.CLOSE_BOX,
							 #useMetal=useMetal,
							 )
			#self.dlg.CenterOnScreen()
			# this does not return until the dialog is closed.

		if 1:
			self.worker = ExecThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=False)
			self.worker.start()
			print self.worker.isAlive()
		#val = self.dlg.Show()
		#self.dlg.Destroy()
		#print 'T2T Dialog exited with: ',val			

			
	
	def onStartF2FCopy(self, evt):
		print '-onStartF2FCopy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
			
		assert len(self.table_to)>0 , 'No tables to copy.'
		print self.table_to
		self.worker={}
		if 1:
			#xml_config='test_config.xml'
			#xml_worker='tc_copy_test.xml'
			#cfrom= self.getVarsToPath(self.drag_pos)
			
			
			#cto =self.getVarsToPath(self.drop_pos)
			#print cfrom
			#print cto
			self.keepGoing = True
			self.status='Started file copy.'
			useMetal = False
			if 1:
				self.dlg = F2FCopyProgressDialog(self, -1, "File to File Copy", size=(750, 500) ,
								 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
								 style =wx.CAPTION|wx.SYSTEM_MENU | wx.THICK_FRAME , # & ~wx.CLOSE_BOX,
								 drop_pos=self.drop_pos
								 #useMetal=useMetal,
								 )
				#self.dlg.CenterOnScreen()
				# this does not return until the dialog is closed.

				if 1:
					from_list=self.getListFromPos(self.drag_pos)
					to_list=self.getListFromPos(self.drop_pos)
					#file_from='/'.join((from_list.getFileLocation(),from_list.GetSelected()))
					file_from=from_list.getFileLocation()
					file_to=to_list.getFileLocation()
					conn_from = from_list.getConnectInfo()
					conn_to = to_list.getConnectInfo()
					for fn, fset in self.table_to.items():
						self.worker[fn] = ExecF2FThread((file_from,file_to,conn_from,conn_to,self.drop_pos,fset), is_trial=False)
						self.worker[fn].start()
						print self.worker[fn].isAlive()
				val = self.dlg.Show()
				#self.dlg.Destroy()
				print 'F2F Dialog exited with: ',val
				#to_list.refreshList()	
					
				
	def onTableCopyDeployXml(self, evt):
		print 'start_table_copy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
		#self.pos_from, self.pos_from, self.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
			
		assert len(self.table_to)>0 , 'No tables to copy.'
		print self.table_to
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started table copy.'
		useMetal = False
		if 1:
			self.worker = ExecThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=True)
			
			self.worker.start()
			print self.worker.isAlive()
	def onStartPartitionCopy(self, evt):
		print 'start_partition_copy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
			
		assert len(self.table_to)>0 , 'No partitions to copy.'
		print self.table_to
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started partition copy.'
		useMetal = False
		if 1:
			self.worker = ExecPcThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=False)
			
			self.worker.start()
			print self.worker.isAlive()
	def onStartSubPartitionCopy(self, evt):
		print 'start_subpartition_copy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
			
		assert len(self.table_to)>0 , 'No sub-partitions to copy.'
		print self.table_to
		
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started sub-partition copy.'
		useMetal = False
		if 1:
			self.worker = ExecSPcThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=False)
			
			self.worker.start()
			print self.worker.isAlive()	
	def getXmlFileNames(self):
		ts= datetime.datetime.now().strftime("%y%m%d_%H%M%S")
		return ('pipeline_config_%s.xml' % ts, 'tc_query_copy_%s.xml' % ts)
		#((local_path,remote_path, config_file),(out_dir,remote_loc, worker_file))
	def del_onStartQueryCopy(self, evt):
		print 'start_subpartition_copy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
			
		assert len(self.table_to)>0 , 'No sub-partitions to copy.'
		print self.table_to
		ts= datetime.datetime.now().strftime("%y%m%d_%H%M%S")
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		print xml_config, xml_worker
		#sys.exit(1)
		self.keepGoing = True
		self.status='Started sub-partition copy.'
		useMetal = False
		if 1:
			self.worker = ExecQcThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=False)
			
			self.worker.start()
			print self.worker.isAlive()		
			
	def onPartitionCopyDeployXml(self, evt):
		print 'start_table_copy'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
		#self.pos_from, self.pos_from, self.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
			
		assert len(self.table_to)>0 , 'No tables to copy.'
		print self.table_to
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started table copy.'
		useMetal = False
		if 1:
			self.worker = ExecPcThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=True)
			
			self.worker.start()
			print self.worker.isAlive()

	def onSubPartitionCopyDeployXml(self, evt):
		print 'onSubPartitionCopyDeployXml'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
		#self.pos_from, self.pos_from, self.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
			
		assert len(self.table_to)>0 , 'No tables to copy.'
		print self.table_to
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started sub-partiton deployment.'
		useMetal = False
		if 1:
			self.worker = ExecSPcThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=True)
			
			self.worker.start()
			print self.worker.isAlive()			
	
	def onQueryCopyDeployXml(self, evt):
		print 'onSubPartitionCopyDeployXml'
		(self.drag_pos,self.drop_pos,self.dd_data,self.table_to, _tcmode) =  evt.data
		#self.pos_from, self.pos_from, self.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
			
		assert len(self.table_to)>0 , 'No tables to copy.'
		print self.table_to
		(xml_config, xml_worker)= self.getXmlFileNames()
		cfrom= self.getVarsToPath(self.drag_pos)
		cto =self.getVarsToPath(self.drop_pos)
		print cfrom
		print cto
		self.keepGoing = True
		self.status='Started sub-partiton deployment.'
		useMetal = False
		if 1:
			self.worker = ExecQcThread((cfrom,cto,self.drag_pos,self.drop_pos,xml_config),(xml_worker, self.table_to, _tcmode), is_trial=True)
			
			self.worker.start()
			print self.worker.isAlive()			
	
			
			
	def ifConnectDups(self,config_file, conn_env,connect,pos):
		specfile_from =os.path.join(configDirLoc, config_file)
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			print doc
			conn=doc.getElementsByTagName("connector")[0]
			assert conn, 'Cannot find connector tag.'
			print conn_env
			env_type=conn_env.split('.')[0]
			env=conn.getElementsByTagName(env_type)[0]
			db_name=conn_env.split('.')[1]
			db_name=env.getElementsByTagName(db_name)[0]
			print db_name
			(username, password, sid, host, port) = connect.values()
			# check if connect already exists
			connects=[n.nodeName for n in db_name.childNodes if n.nodeType!=env.CDATA_SECTION_NODE and n.nodeType != env.TEXT_NODE and n.nodeType != env.COMMENT_NODE]
			print connects
			
			newcon='%s_%s' % (username,sid)
			print newcon in connects
			#sys.exit(1)
			if newcon in connects:
				
				dlg = wx.MessageDialog(self, 'Connect profile %s already exists in %s!' % (newcon, conn_env),
						   'Error',
						   wx.OK | wx.ICON_INFORMATION
						   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
						   )
				dlg.ShowModal()
				dlg.Destroy()
				return True
		return False
	def ifConnectValsSet(self,connect,pos):
		(username, password, sid, host, port) = connect.values()
		for key,conn in connect.items():
			print conn
			if not conn:
				dlg = wx.MessageDialog(self, '%s is not set!' % key,
						   'Error.',
						   wx.OK | wx.ICON_INFORMATION
						   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
						   )
				dlg.ShowModal()
				dlg.Destroy()
				blog.err('%s is not set!' % conn[0],pos)
				return False
		blog.log('All connect values are set.',pos)
		#sys.exit(1)
		return True			
	def addOracleConnect(self,config_file, conn_env,connect,pos):
		specfile_from =os.path.join(configDirLoc, config_file)
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			print doc
			conn=doc.getElementsByTagName("connector")[0]
			assert conn, 'Cannot find connector tag.'
			print conn_env
			env_type=conn_env.split('.')[0]
			env=conn.getElementsByTagName(env_type)[0]
			db_name=conn_env.split('.')[1]
			db_name=env.getElementsByTagName(db_name)[0]
			print db_name
			(username, password, sid, host, port) = connect.values()
			#print connect
			#sys.exit(1)
			# check if connect already exists
			if 0:
				connects=[n.nodeName for n in db_name.childNodes if n.nodeType!=env.CDATA_SECTION_NODE and n.nodeType != env.TEXT_NODE and n.nodeType != env.COMMENT_NODE]
				print connects
				newcon='%s@%s' % (username,sid)
				if newcon in connects:
					dlg = wx.MessageDialog(self, 'Connect profile %s already exists!' % newcon,
							   'Error',
							   wx.OK | wx.ICON_INFORMATION
							   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
							   )
					dlg.ShowModal()
					dlg.Destroy()
				
				sys.exit(1)
			con_str='<%s_%s type1="inline" schema="%s" pword="%s" sid="%s" HOST = "%s"  PORT = "%s"/>' % (username,sid,username,password,sid, host,port)
			print con_str
			conn_doc=xml.dom.minidom.parseString(con_str)
			conn_stab=conn_doc.getElementsByTagName("%s_%s" % (username,sid))[0]
			print conn_stab
			db_name.appendChild(conn_stab)
			xx = doc.toxml()
			doc=None
			if 1:
				print specfile_from
				fw = open(specfile_from,'w')
				print fw
				fw.write(xx)
				fw.close()
				Publisher().sendMessage( "refresh_list", (pos) )
				blog.log('Added connect %s@%s.' % (username,sid),pos)
				
			#connector=alias.getElementsByTagName(conn_name)[0]
			
			#conn = doc_to.createElement('connector')
			#conn
			#<oracle client_type="ORACLE" descr="UAT database">	
	def deleteConnect(self,config_file, conn_env,connect,pos):
		specfile_from =os.path.join(configDirLoc, config_file)
		print specfile_from
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			print doc
			conn=doc.getElementsByTagName("connector")[0]
			assert conn, 'Cannot find connector tag.'
			print conn_env
			env_type=conn_env.split('.')[0]
			env=conn.getElementsByTagName(env_type)[0]
			db_name=conn_env.split('.')[1]
			db_name=env.getElementsByTagName(db_name)[0]
			print db_name
			(aliasTxt,userTxt,serverTxt) = connect
			print aliasTxt,userTxt,serverTxt
			conn_item=env.getElementsByTagName(aliasTxt)[0]
			#print(dir(db_name))
			db_name.removeChild(conn_item)

			xx = doc.toxml()
			#print xx
			doc=None
			if 1:
				print specfile_from
				fw = open(specfile_from,'w')
				print fw
				fw.write(xx)
				fw.close()
				print self.focused_pos
				blog.log('Connect profile %s@%s is deleted.' % (userTxt,serverTxt),pos)
				Publisher().sendMessage( "refresh_list", (self.focused_pos) )
			#connector=alias.getElementsByTagName(conn_name)[0]
			
			#conn = doc_to.createElement('connector')
			#conn
			#<oracle client_type="ORACLE" descr="UAT database">	
	def clearConnectPassword(self,config_file, conn_env,connect,pos):
		specfile_from =os.path.join(configDirLoc, config_file)
		print specfile_from
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			print doc
			conn=doc.getElementsByTagName("connector")[0]
			assert conn, 'Cannot find connector tag.'
			print conn_env
			env_type=conn_env.split('.')[0]
			env=conn.getElementsByTagName(env_type)[0]
			db_name=conn_env.split('.')[1]
			db_name=env.getElementsByTagName(db_name)[0]
			print db_name
			(aliasTxt,userTxt,serverTxt) = connect
			print aliasTxt,userTxt,serverTxt
			conn_item=env.getElementsByTagName(aliasTxt)[0]
			pprint(conn_item)
			#print(dir(conn_item))
			conn_item.setAttribute("pword","")
			#sys.exit(1)
			#db_name.removeChild(conn_item)

			xx = doc.toxml()
			#print xx
			doc=None
			if 1:
				print specfile_from
				fw = open(specfile_from,'w')
				print fw
				fw.write(xx)
				fw.close()
				blog.log('Password cleared for %s@%s.' % (userTxt,serverTxt),pos)
				#Publisher().sendMessage( "refresh_list", (self.focused_pos) )
				#Publisher().sendMessage( "refresh_list", (self.focused_pos) )
			#connector=alias.getElementsByTagName(conn_name)[0]
			
			#conn = doc_to.createElement('connector')
			#conn
			#<oracle client_type="ORACLE" descr="UAT database">		
	def setOracleConnect(self,config_file, conn_env,connect,pos):
		specfile_from =os.path.join(configDirLoc, config_file)
		print specfile_from
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			print doc
			conn=doc.getElementsByTagName("connector")[0]
			assert conn, 'Cannot find connector tag.'
			print conn_env
			env_type=conn_env.split('.')[0]
			env=conn.getElementsByTagName(env_type)[0]
			db_name=conn_env.split('.')[1]
			db_name=env.getElementsByTagName(db_name)[0]
			print db_name
			print connect
			#(alias,username, password, sid, host, port) = connect.values()
			#print alias,username, password, sid, host, port
			conn_item=env.getElementsByTagName(connect['alias'])[0]
			pprint(conn_item)
			#print(dir(conn_item))
			#print connect
			#sys.exit(1)
			#conn_item.setAttribute("pword","")
			#sys.exit(1)
			db_name.removeChild(conn_item)
			
			xx = doc.toxml()
			#print xx
			doc=None
			if 1:
				print specfile_from
				fw = open(specfile_from,'w')
				print fw
				fw.write(xx)
				fw.close()
				#Publisher().sendMessage( "refresh_list", (self.focused_pos) )
			#connector=alias.getElementsByTagName(conn_name)[0]
			
			#conn = doc_to.createElement('connector')
			#conn
			#<oracle client_type="ORACLE" descr="UAT database">	
			self.addOracleConnect2(config_file, conn_env,connect,pos)
	def addOracleConnect2(self,config_file, conn_env,connect,pos):
		specfile_from =os.path.join(configDirLoc, config_file)
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			print doc
			conn=doc.getElementsByTagName("connector")[0]
			assert conn, 'Cannot find connector tag.'
			print conn_env
			env_type=conn_env.split('.')[0]
			env=conn.getElementsByTagName(env_type)[0]
			db_name=conn_env.split('.')[1]
			db_name=env.getElementsByTagName(db_name)[0]
			print db_name
			#(username, password, sid, host, port) = connect.values()
			con_str='<%s type1="inline" schema="%s" pword="%s" sid="%s" HOST = "%s"  PORT = "%s"/>' % (connect['alias'], connect['username'],connect['password'],connect['sid'], connect['host'],connect['port'])
			print con_str
			conn_doc=xml.dom.minidom.parseString(con_str)
			conn_stab=conn_doc.getElementsByTagName("%s_%s" % ( connect['username'], connect['sid']))[0]
			print conn_stab
			db_name.appendChild(conn_stab)
			xx = doc.toxml()
			doc=None
			if 1:
				print specfile_from
				fw = open(specfile_from,'w')
				print fw
				fw.write(xx)
				fw.close()
				Publisher().sendMessage( "refresh_list", (self.focused_pos) )
			#connector=alias.getElementsByTagName(conn_name)[0]
			
			#conn = doc_to.createElement('connector')
			#conn
			#<oracle client_type="ORACLE" descr="UAT database">				
	def createPipelineConfig(self,cfrom,cto,config_file):
		#create config file
		path_from=cfrom.split('/')
		spec_file_name_from=path_from[1]
		out={}
		

		specfile_from =os.path.join(configDirLoc, spec_file_name_from)
		
		if os.path.isfile(specfile_from):
			doc = xml.dom.minidom.parse(specfile_from)
			


			
			doc_to = Document()
			
			base = doc_to.createElement('test_spec')
			doc_to.appendChild(base)
			
			ps=doc.getElementsByTagName("process_spec")
			base.appendChild(ps[0])
			
			conn = doc_to.createElement('connector')
			
			base.appendChild(conn)
			
			
			from_conn=self.getXMLConnector(doc,path_from[2],path_from[3])
			
			conn.appendChild(from_conn)
			if cfrom<>cto:
				path_to=cto.split('/')
				spec_file_name_to=path_to[1]
				specfile_to ='%s.xml' % os.path.join(configDirLoc, spec_file_name_to)
				if os.path.isfile(specfile_to):
					doc = xml.dom.minidom.parse(specfile_to)
					to_conn=self.getXMLConnector(doc,path_to[2],path_to[3])		
					conn.appendChild(to_conn)
				#sys.exit(1)
					
			ps=doc.getElementsByTagName("default")
			base.appendChild(ps[0])
			
			ps=doc.getElementsByTagName("worker")
			base.appendChild(ps[0])			
			#print doc_to.toxml()			
			out_dir=os.path.join(activeProjLoc,'out')
			#config_file='temp_spec.xml'
			out_file=os.path.join(out_dir,config_file)
			f = open(out_file,'w')
			f.write(doc_to.toprettyxml())
			f.close()
			#remote_loc='/home/zkqfas6/tab_copy/pipeline/posix'
			#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,config_file,remote_loc))
			(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]
			remote_loc='%s/%s' % (tc_path, config_path) 
			#print 'echo %s|pscp %s\\%s bk94994@swmapetldev01.nam.nsroot.net:%s' % (lpwd,out_dir,worker_file,remote_loc)
			#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,worker_file,remote_loc))
			rcopyFile(out_file,'%s/%s' % (remote_loc,config_file))
			#sys.exit(1)
		return (out_dir,remote_loc, config_file)
	def getXMLConnector(self, doc, conn_env, conn_name):
		conn=doc.getElementsByTagName("connector")[0]
		assert conn, 'Cannot find connector tag.'
		print conn_env
		env_type=conn_env.split('.')[0]
		env=conn.getElementsByTagName(env_type)[0]
		alias_name=conn_env.split('.')[1]
		alias=env.getElementsByTagName(alias_name)[0]
		
		connector=alias.getElementsByTagName(conn_name)[0]	
		return connector
	def createPipelineWorker(self,cfrom,cto,config, worker_file,tables):
		#create config file
		max_shards=20
		print appLoc
		db_from =cfrom.split('/')[3]
		db_to =cto.split('/')[3]
		schema_from =cfrom.split('/')[len(cfrom.split('/'))-1]
		schema_to =cto.split('/')[len(cto.split('/'))-1]
		
		tmpl_loc=os.path.join(appLoc,'xml_templates')
		template_name='table_copy.xml'
		tmpl_file_loc= os.path.join(tmpl_loc,template_name)
		
		doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))
			
		doc_to = Document()
		base = doc_to.createElement('etldataflow')
		base.setAttribute("name","test")
		base.setAttribute("pipeline_config",config)
		
		#pprint(dir(base))
		doc_to.appendChild(base)
		gl=doc.getElementsByTagName("globals")[0]
		print gl
		fromdb= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
		fromdb.setAttribute('value','%'+db_from+'%')
		todb= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
		todb.setAttribute('value','%'+db_to+'%')	
		toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
		toschema.setAttribute('value',schema_to)
		
		base.appendChild(gl)
		worker_stab=doc.getElementsByTagName("worker")[0].toxml().replace('\n', '').replace('\r', '')
		print 'ws---',worker_stab.replace('\n', '')
		sys.exit(1)
		#pprint(dir(doc))

		

		not_sharded='OFF'
		for key, item in tables.items():
			(tab,tab_to, shards) = item
			print item
			worker=xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
			#pprint(dir(worker))
			worker.setAttribute('name', tab)
			#param=worker.getElementsByTagName("param")[0]
			for n in worker.getElementsByTagName("param") :
				print n.getAttribute('name')
			param= [n for n in worker.getElementsByTagName("param") if n.getAttribute('name')=='PARTITION'][0]
			##
			##non-partitioned table copy
			##
			param.setAttribute('name','IGNORE_%s' % param.getAttribute('name'))
			tasklet=worker.getElementsByTagName("sqlp")[0]
			if tab<>tab_to:
				
				param = doc_to.createElement('param')
				param.setAttribute('name','TO_TABLE')
				param.setAttribute('value',tab_to)
				tasklet.appendChild(param)
			#modify CDATA
			if shards ==not_sharded:
				pass
			else:
				assert int(shards)>2, 'Num of shards should be between 2 and %d per table.'  % max_shards
				param = doc_to.createElement('param')
				param.setAttribute('name','NUM_OF_SHARDS')
				param.setAttribute('value',shards)
				tasklet.appendChild(param)
				
			cd= [n for n in worker.getElementsByTagName("sql_template")[0].childNodes if n.nodeType==worker.CDATA_SECTION_NODE][0]
			#for n in cd.childNodes:
			#	print n
			#pprint(dir(cd))
			
			#schema= cd.wholeText.split('.')[0]
			cd.data='%s...%s' % (schema_from, tab)
			#param=worker.getElementsByTagName("param")[0]
			base.appendChild(worker)
		#print doc_to.toprettyxml()
		
		out_dir=os.path.join(activeProjLoc,'out')
		#worker_file='tc_temp_worker.xml'
		out_file=os.path.join(out_dir,worker_file)
		f = open(out_file,'w')
		f.write(doc_to.toprettyxml())
		f.close()
		remote_loc='/home/zkqfas6/tab_copy/clients/table_copy/tab_copy'
		os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,worker_file,remote_loc))

		#create worker file
		return (out_dir,worker_file,remote_loc)
	def execTaCo(self, specs, worker):
		print specs
		print worker
		plink_loc=r'C:\Program Files\PuTTY'
		command = r"%s\plink.exe -ssh zkqfas6@lrche25546 -pw %s cd tab_copy;time python tc.py --pipeline_spec=%s --pipeline=%s" % (plink_loc,lpwd, specs,worker)
		print command
		#os.system(command)
	def __OnDesignPanelManager(self, data, extra1, extra2=None):
		#(pos_from, pos_to, items_from ) =  args
		(pos_from, items_from, conn_type_from, item_key) =  data
		useMetal = False
		print 'OnDesignPanelManager'
		pos_to=self.drop_pos
		print pos_from
		print pos_to
		print items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			#title='TableCopy_%d.ppl' % self.t2t_id
			self.t2t_id +=1
			print type(self.panels[self.designer_pos])
			
			if type(self.panels[self.designer_pos])==EmptyPanel:	
				#sys.exit(0)
				design=DesignPanelManager(self.msplitter, self, self.designer_pos,pos_from, pos_to, items_from,item_key)
				self.msplitter.ReplaceWindow(self.panels[self.designer_pos],design)
				self.panels[self.designer_pos]=design
			else:
				self.panels[self.designer_pos].appendPanel(pos_from, pos_to, items_from,item_key)
			#TableCopyPanel(self.splitter,self, self.designer_pos,pos_from, pos_to, items_from)	
			self.panel_size=self.wnd_size[0]/3
			self.msplitter.SetSashPosition(0, self.panel_size)
			self.msplitter.SetSashPosition(1, self.panel_size)
			self.msplitter.SizeWindows()	
		else:
			err('Wrong connect type %s' % conn_type_from)
	def OnDesignPanelManager_rem(self, evt):
		#(pos_from, pos_to, items_from ) =  args
		(pos_from, items_from, conn_type_from, item_key) =  evt.data
		useMetal = False
		print 'OnDesignPanelManager'
		pos_to=self.drop_pos
		print pos_from
		print pos_to
		print items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			#title='TableCopy_%d.ppl' % self.t2t_id
			self.t2t_id +=1
			print type(self.panels[self.designer_pos])
			
			if type(self.panels[self.designer_pos])==EmptyPanel:	
				#sys.exit(0)
				design=DesignPanelManager(self.msplitter, self, self.designer_pos,pos_from, pos_to, items_from,item_key)
				self.msplitter.ReplaceWindow(self.panels[self.designer_pos],design)
				self.panels[self.designer_pos]=design
			else:
				self.panels[self.designer_pos].appendPanel(pos_from, pos_to, items_from,item_key)
			#TableCopyPanel(self.splitter,self, self.designer_pos,pos_from, pos_to, items_from)	
			self.panel_size=self.wnd_size[0]/3
			self.msplitter.SetSashPosition(0, self.panel_size)
			self.msplitter.SetSashPosition(1, self.panel_size)
			self.msplitter.SizeWindows()	
		else:
			err('Wrong connect type %s' % conn_type_from)			
	def onShowCopyPipeline(self, evt):
		print 'onShowCopyPipeline'
		(pos_from, items_from, conn_type_from) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
		assert self.drag_pos==pos_from , 'Drag position does not match.'
		print 1,self.dd_data
		print 2,items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			self.openDesignPanelManager((self.drag_pos, self.drop_pos,items_from))
			return
		if 0:
			if conn_type_from=='host_connect':
				#conn_type = self.getConnectType()
				print (self.drag_pos,self.drop_pos,self.dd_data)
				print self.getListFromPos(self.drag_pos).getConnectType()
				conn_type_to=self.getListFromPos(self.drop_pos).getConnectType()
				if conn_type_to=='host_connect':
					self.copyFromFileToFile((pos_from,  self.drop_pos,items_from ))
				else:
					if conn_type_to=='db_connect':
						self.copyFromFileToTable((pos_from, self.drop_pos, items_from ))
					else:
						assert 1==2 , 'Drag: %s, Unknown drop connect type %s' % (conn_type_from, conn_type_to)
				return
		assert 1==2, 'Unknown connect type %s' % conn_type_from
	def onShowTcDialog(self, evt):
		print 'onShowTCDialog'
		(pos_from, items_from, conn_type_from) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
		assert self.drag_pos==pos_from , 'Drag position does not match.'
		print 1,self.dd_data
		print 2,items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			self.openDesignPanelManager((self.drag_pos, self.drop_pos,items_from))
			return
		if 0:
			if conn_type_from=='host_connect':
				#conn_type = self.getConnectType()
				print (self.drag_pos,self.drop_pos,self.dd_data)
				print self.getListFromPos(self.drag_pos).getConnectType()
				conn_type_to=self.getListFromPos(self.drop_pos).getConnectType()
				if conn_type_to=='host_connect':
					self.copyFromFileToFile((pos_from,  self.drop_pos,items_from ))
				else:
					if conn_type_to=='db_connect':
						self.copyFromFileToTable((pos_from, self.drop_pos, items_from ))
					else:
						assert 1==2 , 'Drag: %s, Unknown drop connect type %s' % (conn_type_from, conn_type_to)
				return
		assert 1==2, 'Unknown connect type %s' % conn_type_from
	def onShowPCDialog(self, evt):
		print 'onShowPCDialog'
		(pos_from, items_from, conn_type_from) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
		assert self.drag_pos==pos_from , 'Drag position does not match.'
		print 1,self.dd_data
		print 2,items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			self.copyFromPartitionToTable((pos_from, items_from))
			return
		if conn_type_from=='host_connect':
			#conn_type = self.getConnectType()
			print (self.drag_pos,self.drop_pos,self.dd_data)
			print self.getListFromPos(self.drag_pos).getConnectType()
			conn_type_to=self.getListFromPos(self.drop_pos).getConnectType()
			if conn_type_to=='host_connect':
				self.copyFromFileToFile((pos_from,  self.drop_pos,items_from ))
			else:
				if conn_type_to=='db_connect':
					self.copyFromFileToTable((pos_from, self.drop_pos, items_from ))
				else:
					assert 1==2 , 'Drag: %s, Unknown drop connect type %s' % (conn_type_from, conn_type_to)
			return
		assert 1==2, 'Unknown connect type %s' % conn_type_from
	def onShowSPCDialog(self, evt):
		print 'onShowSPCDialog'
		(pos_from, items_from, conn_type_from) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
		assert self.drag_pos==pos_from , 'Drag position does not match.'
		print 1,self.dd_data
		print 2,items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			self.copyFromSubPartitionToTable((pos_from, items_from))
			return
		if conn_type_from=='host_connect':
			#conn_type = self.getConnectType()
			print (self.drag_pos,self.drop_pos,self.dd_data)
			print self.getListFromPos(self.drag_pos).getConnectType()
			conn_type_to=self.getListFromPos(self.drop_pos).getConnectType()
			if conn_type_to=='host_connect':
				self.copyFromFileToFile((pos_from,  self.drop_pos,items_from ))
			else:
				if conn_type_to=='db_connect':
					self.copyFromFileToTable((pos_from, self.drop_pos, items_from ))
				else:
					assert 1==2 , 'Drag: %s, Unknown drop connect type %s' % (conn_type_from, conn_type_to)
			return
		assert 1==2, 'Unknown connect type %s' % conn_type_from		
	
	def onShowQueryCopyDialog(self, evt):
		print 'onShowSPCDialog'
		(pos_from, items_from, conn_type_from) =  evt.data
		#print '1',pos_from
		#print '1',items_from
		#print '2',self.drag_pos,self.drop_pos
		#print '2',self.dd_data
		assert self.drag_pos==pos_from , 'Drag position does not match.'
		print 1,self.dd_data
		print 2,items_from
		assert len(self.dd_data)==len(items_from) , 'Drag table counts does not match.'
		if conn_type_from=='db_connect':
			self.copyFromQueryToTable((self.drag_pos, self.drop_pos,items_from))
			return
		if conn_type_from=='host_connect':
			#conn_type = self.getConnectType()
			print (self.drag_pos,self.drop_pos,self.dd_data)
			print self.getListFromPos(self.drag_pos).getConnectType()
			conn_type_to=self.getListFromPos(self.drop_pos).getConnectType()
			if conn_type_to=='host_connect':
				self.copyFromFileToFile((pos_from,  self.drop_pos,items_from ))
			else:
				if conn_type_to=='db_connect':
					self.copyFromFileToTable((pos_from, self.drop_pos, items_from ))
				else:
					assert 1==2 , 'Drag: %s, Unknown drop connect type %s' % (conn_type_from, conn_type_to)
			return
		assert 1==2, 'Unknown connect type %s' % conn_type_from		
	def openDesignPanelManager(self, args):
		(pos_from, pos_to, items_from ) =  args
		useMetal = False
		print 'copyFromTableToTable'
		print pos_from
		print pos_to
		print items_from
		
		#title='TableCopy_%d.ppl' % self.t2t_id
		self.t2t_id +=1
		print type(self.panels[self.designer_pos])
		
		if type(self.panels[self.designer_pos])==EmptyPanel:	
			#sys.exit(0)
			design=DesignPanelManager(self.msplitter, self, self.designer_pos,pos_from, pos_to, items_from)
			self.msplitter.ReplaceWindow(self.panels[self.designer_pos],design)
			self.panels[self.designer_pos]=design
		else:
			self.panels[self.designer_pos].appendPanel(pos_from, pos_to, items_from)
		#TableCopyPanel(self.splitter,self, self.designer_pos,pos_from, pos_to, items_from)			
		self.msplitter.SetSashPosition(0, 330)
		self.msplitter.SetSashPosition(1, 600)
		self.msplitter.SizeWindows()	
	
		if 0:
			if 'wxMac' in wx.PlatformInfo:
				useMetal = True
				
			dlg = TableCopyDialog(self, -1, "Table Copy", size=(850, 850),
							 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
							 style=wx.wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.MAXIMIZE_BOX, # & ~wx.CLOSE_BOX,
							 useMetal=useMetal,
							 )
			dlg.CenterOnScreen()
			# this does not return until the dialog is closed.
			val = dlg.ShowModal()

			if val == wx.ID_OK:
				self.log.write("You pressed OK\n")
			else:
				self.log.write("You pressed Cancel\n")
			table_to=None
			#if dlg.status=='Start':
			#	#table_to=dlg.table_to	
			#	Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
			#if dlg.status=='DeployXml':
			#	#table_to=dlg.table_to	
			#	Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to, dlg.config_panel._tcmode) )
			#else:
			dlg.Destroy()
	def copyFromPartitionToTable(self, args):
		(pos_from,  items_from ) =  args
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = PartitionCopyDialog(self, -1, "Partition Copy", size=(850, 850),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.MAXIMIZE_BOX, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None
		#if dlg.status=='Start':
		#	#table_to=dlg.table_to	
		#	Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
		#if dlg.status=='DeployXml':
		#	#table_to=dlg.table_to	
		#	Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to, dlg.config_panel._tcmode) )
		#else:
		dlg.Destroy()		
	def copyFromSubPartitionToTable(self, args):
		(pos_from,  items_from ) =  args
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = SubPartitionCopyDialog(self, -1, "Sub-Partition Copy", size=(850, 850),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.MAXIMIZE_BOX, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None
		#if dlg.status=='Start':
		#	#table_to=dlg.table_to	
		#	Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
		#if dlg.status=='DeployXml':
		#	#table_to=dlg.table_to	
		#	Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to, dlg.config_panel._tcmode) )
		#else:
		dlg.Destroy()	
	def copyFromQueryToTable(self, args):
		#(pos_from,  items_from ) =  args
		(pos_from, pos_to, items_from ) =  args
		useMetal = False
		print 'copyFromQueryToTable'
		print pos_from
		print pos_to
		print items_from
		#form_template='table_to_table_copy'
		#Publisher().sendMessage( "open_design_form", (self.designer_pos, pos_from, pos_to, items_from, form_template) )
		#self.panels[self.designer_pos]
		#self.panels[self.designer_pos]=
		title='QueryCopy_1.ppl'
		design=DesignPanelManager(self.msplitter, self, self.designer_pos,pos_from, pos_to, items_from, title)
		self.msplitter.ReplaceWindow(self.panels[self.designer_pos],design)
		self.panels[self.designer_pos]=design
		#TableCopyPanel(self.splitter,self, self.designer_pos,pos_from, pos_to, items_from)			
		self.msplitter.SetSashPosition(0, 330)
		self.msplitter.SetSashPosition(1, 600)
		self.msplitter.SizeWindows()	
		#self.splitter.Update()
		#print dir(self.splitter)
		#splitter.AppendWindow(self.panels[(0,1)],650)	
		
		if 0:
			useMetal = False
			if 'wxMac' in wx.PlatformInfo:
				useMetal = True
				
			dlg = QueryCopyDialog(self, -1, "Query Copy", size=(850, 850),
							 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
							 style=wx.wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.MAXIMIZE_BOX, # & ~wx.CLOSE_BOX,
							 useMetal=useMetal,
							 )
			dlg.CenterOnScreen()
			# this does not return until the dialog is closed.
			val = dlg.ShowModal()

			if val == wx.ID_OK:
				self.log.write("You pressed OK\n")
			else:
				self.log.write("You pressed Cancel\n")
			table_to=None
			dlg.Destroy()	
		
	def del_copyFromPartitionToTable(self, args):
		(pos_from,  items_from ) =  args
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = PartitionCopyDialog(self, -1, "Partition Copy", size=(650, 650),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None
		if dlg.status=='Start':
			#table_to=dlg.table_to	
			Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to.dlg._tcmode) )
		if dlg.status=='Trial':
			#table_to=dlg.table_to	
			Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,_tcmode) )
		else:
			dlg.Destroy()
	def del_copyFromSubpartitionToTable(self, args):
		(pos_from,  items_from ) =  args
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = SubpartitionCopyDialog(self, -1, "Sub-partition Copy", size=(650, 650),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None
		if dlg.status=='Start':
			#table_to=dlg.table_to	
			Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
		if dlg.status=='Trial':
			#table_to=dlg.table_to	
			_tcmode='SYNC'
			Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
		else:
			dlg.Destroy()			
	def copyFromFileToTable(self, args):
		(pos_from, self.drop_pos, items_from ) =  args
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = TableCopyDialog(self, -1, "File to Table Copy", size=(650, 650),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			self.log.write("You pressed Cancel\n")
		table_to=None
		if dlg.status=='Start':
			#table_to=dlg.table_to	
			Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
		if dlg.status=='Trial':
			#table_to=dlg.table_to	
			_tcmode='SYNC'
			Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
			
	def copyFromFileToFile(self, args):
		(pos_from, self.drop_pos, items_from ) =  args
		useMetal = False
		if 'wxMac' in wx.PlatformInfo:
			useMetal = True
			
		dlg = F2FCopyDialog(self, -1, "File to File Copy", size=(650, 300),
						 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
						 style=wx.DEFAULT_DIALOG_STYLE, # & ~wx.CLOSE_BOX,
						 useMetal=useMetal,
						 )
		dlg.CenterOnScreen()
		# this does not return until the dialog is closed.
		val = dlg.ShowModal()

		if val == wx.ID_OK:
			self.log.write("You pressed OK\n")
		else:
			print val
			self.log.write("You pressed Cancel\n")
		table_to=None
		if dlg.status=='Start':
			#table_to=dlg.table_to	
			Publisher().sendMessage( "start_f2f_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to) )
		#if dlg.status=='Trial':
			#table_to=dlg.table_to	
			#Publisher().sendMessage( "generate_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data) )
		
		else:
			dlg.Destroy()	
	def gen_bind(self, type, instance, handler, *args, **kwargs):
		self.Bind(type, lambda event: handler(event, *args, **kwargs), instance)			

	def OnExit(self,e):
		self.Close(True)
	def OnClose(self, event):

		#self.ticker.Stop()
		self.Destroy()
		
		
#----------------------------------------------------------------------
def GetMondrianData():
	return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\
\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00qID\
ATX\x85\xed\xd6;\n\x800\x10E\xd1{\xc5\x8d\xb9r\x97\x16\x0b\xad$\x8a\x82:\x16\
o\xda\x84pB2\x1f\x81Fa\x8c\x9c\x08\x04Z{\xcf\xa72\xbcv\xfa\xc5\x08 \x80r\x80\
\xfc\xa2\x0e\x1c\xe4\xba\xfaX\x1d\xd0\xde]S\x07\x02\xd8>\xe1wa-`\x9fQ\xe9\
\x86\x01\x04\x10\x00\\(Dk\x1b-\x04\xdc\x1d\x07\x14\x98;\x0bS\x7f\x7f\xf9\x13\
\x04\x10@\xf9X\xbe\x00\xc9 \x14K\xc1<={\x00\x00\x00\x00IEND\xaeB`\x82' 

def GetMondrianBitmap():
	return wx.BitmapFromImage(GetMondrianImage())

def GetMondrianImage():
	import cStringIO
	stream = cStringIO.StringIO(GetMondrianData())
	return wx.ImageFromStream(stream)

def GetMondrianIcon():
	icon = wx.EmptyIcon()
	icon.CopyFromBitmap(GetMondrianBitmap())
	return icon
	
class CustomStatusBar(wx.StatusBar):
	def __init__(self, parent):
		wx.StatusBar.__init__(self, parent, -1)

		# This status bar has three fields
		self.SetFieldsCount(3)
		# Sets the three fields to be relative widths to each other.
		self.SetStatusWidths([-2, -1, -2])
		#self.log = None
		self.sizeChanged = False
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)

		# Field 0 ... just text
		self.SetStatusText("A Custom StatusBar...", 0)

		# This will fall into field 1 (the second field)
		self.cb = wx.CheckBox(self, 1001, "toggle clock")
		self.Bind(wx.EVT_CHECKBOX, self.OnToggleClock, self.cb)
		self.cb.SetValue(True)
		


	

		# set the initial position of the checkbox
		self.Reposition()

		# We're going to use a timer to drive a 'clock' in the last
		# field.
		self.timer = wx.PyTimer(self.Notify)
		self.timer.Start(1000)
		self.Notify()


	# Handles events from the timer we started in __init__().
	# We're using it to drive a 'clock' in field 2 (the third field).
	def Notify(self):
		t = time.localtime(time.time())
		st = time.strftime("%d-%b-%Y   %I:%M:%S", t)
		self.SetStatusText(st, 2)
		#self.log.WriteText("tick...\n")


	# the checkbox was clicked
	def OnToggleClock(self, event):
		if self.cb.GetValue():
			self.timer.Start(1000)
			self.Notify()
		else:
			self.timer.Stop()


	def OnSize(self, evt):
		self.Reposition()  # for normal size events

		# Set a flag so the idle time handler will also do the repositioning.
		# It is done this way to get around a buglet where GetFieldRect is not
		# accurate during the EVT_SIZE resulting from a frame maximize.
		self.sizeChanged = True


	def OnIdle(self, evt):
		if self.sizeChanged:
			self.Reposition()


	# reposition the checkbox
	def Reposition(self):
		rect = self.GetFieldRect(1)
		self.cb.SetPosition((rect.x+2, rect.y+2))
		self.cb.SetSize((rect.width-4, rect.height-4))
		self.sizeChanged = False

import wx.combo

class ListCtrlComboPopup(wx.ListCtrl, wx.combo.ComboPopup):
		
	def __init__(self, log=None):
		if log:
			self.log = log
		else:
			self.log = cu.NullLog()
			
		
		# Since we are using multiple inheritance, and don't know yet
		# which window is to be the parent, we'll do 2-phase create of
		# the ListCtrl instead, and call its Create method later in
		# our Create method.  (See Create below.)
		self.PostCreate(wx.PreListCtrl())

		# Also init the ComboPopup base class.
		wx.combo.ComboPopup.__init__(self)
		

	def AddItem(self, txt):
		self.InsertStringItem(self.GetItemCount(), txt)

	def OnMotion(self, evt):
		item, flags = self.HitTest(evt.GetPosition())
		if item >= 0:
			self.Select(item)
			self.curitem = item

	def OnLeftDown(self, evt):
		self.value = self.curitem
		self.Dismiss()


	# The following methods are those that are overridable from the
	# ComboPopup base class.  Most of them are not required, but all
	# are shown here for demonstration purposes.


	# This is called immediately after construction finishes.  You can
	# use self.GetCombo if needed to get to the ComboCtrl instance.
	def Init(self):
		self.log.write("ListCtrlComboPopup.Init")
		self.value = -1
		self.curitem = -1


	# Create the popup child control.  Return true for success.
	def Create(self, parent):
		self.log.write("ListCtrlComboPopup.Create")
		wx.ListCtrl.Create(self, parent,
						   style=wx.LC_LIST|wx.LC_SINGLE_SEL|wx.SIMPLE_BORDER)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		return True


	# Return the widget that is to be used for the popup
	def GetControl(self):
		#self.log.write("ListCtrlComboPopup.GetControl")
		return self

	# Called just prior to displaying the popup, you can use it to
	# 'select' the current item.
	def SetStringValue(self, val):
		self.log.write("ListCtrlComboPopup.SetStringValue")
		idx = self.FindItem(-1, val)
		if idx != wx.NOT_FOUND:
			self.Select(idx)

	# Return a string representation of the current item.
	def GetStringValue(self):
		self.log.write("ListCtrlComboPopup.GetStringValue")
		if self.value >= 0:
			return self.GetItemText(self.value)
		return ""

	# Called immediately after the popup is shown
	def OnPopup(self):
		self.log.write("ListCtrlComboPopup.OnPopup")
		wx.combo.ComboPopup.OnPopup(self)

	# Called when popup is dismissed
	def OnDismiss(self):
		self.log.write("ListCtrlComboPopup.OnDismiss")
		wx.combo.ComboPopup.OnDismiss(self)

	# This is called to custom paint in the combo control itself
	# (ie. not the popup).  Default implementation draws value as
	# string.
	def PaintComboControl(self, dc, rect):
		self.log.write("ListCtrlComboPopup.PaintComboControl")
		wx.combo.ComboPopup.PaintComboControl(self, dc, rect)

	# Receives key events from the parent ComboCtrl.  Events not
	# handled should be skipped, as usual.
	def OnComboKeyEvent(self, event):
		self.log.write("ListCtrlComboPopup.OnComboKeyEvent")
		wx.combo.ComboPopup.OnComboKeyEvent(self, event)

	# Implement if you need to support special action when user
	# double-clicks on the parent wxComboCtrl.
	def OnComboDoubleClick(self):
		self.log.write("ListCtrlComboPopup.OnComboDoubleClick")
		wx.combo.ComboPopup.OnComboDoubleClick(self)

	# Return final size of popup. Called on every popup, just prior to OnPopup.
	# minWidth = preferred minimum width for window
	# prefHeight = preferred height. Only applies if > 0,
	# maxHeight = max height for window, as limited by screen size
	#   and should only be rounded down, if necessary.
	def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
		self.log.write("ListCtrlComboPopup.GetAdjustedSize: %d, %d, %d" % (minWidth, prefHeight, maxHeight))
		return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, prefHeight, maxHeight)

	# Return true if you want delay the call to Create until the popup
	# is shown for the first time. It is more efficient, but note that
	# it is often more convenient to have the control created
	# immediately.    
	# Default returns false.
	def LazyCreate(self):
		self.log.write("ListCtrlComboPopup.LazyCreate")
		return wx.combo.ComboPopup.LazyCreate(self)

class ListCtrl3(wx.ListCtrl):
		
	def __init__(self,parent, log=None):
		if log:
			self.log = log
		else:
			self.log = cu.NullLog()
			

		# Since we are using multiple inheritance, and don't know yet
		# which window is to be the parent, we'll do 2-phase create of
		# the ListCtrl instead, and call its Create method later in
		# our Create method.  (See Create below.)
		#self.PostCreate(wx.PreListCtrl())

		# Also init the ComboPopup base class.
		#wx.combo.ComboPopup.__init__(self)
		wx.ListCtrl.__init__(self, parent)
		

	def AddItem(self, txt):
		self.InsertStringItem(self.GetItemCount(), txt)

	def OnMotion(self, evt):
		item, flags = self.HitTest(evt.GetPosition())
		if item >= 0:
			self.Select(item)
			self.curitem = item

	def OnLeftDown(self, evt):
		self.value = self.curitem
		self.Dismiss()


	# The following methods are those that are overridable from the
	# ComboPopup base class.  Most of them are not required, but all
	# are shown here for demonstration purposes.


	# This is called immediately after construction finishes.  You can
	# use self.GetCombo if needed to get to the ComboCtrl instance.
	def Init(self):
		self.log.write("ListCtrlComboPopup.Init")
		self.value = -1
		self.curitem = -1


	# Create the popup child control.  Return true for success.
	def Create(self, parent):
		self.log.write("ListCtrlComboPopup.Create")
		wx.ListCtrl.Create(self, parent,
						   style=wx.LC_LIST|wx.LC_SINGLE_SEL|wx.SIMPLE_BORDER)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		return True


	# Return the widget that is to be used for the popup
	def GetControl(self):
		#self.log.write("ListCtrlComboPopup.GetControl")
		return self

	# Called just prior to displaying the popup, you can use it to
	# 'select' the current item.
	def SetStringValue(self, val):
		self.log.write("ListCtrlComboPopup.SetStringValue")
		idx = self.FindItem(-1, val)
		if idx != wx.NOT_FOUND:
			self.Select(idx)

	# Return a string representation of the current item.
	def GetStringValue(self):
		self.log.write("ListCtrlComboPopup.GetStringValue")
		if self.value >= 0:
			return self.GetItemText(self.value)
		return ""

	# Called immediately after the popup is shown
	def OnPopup1(self):
		self.log.write("ListCtrlComboPopup.OnPopup")
		wx.combo.ComboPopup.OnPopup(self)

	# Called when popup is dismissed
	def OnDismiss1(self):
		self.log.write("ListCtrlComboPopup.OnDismiss")
		#wx.combo.ComboPopup.OnDismiss(self)

	# This is called to custom paint in the combo control itself
	# (ie. not the popup).  Default implementation draws value as
	# string.
	def PaintComboControl1(self, dc, rect):
		self.log.write("ListCtrlComboPopup.PaintComboControl")
		#wx.combo.ComboPopup.PaintComboControl(self, dc, rect)

	# Receives key events from the parent ComboCtrl.  Events not
	# handled should be skipped, as usual.
	def OnComboKeyEvent1(self, event):
		self.log.write("ListCtrlComboPopup.OnComboKeyEvent")
		#wx.combo.ComboPopup.OnComboKeyEvent(self, event)

	# Implement if you need to support special action when user
	# double-clicks on the parent wxComboCtrl.
	def OnComboDoubleClick1(self):
		self.log.write("ListCtrlComboPopup.OnComboDoubleClick")
	   # wx.combo.ComboPopup.OnComboDoubleClick(self)

	# Return final size of popup. Called on every popup, just prior to OnPopup.
	# minWidth = preferred minimum width for window
	# prefHeight = preferred height. Only applies if > 0,
	# maxHeight = max height for window, as limited by screen size
	#   and should only be rounded down, if necessary.
	def GetAdjustedSize1(self, minWidth, prefHeight, maxHeight):
		self.log.write("ListCtrlComboPopup.GetAdjustedSize: %d, %d, %d" % (minWidth, prefHeight, maxHeight))
		#return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, prefHeight, maxHeight)

	# Return true if you want delay the call to Create until the popup
	# is shown for the first time. It is more efficient, but note that
	# it is often more convenient to have the control created
	# immediately.    
	# Default returns false.
	def LazyCreate1(self):
		self.log.write("ListCtrlComboPopup.LazyCreate")
		#return wx.combo.ComboPopup.LazyCreate(self)

class ListCtrl4(wx.ListCtrl):
		
	def __init__(self,parent, log=None):
		if log:
			self.log = log
		else:
			self.log = cu.NullLog()
			

		# Since we are using multiple inheritance, and don't know yet
		# which window is to be the parent, we'll do 2-phase create of
		# the ListCtrl instead, and call its Create method later in
		# our Create method.  (See Create below.)
		#self.PostCreate(wx.PreListCtrl())

		# Also init the ComboPopup base class.
		#wx.combo.ComboPopup.__init__(self)
		self.parent=parent
		wx.ListCtrl.__init__(self, parent)
		

	def AddItem(self, txt):
		self.InsertStringItem(self.GetItemCount(), txt)

	def OnMotion(self, evt):
		item, flags = self.HitTest(evt.GetPosition())
		if item >= 0:
			self.Select(item)
			self.curitem = item

	def OnLeftDown(self, evt):
		self.value = self.curitem
		self.Dismiss()


	# The following methods are those that are overridable from the
	# ComboPopup base class.  Most of them are not required, but all
	# are shown here for demonstration purposes.


	# This is called immediately after construction finishes.  You can
	# use self.GetCombo if needed to get to the ComboCtrl instance.
	def Init(self):
		self.log.write("ListCtrlComboPopup.Init")
		self.value = -1
		self.curitem = -1


	# Create the popup child control.  Return true for success.
	def Create(self, parent):
		self.log.write("ListCtrlComboPopup.Create")
		wx.ListCtrl.Create(self, parent,
						   style=wx.LC_LIST|wx.LC_SINGLE_SEL|wx.SIMPLE_BORDER)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		return True


	# Return the widget that is to be used for the popup
	def GetControl(self):
		#self.log.write("ListCtrlComboPopup.GetControl")
		return self

	# Called just prior to displaying the popup, you can use it to
	# 'select' the current item.
	def SetStringValue(self, val):
		self.log.write("ListCtrlComboPopup.SetStringValue")
		idx = self.FindItem(-1, val)
		if idx != wx.NOT_FOUND:
			self.Select(idx)

	# Return a string representation of the current item.
	def GetStringValue(self):
		self.log.write("ListCtrlComboPopup.GetStringValue")
		if self.value >= 0:
			return self.GetItemText(self.value)
		return ""

	# Called immediately after the popup is shown
	def OnPopup1(self):
		self.log.write("ListCtrlComboPopup.OnPopup")
		wx.combo.ComboPopup.OnPopup(self)

	# Called when popup is dismissed
	def OnDismiss1(self):
		self.log.write("ListCtrlComboPopup.OnDismiss")
		#wx.combo.ComboPopup.OnDismiss(self)

	# This is called to custom paint in the combo control itself
	# (ie. not the popup).  Default implementation draws value as
	# string.
	def PaintComboControl1(self, dc, rect):
		self.log.write("ListCtrlComboPopup.PaintComboControl")
		#wx.combo.ComboPopup.PaintComboControl(self, dc, rect)

	# Receives key events from the parent ComboCtrl.  Events not
	# handled should be skipped, as usual.
	def OnComboKeyEvent1(self, event):
		self.log.write("ListCtrlComboPopup.OnComboKeyEvent")
		#wx.combo.ComboPopup.OnComboKeyEvent(self, event)

	# Implement if you need to support special action when user
	# double-clicks on the parent wxComboCtrl.
	def OnComboDoubleClick1(self):
		self.log.write("ListCtrlComboPopup.OnComboDoubleClick")
	   # wx.combo.ComboPopup.OnComboDoubleClick(self)

	# Return final size of popup. Called on every popup, just prior to OnPopup.
	# minWidth = preferred minimum width for window
	# prefHeight = preferred height. Only applies if > 0,
	# maxHeight = max height for window, as limited by screen size
	#   and should only be rounded down, if necessary.
	def GetAdjustedSize1(self, minWidth, prefHeight, maxHeight):
		self.log.write("ListCtrlComboPopup.GetAdjustedSize: %d, %d, %d" % (minWidth, prefHeight, maxHeight))
		#return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, prefHeight, maxHeight)

	# Return true if you want delay the call to Create until the popup
	# is shown for the first time. It is more efficient, but note that
	# it is often more convenient to have the control created
	# immediately.    
	# Default returns false.
	def LazyCreate(self):
		self.log.write("ListCtrlComboPopup.LazyCreate")
		self.parent.LazyCreate(self)
		
class ListCtrl2(wx.ListCtrl):
		
	def __init__(self, log=None):
		if log:
			self.log = log
		else:
			self.log = cu.NullLog()
			
		
		# Since we are using multiple inheritance, and don't know yet
		# which window is to be the parent, we'll do 2-phase create of
		# the ListCtrl instead, and call its Create method later in
		# our Create method.  (See Create below.)
		self.PostCreate(wx.PreListCtrl())

		# Also init the ComboPopup base class.
		#wx.combo.ComboPopup.__init__(self)
		

	def AddItem(self, txt):
		self.InsertStringItem(self.GetItemCount(), txt)

	def OnMotion(self, evt):
		item, flags = self.HitTest(evt.GetPosition())
		if item >= 0:
			self.Select(item)
			self.curitem = item

	def OnLeftDown(self, evt):
		self.value = self.curitem
		self.Dismiss()


	# The following methods are those that are overridable from the
	# ComboPopup base class.  Most of them are not required, but all
	# are shown here for demonstration purposes.


	# This is called immediately after construction finishes.  You can
	# use self.GetCombo if needed to get to the ComboCtrl instance.
	def Init(self):
		self.log.write("ListCtrlComboPopup.Init")
		self.value = -1
		self.curitem = -1


	# Create the popup child control.  Return true for success.
	def Create(self, parent):
		#self.log.write("ListCtrlComboPopup.Create")
		wx.ListCtrl.Create(self, parent,
						   style=wx.LC_LIST|wx.LC_SINGLE_SEL|wx.SIMPLE_BORDER)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		return True


	# Return the widget that is to be used for the popup
	def GetControl(self):
		#self.log.write("ListCtrlComboPopup.GetControl")
		return self

	# Called just prior to displaying the popup, you can use it to
	# 'select' the current item.
	def SetStringValue(self, val):
		self.log.write("ListCtrlComboPopup.SetStringValue")
		idx = self.FindItem(-1, val)
		if idx != wx.NOT_FOUND:
			self.Select(idx)

	# Return a string representation of the current item.
	def GetStringValue(self):
		self.log.write("ListCtrlComboPopup.GetStringValue")
		if self.value >= 0:
			return self.GetItemText(self.value)
		return ""

	# Called immediately after the popup is shown
	def OnPopup1(self):
		self.log.write("ListCtrlComboPopup.OnPopup")
		wx.combo.ComboPopup.OnPopup(self)

	# Called when popup is dismissed
	def OnDismiss1(self):
		self.log.write("ListCtrlComboPopup.OnDismiss")
		#wx.combo.ComboPopup.OnDismiss(self)

	# This is called to custom paint in the combo control itself
	# (ie. not the popup).  Default implementation draws value as
	# string.
	def PaintComboControl1(self, dc, rect):
		self.log.write("ListCtrlComboPopup.PaintComboControl")
		#wx.combo.ComboPopup.PaintComboControl(self, dc, rect)

	# Receives key events from the parent ComboCtrl.  Events not
	# handled should be skipped, as usual.
	def OnComboKeyEvent1(self, event):
		self.log.write("ListCtrlComboPopup.OnComboKeyEvent")
		#wx.combo.ComboPopup.OnComboKeyEvent(self, event)

	# Implement if you need to support special action when user
	# double-clicks on the parent wxComboCtrl.
	def OnComboDoubleClick1(self):
		self.log.write("ListCtrlComboPopup.OnComboDoubleClick")
	   # wx.combo.ComboPopup.OnComboDoubleClick(self)

	# Return final size of popup. Called on every popup, just prior to OnPopup.
	# minWidth = preferred minimum width for window
	# prefHeight = preferred height. Only applies if > 0,
	# maxHeight = max height for window, as limited by screen size
	#   and should only be rounded down, if necessary.
	def GetAdjustedSize1(self, minWidth, prefHeight, maxHeight):
		self.log.write("ListCtrlComboPopup.GetAdjustedSize: %d, %d, %d" % (minWidth, prefHeight, maxHeight))
		#return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, prefHeight, maxHeight)

	# Return true if you want delay the call to Create until the popup
	# is shown for the first time. It is more efficient, but note that
	# it is often more convenient to have the control created
	# immediately.    
	# Default returns false.
	def LazyCreate1(self):
		self.log.write("ListCtrlComboPopup.LazyCreate")
		#return wx.combo.ComboPopup.LazyCreate(self)


				
if 0:
	app = wx.App(0)
	filehunter = FileHunter(None, -1, 'File Hunter')
	app.MainLoop()
	
import wx.lib.inspection
import wx.lib.mixins.inspection
from multiprocessing import freeze_support #Process, Queue, cpu_count, current_process, 

	
if __name__ == '__main__':
	freeze_support()
	items = ['Foo', 'Bar', 'Baz', 'Zif', 'Zaf', 'Zof']

	class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
		def OnInit(self):
			import images as i
			global imgs
			imgs = i
			self.Init()
			self.frame = TabZilla(None, -1,title=prog)
			self.frame.Show(True)
			self.SetTopWindow(self.frame)
			return True

	app = MyApp(redirect=False) #=True,filename="applogfile.txt")


	from random import choice
	from sys import maxint
	if 0:
		for item in items:
			dl1.InsertStringItem(maxint, item)
			idx = dl2.InsertStringItem(maxint, item)
			dl2.SetStringItem(idx, 1, choice(items))
			dl2.SetStringItem(idx, 2, choice(items))
	app.frame.Layout()
	#wx.lib.inspection.InspectionTool().Show()
	#import code; code.interact(local=locals())
	try:
		app.MainLoop()
	except Exception, e:
		traceback.print_exc();
	
