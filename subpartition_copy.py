import wx
import wx.lib.agw.flatnotebook as fnb
from tc_lib import tc_runat, tc_loc, tc_host, tc_home, tc_srv
from wx.lib.mixins.listctrl import TextEditMixin
from editor import TacoCodeEditor, TacoTextEditor
from tc_init import *
#from wx.lib.pubsub import Publisher
import os, sys
from threading import Thread
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
import xml.dom.minidom
from xml.dom.minidom import Node, Document
from common_utils import *

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


def_profile='Compress/Copy/Rebuild indexes/Stats'
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
_flags[def_profile]=		(_OFF,		_ON,		_ON,	_ON,		_OFF,	_OFF,		_ON	)
_flags['Truncate/Copy']=	(_ON,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_ON	)
_flags['Truncate SubPart']=	(_ON,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_OFF)
_flags['Create Table']=		(_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_ON,		_OFF)
_flags['Create/Copy']=		(_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_ON,		_ON	)
_flags['Custom']=			(None,		None,		None,	None,		None,	None,		None)

cp={profile:{title:flag for (title,flag) in zip(_headers,flags)} for (profile, flags) in _flags.items()}


def createSPcPipelineConfig(cfrom,cto,config_file):
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
		config_file='temp_spec.xml'
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
	
def createSPcPipelineWorker(cfrom,cto,config, worker_file,tables,  _tcmode):
	#create config file
	max_shards=20
	print appLoc
	db_from =cfrom.split('/')[3]
	db_to =cto.split('/')[3]
	schema_from =cfrom.split('/')[-3]
	schema_to =cto.split('/')[-3]
	#print 
	#sys.exit(1)
	tmpl_loc=os.path.join(appLoc,'xml_templates')
	template_name='subpartition_copy.xml'
	tmpl_file_loc= os.path.join(tmpl_loc,template_name)
	doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
	#doc = xml.dom.minidom.parse(tmpl_file_loc)
		
	doc_to = Document()
	base = doc_to.createElement('etldataflow')
	base.setAttribute("name","SUBPARTITION_COPY")
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
		(tab,tab_to,subpartition,item) =tabs
		(subpartition_to,copy_profile, trunc,compress,stats, rebuildIdx,shards, createt, copyd) = item
		#print tabs
		#sys.exit(1)
		#('REF_CTP_MSTR', 'REF_CTP_MSTR', 'REF_CDMS_CTP_MSTR', ['REF_CDMS_CTP_MSTR', 'Compress/Copy/Rebuild indexes/Stats', 'OFF', 'ON', 'ON', 'ON', 'OFF', 'OFF', 'ON'])

		worker=xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
		#pprint(dir(worker))
		worker.setAttribute('name', tab_to)
		#param=worker.getElementsByTagName("param")[0]
		for n in worker.getElementsByTagName("param") :
			print n.getAttribute('name')
		param= [n for n in worker.getElementsByTagName("param") if n.getAttribute('name')=='SUBPARTITION'][0]
		##
		##non-partitioned table copy
		##
		param.setAttribute('value',subpartition)
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
			template_name='compress_subpartition.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))

			comp_tasklet=doc.getElementsByTagName("exec_select")[0]

			_table_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TABLE_NAME'][0]
			_table_name.setAttribute('value',tab_to)
			_dbconn=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='DB_CONNECTOR'][0]
			_dbconn.setAttribute('value','%'+db_to+'%')
			_schema_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SCHEMA_NAME'][0]
			_schema_name.setAttribute('value',schema_to)
			subpart_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SUBPARTITION'][0]
			subpart_name.setAttribute('value',subpartition)
			worker.insertBefore(comp_tasklet,exec_copy)
		print stats
		if stats=='ON':
			assert stats in ('ON', 'OFF'), 'Stats should be "ON" or "OFF".'
			tmpl_loc=os.path.join(appLoc,'xml_templates')
			template_name='gather_subpartition_stats.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))

			stats_tasklet=doc.getElementsByTagName("exec_select")[0]

			_table_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TABLE_NAME'][0]
			_table_name.setAttribute('value',tab_to)
			_dbconn=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='DB_CONNECTOR'][0]
			_dbconn.setAttribute('value','%'+db_to+'%')
			_schema_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SCHEMA_NAME'][0]
			_schema_name.setAttribute('value',schema_to)
			subpart_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SUBPARTITION'][0]
			subpart_name.setAttribute('value',subpartition)
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
	
#----------------------------------------------------------------------
# Thread class that executes processing
class ExecSPcThread(Thread):
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
			Publisher().sendMessage( "copy_status", ('Connected to %s.' % (hostname),0) )
			(local_path,remote_path, config_file)= createSPcPipelineConfig(self.cfrom,self.cto,self.xml_config)
			config_loc='%s%s' % (remote_path, config_file)
			Publisher().sendMessage( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
			Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
			
			#count += 10
			#dlg.Update(count)
			xml_worker='tc_copy_test.xml'
			(out_dir,worker_file,remote_loc)= createSPcPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker, self.table_to, self._tcmode )
			worker_loc='%s%s' % (remote_loc,worker_file)
			Publisher().sendMessage( "copy_status", ('Created worker file at %s.' %  worker_loc,0) )
			Publisher().sendMessage( "created_worker_file", (os.path.join(out_dir,worker_file)) )
			
			#count += 10
			#dlg.Update(count)
			#print self.getVarsToPath(self.drag_pos)
			#print self.getVarsToPath(self.drop_pos)
			#pprint (self.dd_data)
			#pprint(self.table_to)
			#Publisher().sendMessage( "show_tc_progress_dialog", ('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file)) )
			(out,err) =('',None)
			if not self.is_trial:
				Publisher().sendMessage( "copy_status", ('Executing table copy...',0) )
				(out,err)=execTaCo(config_loc,worker_loc)
				#Publisher().sendMessage( "table_copy_done",  (out,err) )
			else:
				#(out,err)=('Trial run completed.', 0)				
				Publisher().sendMessage( "copy_status", ('Deployment completed.',0) )
				#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
				
				#Publisher().sendMessage( "copy_status", ('#Execute at %s' % ( hostname) ,0) )
				
				(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
				Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
				Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
				Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )
				#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
			if err and err.strip().startswith('real'):
				err=[]
				out='%s\n%s' % (out, err)
				
				True
			if self.is_trial:
				Publisher().sendMessage( "tc_deployment_completed", (out,err,self.pos_to))
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

		
class SPcDeployXmlLogPanel(wx.Panel):
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
		Publisher().sendMessage( "refresh_list", (None) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'
		
class SPcCodePanel(wx.Panel):
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
		
class EditableTextListCtrl(wx.ListCtrl, TextEditMixin):
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
class SPCD_Configuration(wx.Panel):
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
		label = wx.StaticText(self, -1, "Copy %d subpartition%s." % (len(self.data),suffix))
		label.SetHelpText('Number of subpartitions to copy. \nPless "Cancel" button to do do modifications.')
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

		label = wx.StaticText(self, -1, "Drag from:",size=(80,-1))
		label.SetHelpText("Sub-Partition copy source table.")
		box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

		self.from_loc = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_from)[4:], size=(260,-1))
		self.from_loc.Enable(False)
		#text.SetLabel()
		self.from_loc.SetHelpText("Sub-Partition copy Source URL")
		box.Add(self.from_loc, 1, wx.ALIGN_CENTRE|wx.ALL, 0)
		
		label = wx.StaticText(self, -1, "From Table:",size=(60,-1))
		label.SetHelpText("Sub-Partition copy source table.")
		box.Add((10,5), 0, wx.LEFT, 0)
		box.Add(label, 0, wx.LEFT, 0)
		self.from_table = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_from).split('/')[-2], size=(200,-1))
		self.from_table.Enable(False)
		#text.SetLabel()
		self.from_table.SetHelpText("Sub-Partition copy Source Table")
		box.Add(self.from_table, 0, wx.RIGHT|wx.GROW, 0)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

		box = wx.BoxSizer(wx.HORIZONTAL)

		label = wx.StaticText(self, -1, "Drop to:",size=(80,-1))
		label.SetHelpText("Sub-Partition copy target table.")
		box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
		print 'TableCopyDialog/pos_to:', parent.pos_to
		self.to_loc = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_to)[4:], size=(260,-1))
		self.to_loc.Enable(False)
		self.to_loc.SetHelpText("Sub-Partition copy TARGET table")
		box.Add(self.to_loc, 1, wx.ALIGN_CENTRE|wx.ALL, 0)
		label = wx.StaticText(self, -1, "To Table:",size=(60,-1))
		label.SetHelpText("Sub-Partition copy target table.")
		box.Add((10,5), 0, wx.LEFT, 0)
		box.Add(label, 0, wx.LEFT, 0)
		self.to_table = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_from).split('/')[-2], size=(200,-1))
		self.to_table.Enable(True)
		#text.SetLabel()
		self.to_table.SetHelpText("Sub-Partition copy Target Table")
		box.Add(self.to_table, 0, wx.RIGHT|wx.GROW, 0)
		sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}

		self.listCtrl_t = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES,size=(200, 250))
		self.listCtrl_t.InsertColumn(0, 'From Sub-Partition')
		self.listCtrl = EditableTextListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(650, 250))
		self.listCtrl.InsertColumn(0, 'To Sub-Partition')
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
		prof=def_profile
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

		
class SubPartitionCopyDialog(wx.Dialog):
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
		self.config_panel=SPCD_Configuration(self,parent,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, data=self.data)
		self.nb.AddPage(self.config_panel, 'Configuration')
		self.code_panel=SPcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		self.nb.AddPage(self.code_panel, 'Code')
		self.deploy_panel=SPcDeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
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
		btnsizer.Add(self.btn_cancel, 0 , wx.RIGHT)
		
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
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
		Publisher().subscribe(self.onTcDeploymentCompleted,'tc_deployment_completed')
		Publisher().subscribe(self.onCreatedConfigFile, "created_config_file")
		Publisher().subscribe(self.onCreatedWorkerFile, "created_worker_file")
		Publisher().subscribe(self.onCopyDone, "copy_done")
		Publisher().subscribe(self.onCopyStatus, "copy_status")
		Publisher().subscribe(self.onShellCode, "shell_code")
		self._action=None
		self.SetSize((850,850))
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
			self.code_panel=PcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
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
			self.code_panel=PcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
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
			Publisher().sendMessage( "stop_deploy_xml_process", ('Kill deployment thread') )
		
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
				self.table_to[row[0]]=(self.config_panel.from_table.GetLabel(), self.config_panel.from_table.GetLabel(), self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
				#print  self.table_to[tname]
		self.status='DeployXml'

			
		if 0 or not self.deploy_panel:
			self.deploy_panel=PcDeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
			self.nb.AddPage(self.deploy_panel, 'Deployment log')
		self.nb.SetSelection(2)
		if 1:
			#table_to=dlg.table_to	
			self.btn_start.Enable(False)
			Publisher().sendMessage( "deploy_spc_xml", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )

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
				#self.table_to[row[0]]=(self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
				self.table_to[row[0]]=(self.config_panel.from_table.GetLabel(), self.config_panel.from_table.GetLabel(), self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
				#print  self.table_to[tname]
		#self.status='Start'
		#self.Close(True)
		self.nb.SetSelection(2)
		if 1:
			#table_to=dlg.table_to	
			self.btn_start.Enable(False)
			Publisher().sendMessage( "start_subpartition_copy", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )
		