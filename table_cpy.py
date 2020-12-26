import wx
import wx.lib.agw.flatnotebook as fnb
from tc_lib import tc_runat, tc_loc, tc_host, tc_home, tc_srv
from wx.lib.mixins.listctrl import TextEditMixin
#from editor import TacoCodeEditor, TacoTextEditor
from tc_init import *
#from wx.lib.pubsub import Publisher
import os, sys
from threading import Thread
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
import xml.dom.minidom
from xml.dom.minidom import Node, Document
from common_utils import *
from editor import TacoCodeEditor, TacoTextEditor

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

class TcCodePanel(wx.Panel):
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
		
#----------------------------------------------------------------------
# Thread class that executes processing
class ExecTcThread(Thread):
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
			(local_path,remote_path, config_file)= createPipelineConfig(self.cfrom,self.cto,self.xml_config)
			config_loc='%s%s' % (remote_path, config_file)
			Publisher().sendMessage( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
			Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
			
			#count += 10
			#dlg.Update(count)
			xml_worker='tc_copy_test.xml'
			(out_dir,worker_file,remote_loc)= createPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker, self.table_to, self._tcmode )
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
		
class TableCopyPanel(wx.Panel):
	def __init__(
			self, parent,frame,pos,drag_pos,drop_pos,dd_data #, ID, title, #size, 
			#style, useMetal=False,pos=wx.DefaultPosition, 
			):
		wx.Panel.__init__(self, parent,  id=wx.NewId())
		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.pos=pos
		self.parent=parent
		self.frame=frame
		#pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		#pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		#self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		
		self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_NO_X_BUTTON)	
		#self.initParams()
		if 1:
			(self.pos_from, self.pos_to, self.data)=(drag_pos, drop_pos, dd_data)
			#print 'init:', self.parent.drag_pos
			#print 'init:', 		self.parent.drop_pos
			#print 'init:', 		self.parent.dd_data
			
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)

		
		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.config_panel=TCD_Tab1(self,frame,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, data=self.data)
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
		Publisher().subscribe(self.onTcDeploymentCompleted,'tc_deployment_completed')
		Publisher().subscribe(self.onCreatedConfigFile, "created_config_file")
		Publisher().subscribe(self.onCreatedWorkerFile, "created_worker_file")
		Publisher().subscribe(self.onCopyDone, "copy_done")
		Publisher().subscribe(self.onCopyStatus, "copy_status")
		Publisher().subscribe(self.onShellCode, "shell_code")
		self._action=None
		#self.SetSize((850,650))
	def OnTest(self,event):		
		print 'OnTest'
		if 1:
			Publisher().sendMessage( "test_manager_panes", (1) )
			
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
			Publisher().sendMessage( "deploy_tc_xml", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )

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
			Publisher().sendMessage( "start_table_copy", (self.pos_from, self.pos_to, self.data,self.table_to, self.config_panel._tcmode) )
class TCD_Tab1(wx.Panel):
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
class DeployXmlLogPanel(wx.Panel):
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