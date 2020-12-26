if 0:
	import wxversion
	import wxversion as wv
	wv.select("3.0")
import wx
import wx.lib.agw.flatnotebook as fnb
from tc_lib import tc_runat, tc_loc, tc_host, tc_home, tc_srv
#from tc_lib import  EVT_SIGNAL, SignalEvent 
from wx.lib.mixins.listctrl import TextEditMixin
from editor import TacoCodeEditor, TacoTextEditor
from tc_init import *
import lib_callback2 as libcb
#from wx.lib.pubsub import Publisher
from tc_lib import sub, send
import os, sys, types
from threading import Thread
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
import xml.dom.minidom
from xml.dom.minidom import Node, Document
import common_utils as cu
import datetime
from editor import TacoSqlEditor
from pprint import pprint
from wx.lib.splitter import MultiSplitterWindow
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

try:
    from agw import ultimatelistctrl as ULC
except ImportError: # if it's not there locally, try the wxPython lib.
    from wx.lib.agw import ultimatelistctrl as ULC
import random

try:
	dirName = os.path.dirname(os.path.abspath(__file__))
except:
	dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.append(os.path.split(dirName)[0])

try:
	from agw import hypertreelist as HTL
	bitmapDir = "bitmaps/"
except ImportError: # if it's not there locally, try the wxPython lib.
	import wx.lib.agw.hypertreelist as HTL
	bitmapDir = "agw/bitmaps/"

from xml_generators import *
#from worker_template import *
from pipeline_template import * #pipeline_Template #, pipeline_SyncCopy, pipeline_AsyncCopy

blog= cu.BrowserLog()
plog=cu.plog
_OFF='OFF'
_ON='ON'
_na ='n/a'
_parallel='Parallel'
_truncate='Truncate'
_compress='Compress'
_stats='Stats'
_reb_idx= 'Rebuild Indexes'
_shards='Shards'
_copyd='Copy data'
_createtab='Create table'
_w_flags={}
_ppl_flags={}

def_ppl_prof='Parallel (ASYNC) Copy'
def_w_prof='Create/Copy'

_headers=							(_parallel,	_truncate,	_compress,	_stats,	_reb_idx,	_shards,_createtab,	_copyd	)
_width=								(50,		55,			59,			40,		85,			45,		70,			65	)
_w_flags['Quick Query Copy']=		(_na,		_OFF,		_OFF,		_OFF,	_OFF,		_na,	_OFF,		_ON	)
_w_flags['Truncate/Copy']=			(_na,		_ON,		_OFF,		_OFF,	_OFF,		_na,	_OFF,		_ON	)
_w_flags['Truncate Table']=			(_na,		_ON,		_OFF,		_OFF,	_OFF,		_na,	_OFF,		_OFF)
_w_flags['Create Table']=			(_na,		_OFF,		_OFF,		_OFF,	_OFF,		_na,	_ON,		_OFF)
_w_flags[def_w_prof]=				(_na,		_OFF,		_OFF,		_OFF,	_OFF,		_na,	_ON,		_ON	)
_w_flags['Custom']=					(None,		None,		None,	None,		None,	None,		None)
#pipeline flags
_ppl_flags[def_ppl_prof]=			(_ON,		_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_na)
_ppl_flags['Sequential (SYNC) Copy']=(_OFF,		_OFF,		_OFF,		_OFF,	_OFF,		_OFF,	_OFF,		_OFF)
_ppl_flags['Parallel Shards Copy']=	(_ON,		_OFF,		_OFF,		_OFF,	_OFF,		'5',		_OFF,		_OFF)
_ppl_flags['Custom']=				(None,		None,		None,	None,		None,	None,		None)

w_cp={profile:{title:flag for (title,flag) in zip(_headers,flags)} for (profile, flags) in _w_flags.items()}
ppl_cp={profile:{title:flag for (title,flag) in zip(_headers,flags)} for (profile, flags) in _ppl_flags.items()}
shrd_col_id=5
#log=Logger()

#Publisher().sendMessage( "stop_deploy_xml_process", ('Kill deployment thread') )

def log_del(msg, pos=None):
	#wx.LogMessage(msg)
	#Publisher().sendMessage( "append_log", (msg,pos) )
	send( "append_log", (msg,pos) )


EVT_RESULT_ID = wx.NewId()
 
def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


	
class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
		
		
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
		
	
import time
#----------------------------------------------------------------------
# Thread class that executes processing
class TestThread(Thread):
	"""Exec Table Copy Thread Class."""
	def __init__(self,args,run_id, is_trial=False):
		"""Init Exec Table Copy Thread Class."""
		Thread.__init__(self)
		#(self.cfrom,self.cto,self.pos_from,self.pos_to,self.xml_config) = create_spec
		#(self.xml_worker, self.table_to, self._tcmode) = create_worker
		#(self.obj,(self.local_path,self.remote_path, self.config_file),(self.out_dir,self.remote_loc, self.worker_file)) = args
		(self.obj) = args
		self.run_id=run_id
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		self.is_trial=is_trial
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()
		self.log={}
	def append_signal(self,signal,msg):
		pass
	def run(self):
		"""Run Exec Table Copy Thread."""
		"""Run Worker Thread."""
		# This is the code executing in the new thread.
		for i in range(6):
			time.sleep(3)
			amtOfTime = (i + 1) * 3
			wx.PostEvent(self.obj, ResultEvent(amtOfTime))
		time.sleep(2)
		wx.PostEvent(self.obj, ResultEvent("Thread finished!"))
		
		
#----------------------------------------------------------------------
# Thread class that executes processing
class ExecQcThread_(Thread):
	"""Exec Table Copy Thread Class."""
	def __init__(self,args,run_id, is_trial=False):
		"""Init Exec Table Copy Thread Class."""
		Thread.__init__(self)
		#(self.cfrom,self.cto,self.pos_from,self.pos_to,self.xml_config) = create_spec
		#(self.xml_worker, self.table_to, self._tcmode) = create_worker
		#(self.obj,(self.local_path,self.remote_path, self.config_file),(self.out_dir,self.remote_loc, self.worker_file)) = args
		(self.obj) = args
		self.run_id=run_id
		#self.db=db
		#self._notify_window = notify_window
		self._want_abort = 0
		self.is_trial=is_trial
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		#self.start()
		self.log={}
	def append_signal(self,signal,msg):
		pass
	def run(self):
		"""Run Exec Table Copy Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable
		#print self.q, self.user,self.limit
		
		#self.result=dbu.query(self.q, (self.user,self.sid,self.pwd), self.limit)
		#if 1:
		start_t= datetime.datetime.now()
		((status, err),(self.local_path,self.remote_path, self.config_file),(self.out_dir,self.remote_loc, self.worker_file))=self.obj.deployXML()
		if err:	
			if  not self.is_trial:
				end_t= datetime.datetime.now()
				#Publisher().sendMessage( "table_copy_done",  (status,err,self.run_id,start_t,end_t))
				self.send("table_copy_done",  (status,err,self.run_id,start_t,end_t))
			else:
				#Publisher().sendMessage( "tc_deployment_completed", (status,err,self.obj.pos))	
				end_t= datetime.datetime.now()				
				self.send("tc_deployment_completed", (status,err,self.run_id,start_t,end_t))
			if 0:
				(username, password, hostname) = tc_host[tc_srv]
				Publisher().sendMessage( "copy_status", ('Connected to %s.' % (hostname),0) )
				#config_file='temp_spec.xml'
				pplxml=xml_Pipeline()
				(local_path,remote_path, config_file)= pplxml.createQcPipelineConfig(self.cfrom,self.cto,self.xml_config)
				config_loc='%s%s' % (remote_path, config_file)
				Publisher().sendMessage( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
				Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
				
				#count += 10
				#dlg.Update(count)
				#xml_worker='tc_copy_test.xml'
				workerxml=xml_Table()
				(out_dir,worker_file,remote_loc)= workerxml.createQcPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker, self.table_to, self._tcmode )
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
			#(out,err) =('',None)
		else:
			if  not self.is_trial:
				#Publisher().sendMessage( "append_log", ('Executing partition copy...',self.obj.pos,self.run_id[0]) )
				self.send("append_log", ('Executing data copy...',self.obj.pos,self.run_id[0]) )
				
				(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
				#Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
				#Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
				#Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )				
				config_loc='%s%s' % (self.remote_path, self.config_file)
				worker_loc='%s%s' % (self.remote_loc,self.worker_file)
				(out,err)=cu.execTaCo(config_loc,worker_loc,self.run_id[0])
				#pprint (out)
				#print '**************&&&&&&&&&&&&&&&',err
				#sys.exit(0)
				end_t= datetime.datetime.now()
				#Publisher().sendMessage( "table_copy_done",  (out,err,self.run_id, start_t,end_t))
				self.send( "table_copy_done",  (out,err,self.run_id, start_t,end_t))
			else:
				#Publisher().sendMessage( "tc_deployment_completed", ((),err,self.obj.pos))
				end_t= datetime.datetime.now()
				self.send( "tc_deployment_completed", (status,err,self.run_id,start_t,end_t))
				if 0:
					#(out,err)=('Trial run completed.', 0)				
					Publisher().sendMessage( "copy_status", ('Deployment completed.',0) )
					#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
					
					#Publisher().sendMessage( "copy_status", ('#Execute at %s' % ( hostname) ,0) )
					
					(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
					Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
					Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
					Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )
					#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
					
			if 0 and err and err.strip().startswith('real'):
				err=[]
				out='%s\n%s' % (out, err)
				
				#True
			#if self.is_trial:
			#	Publisher().sendMessage( "tc_deployment_completed", (out,err,self.obj.pos)
		#else:

		#Publisher().sendMessage( "append_log", ('Done',self.obj.pos,self.run_id[0]))
		self.send("append_log", ('Done',self.obj.pos,self.run_id[0]))
			
				
				

		# Here's where the result would be returned (this is an
		# example fixed result of the number 10, but it could be
		# any Python object)
		#self.db.result=42
		#Publisher().sendMessage( "table_copy_done", ('%s/%s' % (remote_path, config_file),'%s/%s' % (remote_loc,worker_file)) )
		
	def send(self, signal, data):
		wx.PostEvent(self.obj, SignalEvent(signal, data))
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

class del_ExecQcThread(Thread):
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
			#config_file='temp_spec.xml'
			(local_path,remote_path, config_file)= createQcPipelineConfig(self.cfrom,self.cto,self.xml_config)
			config_loc='%s%s' % (remote_path, config_file)
			#Publisher().sendMessage( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
			send("copy_status", ('Created pipeline config at %s .' % config_loc,0) )
			#Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
			send("created_config_file", (os.path.join(local_path,config_file)) )
			
			#count += 10
			#dlg.Update(count)
			#xml_worker='tc_copy_test.xml'
			(out_dir,worker_file,remote_loc)= createQcPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker, self.table_to, self._tcmode )
			worker_loc='%s%s' % (remote_loc,worker_file)
			#Publisher().sendMessage( "copy_status", ('Created worker file at %s.' %  worker_loc,0) )
			send("copy_status", ('Created worker file at %s.' %  worker_loc,0) )
			#Publisher().sendMessage( "created_worker_file", (os.path.join(out_dir,worker_file)) )
			send("created_worker_file", (os.path.join(out_dir,worker_file)))
			
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
				sub("copy_status", ('Executing table copy...',0) )
				(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
				#Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
				send("shell_code", ('cd %s' % tc_path,0) )
				#Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
				send("shell_code", ('. ./.ora_profile',0))
				#Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )				
				send("shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )
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
class QcDeployXmlLogPanel(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent, style):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent=parent
		self.parentFrame=parent.frame
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
			self.gauge = wx.Gauge(self, -1, size=(-1, 12),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
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
		send("refresh_list", (None))
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'
		
class QcCodePanel(wx.Panel):
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
		self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndLabelEdit)
		#self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnListItemDeselected)
		
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
		#self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
		#Publisher().subscribe(self.OnTableNameChanged, "table_name_changed")
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
	def OnEndLabelEdit(self, event):
		print  'OnEndLabelEdit', event.m_col, event.m_itemIndex, self.GetItem(0,0).GetText(), self.editor.GetValue() 
		new_val= self.editor.GetValue()
		
		#Publisher().sendMessage( "table_name_changed", (event.m_col, event.m_itemIndex,new_val) )	
		send("table_name_changed", (event.m_col, event.m_itemIndex,new_val))
		
	#def OnListItemDeselected(self, event):
	#	print  'OnListItemDeselected', event.m_col, event.m_itemIndex, self.GetItem(0,0).GetText()
	#def OnTableNameChanged(self, evt):
	#	(col, index) = evt.data
	#	print 'OnTableNameChanged', self.GetItem(col, index).GetText()
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
			#self.SetStringItem(index, 1, 'Custom')
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
			menu.AppendMenu(self.profile_id, "Query Copy Profile", menu_cp)
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
import  wx.gizmos   as  gizmos		

import  images

class MyGizmos(wx.gizmos.TreeListCtrl): #,TextEditMixin):
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize,style=0):
		#super(MyGizmos, self).__init__(parent, id, pos, size,style)
		wx.gizmos.TreeListCtrl.__init__(self, parent, id, pos, size,style)
		#self.Bind(wx.EVT_LIST_COL_CLICK, self.OnLabel)
		#self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		#TextEditMixin.__init__(self) 
		#self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
		self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)	
		self.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.OnLeftUp)	
		self.log=cu.NullLog()
		self.selChanged=False
	def OnActivate(self, evt):
		print 'OnActivate', evt.GetItem(), self.GetItemText(evt.GetItem())
		print 'OnActivate', self.GetItemData(evt.GetItem()).GetData()
		#print dir(self.tree)
		#self.log.write('OnActivate: %s' % self.tree.GetItemText(evt.GetItem()))
	def OnSelChanged(self, evt):
		print "OnSelChanged:   ", self.GetItemText(evt.GetItem())
		#print evt.m_col, evt.m_itemIndex
		self.selChanged=True
		if 0:
			
			pos = evt.GetPosition()
			item, flags, col = self.HitTest(pos)	
			print 'OnSelChanged',  flags, col 
	def OnRightUp(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.HitTest(pos)
		if item:
			self.log.write('Flags: %s, Col:%s, Text: %s' %
						   (flags, col, self.GetItemText(item, col)))
	def OnLeftUp(self, evt):
		if self.selChanged:
			print 'passing', self.selChanged
			self.selChanged=False
		else:
			pos = evt.GetPosition()
			item, flags, col = self.HitTest(pos)
			if item:
				print 'LeftUp', self.GetItemData(item).GetData()
				(parent_id, item_id, item_type) =  self.GetItemData(item).GetData()
				self.log.write('LeftUp Flags: %s, Col:%s, Text: %s' %
							   (flags, col, self.GetItemText(item, col)))	
				self.flipItemValue(item,col,item_id)
						   
	def OnDoubleClick(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.HitTest(pos)	
		print 'OnDoubleClick', item, flags, col 
		
	def flipItemValue(self, item, col, index):
		#val=self.GetItemText(col)

		#print val
		#print truncate_id
		#index = -1 
		#selected_items = [] 
		
		offset=2
		colcnt=self.GetColumnCount()
		
		#self.SetItemText(item, 'Custom', 1)
		if col in range(offset,colcnt) and col!=(shrd_col_id+offset):			
			#self.SetStringItem(index, 1, 'Custom')
			#if index==-1: 
			#	break 

			#

			#pprint(dir(item))
			#print item.GetData()
			val=self.GetItemText(item, col)
			print val
			if val not in (_na):
				#item = self.GetItem(index, col)
				#val = item.GetText() 
				
				#selected_items.append(index) 
				if 0 and col==2:
					
					item = self.GetItem(index)
					#attr=wx.ListItemAttr()
					#attr.SetTextColour( wx.RED )
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
				#self.SetStringItem(index, col, tr[val])
				#self.SetStringItem(index, 1, tr[val])
				self.SetItemText(item, tr[val], col)

	
class GenericCopyTreeList(HTL.HyperTreeList): #,TextEditMixin):
	def __init__(self, parent, form, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize,
				 style=wx.SUNKEN_BORDER,
				 agwStyle=wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT|HTL.TR_NO_HEADER,
				 log=None):
		#super(MyGizmos, self).__init__(parent, id, pos, size,style)
		#wx.gizmos.TreeListCtrl.__init__(self, parent, id, pos, size,style)
		HTL.HyperTreeList.__init__(self, parent, id, pos, size, style, agwStyle)
		#self.Bind(wx.EVT_LIST_COL_CLICK, self.OnLabel)
		#self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		#TextEditMixin.__init__(self) 
		#self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginLabelEdit)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
		self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)	
		self.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.OnLeftUp)	
		self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self)
		self.log=cu.NullLog()
		self.selChanged=False		
		self.form=form
		self.frame=form.parentFrame
		self.ID=form.ID
		self.source=form.source
		self.target=form.target
		self.direction=form.direction
		self.lists=form.lists
		form.ts= datetime.datetime.now().strftime("%y%m%d_%H%M%S")
		#self.SetSize((400,400))
		#--------------------------------------------
		isz = (16,16)
		il = wx.ImageList(isz[0], isz[1])
		self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
		self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
		fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
		smileidx    = il.Add(images.Smiles.GetBitmap())

		self.SetImageList(il)
		self.il = il
		self.AddColumn("Pipeline/Query")
		self.AddColumn("Copy Profile")
		#self.tree.AddColumn("Truncate")
		offset=2
		if 0:
			for id in range(len(_headers)):
				self.AddColumn(_headers[id])
				self.SetColumnWidth(id+offset, _width[id])
		self.AddColumn('details')
			#self.listCtrl.InsertColumn(offset+id+1, _headers[id])
		self.SetMainColumn(0) # the one with the tree in it...
		self.SetColumnWidth(0, 400)
		self.SetColumnWidth(1, 300)
		#self.ppl_name= 'TABLE_COPY_%s_%s' % self.source
		prof=def_w_prof

		max_shards=20
		print appLoc

		#sys.exit(1)
		if 1:
			#if 
			(from_list, to_list)=self.lists
			#print self.lists
			#print t_TABLE_LIST
			wTmpl= None
			ppl_template_class_name= 'pipeline_%s_to_%s' % (from_list.current_list,to_list.current_list)
			exec('ppl=%s(self)' % ppl_template_class_name)
			#print ppl
			#sys.exit(1)
			if 0:
				ppl= block_Sync(self)
				if from_list.current_list in (t_TABLE_LIST) and to_list.current_list in (t_TABLE_LIST):
					# it's table copy
					wTmpl = worker_TableCopy(ppl)
				elif from_list.current_list in (t_PARTITION_LIST) and to_list.current_list in (t_PARTITION_LIST):
					# it's partition copy
					wTmpl = worker_PartCopy(ppl)	
				elif from_list.current_list in (t_SUBPARTITION_LIST) and to_list.current_list in (t_SUBPARTITION_LIST):
					# it's sub-partition copy
					wTmpl = worker_SubPartCopy(ppl)					
				elif from_list.current_list in (t_COLUMN_LIST) and to_list.current_list in (t_TABLE_LIST):
					# it's query copy
					wTmpl = worker_QueryCopy(ppl)					
				else:
					blog.err('Unsupported copy direction: %s -> %s' % (from_list.current_list,to_list.current_list), from_list.pos)
			if ppl:
				ppl.CreatePipelineTree()
				self.globals=ppl.globals
				self.root =ppl.root
			if 0 and wTmpl:
				#wTmpl.CreatePipelineTree()
				#self.Expand(workflow)
				#self.globals =wTmpl.globals
				#self.root =wTmpl.root
				self.globals =ppl.globals
				self.root =ppl.root
				

				#sys.exit(0)
				#pprint(dir(doc))

	def _CreatePipelineTree(self, doc):
		idx=1
		db_from =self.form.spath.split('/')[3]
		db_to =self.form.tpath.split('/')[3]
		schema_from =self.form.spath.split('/')[4]
		schema_to =self.form.tpath.split('/')[4]
		print self.form.spath
		print self.form.tpath
		print self.gl
		_tcmode='SYNC'
		if 1:
			flowt= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+db_from+'%')
			#fromschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			#fromschema.setAttribute('value',schema_from)

			todb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+db_to+'%')	
			#toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			#toschema.setAttribute('value',schema_to)

		txt = self.to_table[idx]
		self.globals = self.AppendItem(self.root, 'globals')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.SetPyData(self.globals,wx.TreeItemData(('globals',{'node_type':'globals'})))
		p=0
		for n in self.gl.getElementsByTagName("param"):
			
			#for i in range(10):
			
			child = self.AppendItem(self.globals, '%s = "%s"' %(n.getAttribute('name'),n.getAttribute('value')))
			#self.tree.SetItemText(child, def_w_prof, idx)
			print n.getAttribute('name'), n.getAttribute('value')
			#self.tree.SetItemText(child, n.getAttribute('value'), 1)
			self.SetPyData(child,wx.TreeItemData(('param',{'node_type':'param', 'name':n.getAttribute('name'),'value':n.getAttribute('value')})))
			p +=1
		#self.Expand(self.globals)
		pipeline = self.AppendItem(self.root, 'SYNC_PIPELINE')
		self.SetItemImage(pipeline, self.fldridx, which = wx.TreeItemIcon_Normal)
		self.SetItemImage(pipeline, self.fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.SetPyData(pipeline,wx.TreeItemData(('pipeline',{'node_type':'pipeline' })))
		if 0:
			callbefore = self.AppendItem(pipeline, 'CallBefore')
			#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
			#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
			self.SetPyData(callbefore,wx.TreeItemData(('CallBefore',{'node_type':'call_before' })))
		worker_stab=doc.getElementsByTagName("worker")[0].toxml()
		worker=xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
		#pprint(dir(worker))
		t_name=self.to_table[idx]
		worker.setAttribute('name',t_name )
		#param=worker.getElementsByTagName("param")[0]
		for n in worker.getElementsByTagName("param") :
			print n.getAttribute('name')
	
		for n in worker.childNodes:
			print n.nodeType
		print worker.ELEMENT_NODE,worker.ENTITY_NODE
		worker_ = self.AppendItem(pipeline, 'WORKER "%s"' % ('.'.join(self.source)))
		self.SetItemImage(worker_, self.fldridx, which = wx.TreeItemIcon_Normal)
		self.SetItemImage(worker_, self.fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.SetPyData(worker_,wx.TreeItemData(('worker',{'node_type':'worker', 'name':'.'.join(self.source)})))			
		for n in worker.childNodes:
			if n.nodeType==worker.ELEMENT_NODE:
				exec_node= n
				print exec_node
				print exec_node.nodeName
				exec_title=n.getAttribute('title')
				#sys.exit(0)
				#exec_copy=worker.getElementsByTagName(exec_node.nodeName)[0]
				self.util_node= [n for n in exec_node.childNodes if n.nodeType==worker.ELEMENT_NODE][0]
				print  self.util_node.nodeName
				util_method=self.util_node.getAttribute('method')
				print util_method
				#sys.exit(1)
				#tasklet=worker.getElementsByTagName(self.util_node.nodeName)[0]
				#tasklet=worker.getElementsByTagName(self.util_node.nodeName)[0]
				if 0 : #tab<>tab_to:
					_to_table=[n for n in self.util_node.getElementsByTagName("param") if n.getAttribute('name')=='TO_TABLE'][0]
					if _to_table:
						_to_table.setAttribute('value',t_name)
					else:
						param = doc_to.createElement('param')
						param.setAttribute('name','TO_TABLE')
						param.setAttribute('value',t_name)
						self.util_node.appendChild(param)
						
				
				#self.tree.SetItemText(wk, 'Template: Query Copy', 1)

				task = self.AppendItem(worker_, 'task "%s" 11' % exec_title)
				#self.tree.SetItemText(wk, 'Template: Query Copy', 1)
				self.SetItemImage(task, self.fldridx, which = wx.TreeItemIcon_Normal)
				self.SetItemImage(task, self.fldropenidx, which = wx.TreeItemIcon_Expanded)			
				self.SetPyData(task,wx.TreeItemData((exec_node.nodeName,{'node_type':'exec_node', 'util_node_name':self.util_node.nodeName,'util_method':util_method})))
				
				locals = self.AppendItem(task, 'locals')
				#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
				#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
				self.SetPyData(locals,wx.TreeItemData(('locals',{'node_type':'locals', })))
				p=0
				for n in self.util_node.getElementsByTagName("param"):
					#print 
					
					#self.tree.SetItemText(child, def_w_prof, idx)
					print n.getAttribute('name'), n.getAttribute('value')
					#self.tree.SetItemText(child, n.getAttribute('value'), 1)
					value=n.getAttribute('value')
					if n.getAttribute('name') in ('TO_TABLE','TABLE_NAME'):
						value=self.target[1]
					if n.getAttribute('name')in ('TO_SCHEMA','SCHEMA_NAME'):
						value=self.target[0]							
					if n.getAttribute('name')in ('SUBPARTITION') and len(self.target)>3:
						value=self.target[3]	
					else:
						if n.getAttribute('name')in ('PARTITION') and len(self.target)>2:
							value=self.target[2]
					if n.getAttribute('name') in ('DB_CONNECTOR','TO_DB'):
						value='%'+db_to+'%'							
					print  value
					child = self.AppendItem(locals, '%s = "%s"' % (n.getAttribute('name'),value))
					self.SetPyData(child,wx.TreeItemData(('param',{'node_type':'param', 'name':n.getAttribute('name'),'value':value })))
					p +=1
				#self.Expand(locals)
				#sys.exit(0)
				#self.q=self.createQuery(form.data,form.spath)
				#self.schema_table='.'.join(self.source)
				cd= [n for n in self.util_node.getElementsByTagName("sql_template")[0].childNodes if n.nodeType==worker.CDATA_SECTION_NODE][0]
				cdata = self.AppendItem(task, '"%s"' % cd.data)
				
				#self.tree.SetItemText(query, '%s...' % q[:15], 1)
				
				#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
				#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
				self.SetPyData(cdata,wx.TreeItemData(('cdata',{'node_type':'sql_template', 'tag':'sql_template','cdata':cd.data})))
				#self.Expand(task)
		self.Expand(worker_)
		callafter = self.AppendItem(pipeline, 'CallAfter')
		#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.SetPyData(callafter,wx.TreeItemData(('CallAfter',{'node_type':'call_after' })))	
		self.Expand(pipeline)
	def _getXmlFileNames(self, ts=None):
		if not ts:
			ts= self.form.ts
		return ('pipeline_config_%s.xml' % ts, 'tc_query_copy_%s.xml' % ts)		
	def _getXMLConnector(self, doc, conn_env, conn_name):
		conn=doc.getElementsByTagName("connector")[0]
		assert conn, 'Cannot find connector tag.'
		print conn_env
		env_type=conn_env.split('.')[0]
		env=conn.getElementsByTagName(env_type)[0]
		alias_name=conn_env.split('.')[1]
		alias=env.getElementsByTagName(alias_name)[0]
		
		connector=alias.getElementsByTagName(conn_name)[0]	
		return connector
	
	def _createPipelineConfig(self,cfrom,cto,config_file):
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
			print doc,path_from[2],path_from[3]
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
			ps=doc.getElementsByTagName("default")
			base.appendChild(ps[0])
			ps=doc.getElementsByTagName("worker")
			base.appendChild(ps[0])			
			#print doc_to.toxml()			
			out_dir=os.path.join(activeProjLoc,'out')
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
			(status, err)=cu.rcopyFile(out_file,'%s/%s' % (remote_loc,config_file),self.ID)
			#sys.exit(1)
		return ((status, err),out_dir,remote_loc, config_file)
	def getExecMode(self):
		#print dir(self.globals)
		print self.globals.GetChildrenCount()
		for item in self.globals.GetChildren():
			print self.GetPyData(item).GetData()
	def getGlobals(self):
		#print dir(self.globals)
		#print self.globals.GetChildrenCount()
		#pprint(self.globals)
		#sys.exit(1)
		g={}
		d= dict((self.GetPyData(item).GetData()[1]['name'],self.GetPyData(item).GetData()) for item in self.globals.GetChildren())
		return d
	def _createPipelineWorker(self, cfrom,cto,config, worker_file):
		#create config file
		max_shards=20
		print appLoc
		db_from =cfrom.split('/')[3]
		db_to =cto.split('/')[3]
		schema_from =cfrom.split('/')[4]
		schema_to =cto.split('/')[4]
		print cfrom
		print cto
		_globals=self.getGlobals()
		print _globals
		_tcmode=_globals['FLOW_TYPE']
		#sys.exit(1)
		doc_to = Document()
		elem={}
		(root,attr)=self.GetPyData(self.root).GetData()
		root_elem = doc_to.createElement(root)
		
		for key,val in attr.items():
			root_elem.setAttribute(key,val )
		#sys.exit(0)
		root_elem.setAttribute("pipeline_config",config)
		for r in self.root.GetChildren():
			(r_tag, attr)=self.GetPyData(r).GetData()
			print '------------', r_tag
			tag_elem = None
			if r_tag in ('runat'):
				pass
			elif r_tag in ('globals'):
				tag_elem = doc_to.createElement(r_tag)
				if r.GetChildrenCount()>0:
					for par in r.GetChildren():
						(param, attr)=self.GetPyData(par).GetData()
						param_elem = doc_to.createElement(param)
						print param	, attr			
						for key,val in attr.items():
							print key,val
							param_elem.setAttribute(key,val )
						tag_elem.appendChild(param_elem)
				#root_elem.appendChild(tag_elem)
			elif r_tag in ('pipeline'): #process 'PIPELINE' section
				#tag_elem = doc_to.createElement(r_tag)
				#tag_elem =root_elem
				for w in r.GetChildren():
					print '***',w.GetText()
					(w_tag, attr)=self.GetPyData(w).GetData()
					print 0,w_tag, attr
					w_elem = doc_to.createElement(w_tag)
					if w_tag in ('worker'):
						for name,value in attr.items():
							w_elem.setAttribute(name,value )
						for t in w.GetChildren():
							#print t.GetText()
							(t_tag, attr)=self.GetPyData(t).GetData()
							print 1,t_tag,attr
							#sys.exit(1)
							t_elem = doc_to.createElement(t_tag)
							t_utils=doc_to.createElement(attr['util_node_name'])
							t_utils.setAttribute('method',attr['util_method'] )
							for v in t.GetChildren():
								(v_tag, attr)=self.GetPyData(v).GetData()
								print 2,v_tag, attr
								if v_tag in ('locals'):
									for p in v.GetChildren():
										(p_tag, attr)=self.GetPyData(p).GetData()
										print 3,p_tag, attr
										if p_tag in ('param'):
											par=doc_to.createElement('param')
											for name,value in attr.items():
												par.setAttribute(name,value )
											t_utils.appendChild(par)
								if v_tag in 'cdata':
									if 'tag' in attr.keys():
										tag=doc_to.createElement(attr['tag'])
										
										if 'cdata' in attr.keys():
											data=doc_to.createCDATASection(attr['cdata']) 
											tag.appendChild(data)
										else:
											tag.data='SELECT * FROM DUAL'
										t_utils.appendChild(tag)
							t_elem.appendChild(t_utils)
							w_elem.appendChild(t_elem)
					root_elem.appendChild(w_elem)
			if tag_elem:
				root_elem.appendChild(tag_elem)
			#elem[root].setAttribute(param,config)
		
		#sys.exit(0)
		#base.setAttribute("pipeline_config",config)
		#globals = doc_to.createElement('globals')		
		#for g,i in _globals.items():
		#	globals.setAttribute(i[0],i[1])
		#base.appendChild(globals)
		if 0:
			tmpl_loc=os.path.join(appLoc,'xml_templates')
			template_name='trunc_comp_stats_sharded_spart_copy.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
			worker_stab=doc.getElementsByTagName("worker")[0].toxml()
			worker = xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
		#base.appendChild(worker)
		doc_to.appendChild(root_elem)
		
		if 0:
			tmpl_loc=os.path.join(appLoc,'xml_templates')
			template_name='trunc_comp_stats_sharded_spart_copy.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
			#doc = xml.dom.minidom.parse(tmpl_file_loc)
				
			doc_to = Document()
			base = doc_to.createElement('etldataflow')
			
			base.setAttribute("pipeline_config",config)
			
			#pprint(dir(base))
			doc_to.appendChild(base)
			gl=doc.getElementsByTagName("globals")[0]
			print gl
			flowt= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+db_from+'%')
			#fromschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			#fromschema.setAttribute('value',schema_from)

			todb= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+db_to+'%')	
			#toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			#toschema.setAttribute('value',schema_to)
			
			base.appendChild(gl)
			worker_stab=doc.getElementsByTagName("worker")[0].toxml()
			print worker_stab
			#pprint(dir(doc))

		
		if 0:
			not_sharded='OFF'
			for ppl_name, ppl_item in pipeline.items():
				(ppl_name,tabs, queries, ppl_flags,tables) =ppl_item
				base.setAttribute("name","TABLE_COPY_%s" % ppl_name)
				(discard,ppl_copy_profile, ppl_parallel,ppl_trunc,ppl_compress,ppl_stats, ppl_rebuildIdx,ppl_shards, ppl_createt, ppl_copyd) = ppl_flags
				print ppl_flags
				for tab_id in range(len(tables)):
					query=queries[tab_id-1]
					tab_flags=tables[tab_id]
					#print tab
					(t_name,t_copy_profile, t_parallel,t_trunc,t_compress,t_stats, t_rebuildIdx,t_shards, t_createt, t_copyd) = tab_flags
					#print tabs
					#sys.exit(1)
					#('REF_CTP_MSTR', 'REF_CTP_MSTR', 'REF_CDMS_CTP_MSTR', ['REF_CDMS_CTP_MSTR', 'Compress/Copy/Rebuild indexes/Stats', 'OFF', 'ON', 'ON', 'ON', 'OFF', 'OFF', 'ON'])

					worker=xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
					#pprint(dir(worker))
					worker.setAttribute('name', t_name)
					#param=worker.getElementsByTagName("param")[0]
					for n in worker.getElementsByTagName("param") :
						print n.getAttribute('name')
					#param= [n for n in worker.getElementsByTagName("param") if n.getAttribute('name')=='SUBPARTITION'][0]
					##
					##non-partitioned table copy
					##
					#param.setAttribute('value',subpartition)
					exec_copy=worker.getElementsByTagName("exec_query_copy")[0]
					
					tasklet=worker.getElementsByTagName("table_utils")[0]
					if 1 : #tab<>tab_to:
						_to_table=[n for n in tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TO_TABLE'][0]
						if _to_table:
							_to_table.setAttribute('value',t_name)
						else:
							param = doc_to.createElement('param')
							param.setAttribute('name','TO_TABLE')
							param.setAttribute('value',t_name)
							tasklet.appendChild(param)
					#modify CDATA
					print t_createt
					if 	t_createt in ('ON', 'OFF'):
						#Truncate should be "ON" or "OFF".
						tr={'ON':"1",'OFF':"0"}
						_create_t=[n for n in tasklet.getElementsByTagName("param") if n.getAttribute('name')=='IF_CREATE_TARGET_TABLE'][0]
						if _create_t:
							_create_t.setAttribute('value',tr[t_createt])
						else:
							param = doc_to.createElement('param')
							param.setAttribute('name','IF_CREATE_TARGET_TABLE')					
							param.setAttribute('value',tr[t_trunc])
							tasklet.appendChild(param)			
					if 0:
						if t_shards ==not_sharded:
							pass
						else:
							assert int(t_shards)>2 and int(t_shards)<max_shards, 'Num of t_shards should be between 2 and %d per table.'  % max_shards
							param = doc_to.createElement('param')
							param.setAttribute('name','NUM_OF_SHARDS')
							param.setAttribute('value',t_shards)
							tasklet.appendChild(param)
					print t_trunc
					if 	t_trunc in ('ON', 'OFF'):
						#Truncate should be "ON" or "OFF".
						param = doc_to.createElement('param')
						param.setAttribute('name','IF_TRUNCATE')
						tr={'ON':"1",'OFF':"0"}
						param.setAttribute('value',tr[t_trunc])
						tasklet.appendChild(param)	
					print t_compress 
					if 	t_compress=='ON':
						assert t_compress in ('ON', 'OFF'), 'Compress should be "ON" or "OFF".'
						tmpl_loc=os.path.join(appLoc,'xml_templates')
						template_name='compress_subpartition.xml'
						tmpl_file_loc= os.path.join(tmpl_loc,template_name)
						
						doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))

						comp_tasklet=doc.getElementsByTagName("exec_select")[0]

						_table_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TABLE_NAME'][0]
						_table_name.setAttribute('value',t_name)
						_dbconn=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='DB_CONNECTOR'][0]
						_dbconn.setAttribute('value','%'+db_to+'%')
						_schema_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SCHEMA_NAME'][0]
						_schema_name.setAttribute('value',schema_to)
						subpart_name=[n for n in comp_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SUBPARTITION'][0]
						subpart_name.setAttribute('value',subpartition)
						worker.insertBefore(comp_tasklet,exec_copy)
					print t_stats
					if t_stats=='ON':
						assert t_stats in ('ON', 'OFF'), 'Stats should be "ON" or "OFF".'
						tmpl_loc=os.path.join(appLoc,'xml_templates')
						template_name='gather_table_stats.xml'
						tmpl_file_loc= os.path.join(tmpl_loc,template_name)
						
						doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read().replace('\r', ''))

						stats_tasklet=doc.getElementsByTagName("exec_select")[0]

						_table_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='TABLE_NAME'][0]
						_table_name.setAttribute('value',t_name)
						_dbconn=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='DB_CONNECTOR'][0]
						_dbconn.setAttribute('value','%'+db_to+'%')
						_schema_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SCHEMA_NAME'][0]
						_schema_name.setAttribute('value',schema_to)
						#subpart_name=[n for n in stats_tasklet.getElementsByTagName("param") if n.getAttribute('name')=='SUBPARTITION'][0]
						#subpart_name.setAttribute('value',subpartition)
						worker.appendChild(stats_tasklet)
						
						
					if 0:
						if 	t_rebuildIdx in ('ON', 'OFF'):
							print 't_rebuildIdx', t_rebuildIdx
							#t_rebuildIdx should be "ON" or "OFF"
							param = doc_to.createElement('param')
							param.setAttribute('name','SKIP_INDEX_MAINTENANCE')
							tr={'ON':"TRUE",'OFF':"FALSE"}
							param.setAttribute('value','TRUE')
							tasklet.appendChild(param)		
							param = doc_to.createElement('param')
							param.setAttribute('name','IF_REBUILD_UNUSABLE_INDEXES')
							tr={'ON':"1",'OFF':"0"}
							param.setAttribute('value',tr[t_rebuildIdx])
							tasklet.appendChild(param)	

						
					cd= [n for n in tasklet.getElementsByTagName("sql_template")[0].childNodes if n.nodeType==worker.CDATA_SECTION_NODE][0]
					#for n in cd.childNodes:
					#	print n
					#pprint(dir(cd))
					
					#schema= cd.wholeText.split('.')[0]
					cd.data=query
					#param=worker.getElementsByTagName("param")[0]
					base.appendChild(worker)
			#print doc_to.toprettyxml()
		
		out_dir=os.path.join(activeProjLoc,'out')
		#worker_file='tc_temp_worker.xml'
		out_file=os.path.join(out_dir,worker_file)
		f = open(out_file,'w')
		#from xml.dom.minidom import parseString

		pretty_print =  '\n'.join([line for line in doc_to.toprettyxml(indent=' '*2).split('\n') if line.strip()])


		f.write(pretty_print)
		f.close()
		#remote_loc='/home/zkqfas6/tab_copy/clients/table_copy/tab_copy'
		(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]
		remote_loc='%s/%s' % (tc_path, client_path) 
		print 'echo %s|pscp %s\\%s bk94994@swmapetldev01.nam.nsroot.net:%s' % (lpwd,out_dir,worker_file,remote_loc)
		#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,worker_file,remote_loc))
		(status, err)=cu.rcopyFile(os.path.join(out_dir,worker_file),'%s/%s' % (remote_loc,worker_file),self.ID)
		#create worker file
		return (out_dir,remote_loc, worker_file)
		
	def del_createQuery(self,data, spath):
			q='SELECT '
			for i in range(len(data)):
				item = data[i]
				q='%s %s\n,' % (q,item[2])
				print item
			#sys.exit(1)
			from_loc=spath
			#sys.exit(0)
			from_table=from_loc.split('/')[5]
			from_schema=from_loc.split('/')[4]
			q='%s  FROM %s.%s' % (q.strip(','),from_schema, from_table)
			ext=''
			if len(from_loc.split('/'))==8:
				ext='SUBPARTITION (%s)' % from_loc.split('/')[7]
			if len(from_loc.split('/'))==7:
				ext='SUBPARTITION (%s)' % from_loc.split('/')[6]
			q='%s %s' % (q, ext)
			return q		
	def OnBeginEdit(self, evt):
		print "OnBeginEdit:    ", self.GetItemText(evt.GetItem())
		# we can prevent nodes from being edited, for example let's
		# not let the root node be edited...
		item = evt.GetItem()
		if item == self.tree.GetRootItem():
			evt.Veto()
			print "*** Edit was vetoed!"		
	def OnActivate(self, evt):
		print 'OnActivate', evt.GetItem(), self.GetItemText(evt.GetItem())
		print 'OnActivate', self.GetPyData(evt.GetItem()).GetData()
		#print dir(self.tree)
		#self.log.write('OnActivate: %s' % self.tree.GetItemText(evt.GetItem()))
	def OnSelChanged(self, evt):
		print "OnSelChanged:   ", self.GetItemText(evt.GetItem())
		#print evt.m_col, evt.m_itemIndex
		self.selChanged=True
		if 0:
			
			pos = evt.GetPosition()
			item, flags, col = self.HitTest(pos)	
			print 'OnSelChanged',  flags, col
	def getTmplList(self, node_type):
		tmpl_types={}
		tmpl_types['task']=['Truncate Table','Compress Table','Sharded Table Copy','Gather Table Stats']
		tmpl_types['worker']=['Sharded Copy with Stats']
		tmpl_types['pipeline']=['Table Copy']
		tmpl_types['etldataflow']=['Sequential Pipeline','Parallel Pipeline']
	
	def OnRightUp(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.HitTest(pos)
		if item:
			print flags, col, self.GetItemText(item, col)
			print item
			(_, idata) = self.GetPyData(item).GetData()
			print idata
			type(idata)
			node_type=idata['node_type']
		#print type, name, method
		menu = wx.Menu()
		if 0:
			submenu = wx.Menu()
			submenu.Append(301, 'radio item1', kind=wx.ITEM_RADIO)
			submenu.Append(302, 'radio item2', kind=wx.ITEM_RADIO)
			submenu.Append(302, 'radio item3', kind=wx.ITEM_RADIO)

			item2 = menu.AppendMenu(wx.ID_ANY, "Type (%s)" % node_type,submenu)
		else:
			menu.Append(wx.ID_ANY, "Disable Item")
			
		menu.AppendSeparator()
		if 1:
			strs = "Make Item Text Not Bold"
		else:
			strs = "Make Item Text Bold"
		item3 = menu.Append(wx.ID_ANY, strs)
		item4 = menu.Append(wx.ID_ANY, "Change Item Font")
		item13 = menu.Append(wx.ID_ANY, "Change Item Background Colour")
		menu.AppendSeparator()
		if 1:
			strs = "Set Item As Non-Hyperlink"
		else:
			strs = "Set Item As Hyperlink"
		item5 = menu.Append(wx.ID_ANY, strs)
		menu.AppendSeparator()

		item7 = menu.Append(wx.ID_ANY, "Disable Item")
		
		menu.AppendSeparator()
		item8 = menu.Append(wx.ID_ANY, "Change Item Icons")
		menu.AppendSeparator()
		item9 = menu.Append(wx.ID_ANY, "Get Other Information For This Item")
		menu.AppendSeparator()

		item10 = menu.Append(wx.ID_ANY, "Delete Item")
		if item == self.GetRootItem():
			item10.Enable(False)
		item11 = menu.Append(wx.ID_ANY, "Prepend An Item")
		item12 = menu.Append(wx.ID_ANY, "Append An Item")

		self.Bind(wx.EVT_MENU, self.OnTest, item2)
		self.Bind(wx.EVT_MENU, self.OnTest, item3)
		self.Bind(wx.EVT_MENU, self.OnTest, item4)
		self.Bind(wx.EVT_MENU, self.OnTest, item5)
		self.Bind(wx.EVT_MENU, self.OnTest, item7)
		self.Bind(wx.EVT_MENU, self.OnTest, item8)
		self.Bind(wx.EVT_MENU, self.OnTest, item9)
		self.Bind(wx.EVT_MENU, self.OnTest, item10)
		self.Bind(wx.EVT_MENU, self.OnTest, item11)
		self.Bind(wx.EVT_MENU, self.OnTest, item12)
		self.Bind(wx.EVT_MENU, self.OnTest, item13)
		
		self.PopupMenu(menu)
		menu.Destroy()	
	def OnTest(self, event):	
		print 'menu test'
	def _getFromConnect(self):
		return ['user_name','SID_NAME']
	def OnLeftUp(self, evt):
		if self.selChanged:
			#print 'passing', self.selChanged
			self.selChanged=False
		else:
			pos = evt.GetPosition()
			item, flags, col = self.HitTest(pos)
			if item:
				print 'LeftUp', self.GetPyData(item).GetData()
				(name, ddict) =  self.GetPyData(item).GetData()
				#self.log.write('LeftUp Flags: %s, Col:%s, Text: %s' %
				#			   (flags, col, self.GetItemText(item, col)))	
				#self.flipItemValue(item,col,item_id)
				#pprint(dir(item))
				#print 'GetText',item.GetText()
				#print 'GetText',item.GetText()
				if ddict['node_type'] in 'query':
					#print ddict['cdata']
					from query_edit import QueryEditor
					file_to_open='test.sql'
					#print item
					#print self.source
					#sys.exit(1)
					#from_conn=self.getXMLConnector(doc,self.source[2],self.source[3])
					#from_conn=self.getFromConnect()
					(from_list, to_list) = self.lists
					from_conn= from_list.getConnectInfo()
					#sys.exit(1)
					dlg = QueryEditor(self, sys.stdout,'Editing query template.', from_conn,item)
					dlg.CenterOnScreen()
					# this does not return until the dialog is closed.
					val=dlg.Show()
					#print 'dialog val=', val,wx.ID_OK					
						   
	def OnDoubleClick(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.HitTest(pos)	
		print 'OnDoubleClick', item, flags, col 
		
	def flipItemValue(self, item, col, index):
		#val=self.GetItemText(col)

		#print val
		#print truncate_id
		#index = -1 
		#selected_items = [] 
		
		offset=2
		colcnt=self.GetColumnCount()
		
		#self.SetItemText(item, 'Custom', 1)
		if col in range(offset,colcnt) and col!=(shrd_col_id+offset):			
			#self.SetStringItem(index, 1, 'Custom')
			#if index==-1: 
			#	break 

			#

			#pprint(dir(item))
			#print item.GetData()
			val=self.GetItemText(item, col)
			print val
			if val not in (_na):
				#item = self.GetItem(index, col)
				#val = item.GetText() 
				
				#selected_items.append(index) 
				if 0 and col==2:
					
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
				#self.SetStringItem(index, col, tr[val])
				#self.SetStringItem(index, 1, tr[val])
				self.SetItemText(item, tr[val], col)
class TacoLogger_simple(wx.Panel):
	"""Panel for the Taco deploy xml log panel"""
	def __init__(self, parent, style=1):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent=parent
		#self.parentFrame=parent.frame
		#suffix=''
		#self.label = wx.StaticText(self, -1, 'Started code deployment.')
		#self.label.SetLabel("Hello World!")
		#self.label.SetHelpText('Deployment status.')
		self.logList = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_VRULES|wx.LC_HRULES)
		self.logList.InsertColumn(0, 'Time')
		self.logList.InsertColumn(1, 'Message')
		self.logList.SetColumnWidth(0, 50)
		self.logList.SetColumnWidth(1, 600)


		self.logList.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
		if 1:
			#self.listCtrl_t.InsertStringItem(0, '/'.join(spath.split('/')[3:5]))
			self.logList.InsertStringItem(0, 'time')
			#self.listCtrl.InsertStringItem(0, prof)
			self.logList.SetStringItem(0, 1, 'test message')
		self.sizer.Add(self.logList, 1, wx.GROW|wx.ALL, 5)

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

			self.SetItemCount(1000000)
			
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
		#pprint(charge)
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
			msg =charge[0].strip()
			if msg:
				self.SetStringItem(idx, 1, charge[0].strip())
				if if_error:
					item = self.GetItem(idx,1)
					item.SetMask(ULC.ULC_MASK_BACKCOLOUR)
					pink=wx.Colour(255, 168, 168, 255)
					item.SetBackgroundColour(pink)
					self.SetItem(item)	
					
	def appendList_(self, items,now,charge, if_error=False):
		if len(charge)==1 and type(charge)==types.ListType and '\n' in charge[0]:
			charge=charge[0].split('\n')
		#pprint(charge)
		
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
			#pprint (msg)
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
	def __init__(self, parent, pos,panel_id, style=1):
		wx.Panel.__init__(self, parent, -1, style=style)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.parent=parent
		self.pos=pos
		self.panel_id=panel_id
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
		self.sizer.Fit(self)
		print self.logList._mainWin
		#Publisher().subscribe(self.OnAppendLog, "append_log")
		sub(self.__OnAppendLog, "append_log")
		#Publisher().subscribe(self.OnAppendErr, "append_err")
		sub(self.__OnAppendErr, "append_err")
	def Status(self, msg):
		self.label.SetLabel(msg) 
		self.logger.AppendText(msg+'\n')
		#print(dir(self.logger))
		#sys.exit(1)
	def OnAppendLog_del(self, evt):
		(msg,pos,panel_id) = evt.data
		print 'Got message',msg,pos,panel_id
		if pos==self.pos:
			if panel_id!=None:
				if panel_id==self.panel_id:
					self.logList.append(msg)	
			else:
				self.logList.append(msg)
	def msg(self, msg):
		self.logList.append(msg)
	def err(self, err):
		self.logList.appendErr(err)
		
	def __OnAppendLog(self, data, extra1, extra2=None):
		(msg,pos,panel_id) = data
		
		if pos==self.pos:
			print '<<<<<<<<<<<<<<<<<<<<<<<<<Got message',msg,pos,panel_id
			if panel_id!=None:
				if panel_id==self.panel_id:
					if not msg=='\n':
						self.logList.append(msg)	
			else:
				self.logList.append(msg)				
	def OnAppendErr_del(self, evt):
		(err,pos,panel_id) = evt.data
		if pos==self.pos:
			if panel_id!=None:
				if panel_id==self.panel_id:
					#self.logList.appendErr(out)	
					self.logList.appendErr(err)	
			else:
				#self.logList.appendErr(out)	
				self.logList.appendErr(err)	
	def __OnAppendErr(self, data, extra1, extra2=None):
		(err,pos,panel_id) = data
		if pos==self.pos:
			if panel_id!=None:
				if panel_id==self.panel_id:
					#self.logList.appendErr(out)	
					self.logList.appendErr(err)	
			else:
				#self.logList.appendErr(out)	
				self.logList.appendErr(err)					
	def OnExit(self,e):
		#Publisher().sendMessage( "refresh_list", (None) )
		send( "refresh_list", (None) )
		self.parentFrame.MakeModal(False)
		self.parentFrame.Close(True)

		
	def OnBackground(self,e):
		print 'OnBackground'
		
#--------------------------------------------------------------------------------------------------		
class PCD_Configuration(wx.Panel):
	"""Panel for copy config"""
	def __init__(self, parent,style,data,pos,spath,tpath, sides, lists):
		wx.Panel.__init__(self, parent, -1, style=style)
		self.data=data
		self.parent=parent
		self.ID=parent.ID
		self.parentFrame=parent.frame
		self.pos=pos
		self.lists=lists
		#ID_TC_MODE = wx.NewId()
		ID_RUN_AT = wx.NewId()
		sizer = wx.BoxSizer(wx.VERTICAL)
		(self.source, self.target)=sides
		suffix=''
		self.direction =(parent.pos_from,parent.pos_to)
		if len(self.data)>1:
			suffix='s'
		#label = wx.StaticText(self, -1, "Copy %d subpartition%s." % (len(self.data),suffix))
		#label = wx.StaticText(self, -1, 'Query copy.')
		#label.SetHelpText('Number of subpartitions to copy. \nPless "Cancel" button to do do modifications.')
		#self.mode_btn = wx.Button(self, ID_TC_MODE, "Mode(SYNC/sequential copy)",style=wx.BU_EXACTFIT)
		#self.mode_btn.Enable(True) 
		#self.runat_btn = wx.Button(self, ID_RUN_AT, "Run at %s (%s)" % (tc_host[tc_srv][2],tc_home),style=wx.BU_EXACTFIT)
		#self.runat_btn.Enable(True)
		#mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
		#mode_sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(self.mode_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(self.runat_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		#mode_sizer.Add((6,6),0)
		#mode_sizer.Add(shards_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)		
		#sizer.Add(mode_sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
		
		#self.Bind(wx.EVT_BUTTON,self.OnTCModeButton, id=ID_TC_MODE)
		#self.Bind(wx.EVT_BUTTON,self.OnRunAtButton, id=ID_RUN_AT)
		
		box = wx.BoxSizer(wx.HORIZONTAL)

		#label = wx.StaticText(self, -1, "Copy from:",size=(80,-1))
		#label.SetHelpText("Sub-Partition copy source table.")
		#box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 0)
		#print self.parentFrame
		self.spath=spath
		self.tpath=tpath
		if 0:
			if 0:
				self.spath=self.parentFrame.getVarsToPath(parent.pos_from)
				self.tpath=self.parentFrame.getVarsToPath(parent.pos_to)		
			else:
				self.spath='root/ORACLE/DEV.oracle/DEV_connect/USER/TEST_TABLE'
				self.tpath='root/ORACLE/QA.oracle/QA_connect/USER/QA_TEST_TABLE'
		#self.from_loc = wx.TextCtrl(self, -1,'/'.join(spath.split('/')[1:5]), size=(300,-1))
		#self.from_loc.Enable(False)
		#text.SetLabel()
		#self.from_loc.SetHelpText("Sub-Partition copy Source URL")
		#box.Add(self.from_loc, 1, wx.ALIGN_CENTRE|wx.ALL, 0)
		
		#label = wx.StaticText(self, -1, "From Table:",size=(60,-1))
		#label.SetHelpText("Sub-Partition copy source table.")
		#box.Add((10,5), 0, wx.LEFT, 0)
		#box.Add(label, 0, wx.LEFT, 0)
		#self.from_table = wx.TextCtrl(self, -1, self.parentFrame.getVarsToPath(parent.pos_from).split('/')[-2], size=(200,-1))
		#self.from_table.Enable(False)
		#text.SetLabel()
		#self.from_table.SetHelpText("Sub-Partition copy Source Table")
		#box.Add(self.from_table, 0, wx.RIGHT|wx.GROW, 0)
		#sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		if 0:
			box = wx.BoxSizer(wx.HORIZONTAL)

			label = wx.StaticText(self, -1, "Copy to:",size=(80,-1))
			label.SetHelpText("Sub-Partition copy target table.")
			box.Add(label, 0, wx.ALIGN_LEFT|wx.ALL,0)
			print 'TableCopyDialog/pos_to:', parent.pos_to
			self.to_loc = wx.TextCtrl(self, -1, '/'.join(tpath.split('/')[1:5]), size=(260,-1))
			self.to_loc.Enable(False)
			self.to_loc.SetHelpText("Sub-Partition copy TARGET table")
			box.Add(self.to_loc, 1, wx.ALIGN_CENTRE|wx.ALL, 0)
			#label = wx.StaticText(self, -1, "To Table:",size=(60,-1))
			#label.SetHelpText("Sub-Partition copy target table.")
			#box.Add((10,5), 0, wx.LEFT, 0)
			#box.Add(label, 0, wx.LEFT, 0)
			#self.to_table = wx.TextCtrl(self, -1, '', size=(200,-1))
			#self.to_table.Enable(True)
			#text.SetLabel()
			#self.to_table.SetHelpText("Sub-Partition copy Target Table")
			#box.Add(self.to_table, 0, wx.RIGHT|wx.GROW, 0)
			sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.tc_tables={}
		self.shards_btn={}
		self.splitter =MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE) # wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
		self.splitter.SetOrientation(wx.VERTICAL)		
		#self.splitter.SetSashSize(2)
		#self.splitter.SetBackgroundColour('#000000')
		
		
			
		if 0:
			if 0:
				self.listCtrl_t = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES,size=(200, 250))
				self.listCtrl_t.InsertColumn(0, 'From db')
			self.listCtrl = EditableTextListCtrl(self.splitter, -1, style=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES, size=(650, 80))
			self.listCtrl.InsertColumn(0, 'To Table (Editable)')
			self.listCtrl.InsertColumn(1, 'Query Copy Profile')
			offset=1
			for id in range(len(_headers)):
				self.listCtrl.InsertColumn(offset+id+1, _headers[id])
			if 0:
				self.listCtrl.InsertColumn(offset+1, 'Truncate')
				self.listCtrl.InsertColumn(offset+2, 'Compress')
				self.listCtrl.InsertColumn(offset+3, 'Stats')
				self.listCtrl.InsertColumn(offset+4, 'Rebuild Indexes')
				self.listCtrl.InsertColumn(offset+5, 'Shards')
			#self.listCtrl_t.SetColumnWidth(0, 200)
			self.listCtrl.SetColumnWidth(0, 220)
			self.listCtrl.SetColumnWidth(1, 200)
			self.listCtrl.SetColumnWidth(offset+1, 55)
			self.listCtrl.SetColumnWidth(offset+2, 59)
			self.listCtrl.SetColumnWidth(offset+3, 40)
			self.listCtrl.SetColumnWidth(offset+4, 100)
			self.listCtrl.SetColumnWidth(offset+5, 45)
			prof=def_w_prof

			#for i in range(len(self.data)):
			self.listCtrl.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
			if 1:
				i=0
				item = self.data[i]
				
				#box.Add((10,5),0)
				tname=item[2].strip('[]')
				#self.listCtrl_t.InsertStringItem(0, '/'.join(spath.split('/')[3:5]))
				self.listCtrl.InsertStringItem(0, to_table)
				#self.listCtrl.InsertStringItem(0, prof)
				self.listCtrl.SetStringItem(0, 1, prof)
				
		
				flags=_w_flags[prof]	
				for pid in range(len(flags)):
					print pid
					self.listCtrl.SetStringItem(0, offset+pid+1, flags[pid])
				#item = self.listCtrl.GetItem(0)
				#font = item.GetFont()
				#font.SetSize(18)
				#item.SetFont(font)
				#self.listCtrl.SetItem(item)	
				#sys.exit(1)
		

			#lists = wx.BoxSizer(wx.HORIZONTAL)
			
			#lists.Add(self.listCtrl_t, 0, wx.GROW|wx.EXPAND, 0)
			#lists.Add(self.listCtrl, 1, wx.GROW|wx.EXPAND|wx.ALL, 0)
			
			#sizer.Add(self.listCtrl, 0, wx.EXPAND|wx.ALL, 1)
		self.log=cu.NullLog()
		#wx.gizmos.TreeListCtrl
		if 1:
			idx=1
			self.log = UltTacoLogger(self.splitter,self.pos,self.parent.ID) 		
		self.tree = GenericCopyTreeList(self.splitter,self, -1 #, #style =
										#wx.TR_DEFAULT_STYLE
										#| wx.TR_HAS_BUTTONS
										#| wx.TR_TWIST_BUTTONS
										#| wx.TR_ROW_LINES
										#| wx.TR_COLUMN_LINES
										#| wx.TR_NO_LINES 
										#| wx.TR_EDIT_LABELS
										#| wx.TR_FULL_ROW_HIGHLIGHT
										#| 0x40000
								   )		

		
		

		#self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		#self.tree.Bind(wx.EVT_LIST_COL_CLICK, self.OnLabel)
		#self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		#self.tree.Bind(wx.EVT_TREE_ITEM_SELECTED, self.OnTreeItemSelected)
		#self.tree.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnTreeLabelEdit)
		#self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnTreeLabelEditEnd)
		#self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
		if 1:
			#self.nbe = fnb.FlatNotebook(self.splitter, -1, agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_NO_X_BUTTON|fnb.FNB_HIDE_ON_SINGLE_TAB)				

				#self.nbe.AddPage(self.log, 'Log')
			
			
			if 0:
				q='--place your query here\n\nSELECT '
				for i in range(len(self.data)):
					item = self.data[i]
					q='%s %s\n,' % (q,item[2])
					print item
				#sys.exit(1)
				
				#from_loc=self.parentFrame.getVarsToPath(parent.pos_from)
				from_loc=spath
				#sys.exit(0)
				from_table=from_loc.split('/')[5]
				from_schema=from_loc.split('/')[4]
				q='%s  FROM %s.%s' % (q.strip(','),from_schema, from_table)
				ext=''
				if len(from_loc.split('/'))==8:
					ext='SUBPARTITION (%s)' % from_loc.split('/')[7]
				if len(from_loc.split('/'))==7:
					ext='SUBPARTITION (%s)' % from_loc.split('/')[6]
			#q=self.tree.createQuery(self.data,self.spath)
			#self.query.SetText(q)
			
			
			self.splitter.SetMinimumPaneSize(100)
			#self.splitter.SplitHorizontally(self.tree, self.nbe)
			self.splitter.AppendWindow(self.tree,600)				
			self.splitter.AppendWindow(self.log)				
			#splitter.AppendWindow(self.panels[(0,2)],200)				
			#sys.exit(1)
			#wnd_size=(1200,1050)
			#self.splitter.SetSashPosition(0, wnd_size[0]/2)
			#self.splitter.SetSashPosition(1, 0)
			self.splitter.SizeWindows()
			sizer.Add(self.splitter, 1, wx.GROW|wx.EXPAND|wx.ALL, 0)

		#sizer.Add(self.splitter, 1, wx.GROW|wx.EXPAND|wx.ALL)	
		#sizer.Add(self.tree, 1, wx.GROW|wx.EXPAND|wx.ALL)	
		#sizer.Add(self.nbe, 1, wx.GROW|wx.EXPAND|wx.ALL, 1)
		#self.tree.Expand(self.tree.root)
		self.tcmodes={'SYNC':'SYNC/sequential copy', 'ASYNC': 'ASYNC/parallel copy'}
		self._tcmode='SYNC'
		self._runat='%s.%s' % (tc_srv, tc_home)
		self.SetSizer(sizer)
		sizer.Fit(self)
		#Publisher().subscribe(self.OnTableNameChanged, "table_name_changed")
		sub(self.OnTableNameChanged, "table_name_changed")
		#Publisher().subscribe(self.onAdjustDesignLogger, "adjust_design_logger")
		sub(self.__onAdjustDesignLogger, "adjust_design_logger")
	def onAdjustDesignLogger_del(self,evt):
		(width,height) = evt.data
		#selected = self.nbe.GetPage(idx)
		self.splitter.SetSashPosition(0, (height/4)*1)
		self.splitter.SizeWindows()
	def __onAdjustDesignLogger(self,data, extra1, extra2=None):
		(width,height) = data
		#selected = self.nbe.GetPage(idx)
		self.splitter.SetSashPosition(0, (height/5)*2)
		self.splitter.SizeWindows()
	def OnTreeLabelEdit(self, event):
		"""Edit tree label (only root label can be edited)."""
		item = event.GetItem()
		if item != self.tree.root:
			event.Veto()
		pos = evt.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		print 'OnTreeLabelEdit'
		print item, flags, col
		

	def OnTreeLabelEditEnd(self, evt):
		"""End editing the tree label."""
		#self.projectdirty = True
		pos = evt.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		print 'OnTreeLabelEditEnd'
		print item, flags, col
		
		
	def OnTreeItemSelected(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		print 'OnLabel'
		print item, flags, col
	def OnLabel(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		print 'OnLabel',item, flags, col

	def OnActivate(self, evt):
		print 'OnActivate', evt.GetItem(), self.tree.GetItemText(evt.GetItem())
		print 'OnActivate', self.tree.GetItemData(evt.GetItem()).GetData()
		#print dir(self.tree)
		#self.log.write('OnActivate: %s' % self.tree.GetItemText(evt.GetItem()))
		
		

	def OnRightUp(self, evt):
		pos = evt.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		if item:
			self.log.write('Flags: %s, Col:%s, Text: %s' %
						   (flags, col, self.tree.GetItemText(item, col)))

	def OnSize(self, evt):
		self.tree.SetSize(self.GetSize())
		
	def OnTableNameChanged(self,evt):
		(col, idx, new_val) = evt.data
		#selected = self.nbe.GetPage(idx)
		self.nbe.SetPageText(idx,new_val)
		
	def OnTCModeButton1(self, event):
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
	def CreateTcModeMenu1(self):

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
				
	def OnTcModeMenu1(self, event, params):
		(id, label) = params
		print 'OnTcModeMenu', id, label
		self.mode_btn.SetLabel('Mode(%s)' % label)
		self._tcmode=id	
	def OnRunAtMenu(self, event, params):
		(id, label) = params
		print 'OnRunAtMenu', id, label
		self.runat_btn.SetLabel("Run at %s" % label)
		self._runat=id	
if 1:
	#from lib_callback2 import *
	class dxml(object):
		def __init__(self):
			pass
		def new_deployXML(self,*args):
			(a,b,c)=args
			print a,b
			#print c
			#print dir(c)
			print 'cleanlog'
			#print 'new_deployXML'
			ID=b['ID']
			#sys.exit(1)
			#plog.log('new_deployXML',ID)
			#self.send("append_log", ('new_deployXML',(0,1),ID) )
			return (22)
		def deployXML(self,*args):
			#conf= self.config_panel
			#tree=conf.tree
			(a,b,c)=args
			tree=b['tree']
			self.status='DeployXml'

			((status, err),(local_path,remote_path, config_file),(out_dir,remote_loc, worker_file))=((0, None),(None,None, None),(None,None, None))
			if 0 and not self.deploy_panel:
				self.deploy_panel=PcDeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
				self.nb.AddPage(self.deploy_panel, 'Deployment log')
			#self.nb.SetSelection(2)
			pipeline=xml_Table(tree)
			if 1:
				#table_to=dlg.table_to	
				
				if 1:
					(username, password, hostname) = tc_host[tc_srv]
					self.log('Connected to %s.' % hostname)
					#config_file='temp_spec.xml'
					(self.xml_config, self.xml_worker)= pipeline.getXmlFileNames()
					print self.xml_config, self.xml_worker
					((status, err),local_path,remote_path, config_file)=  pipeline.createPipelineConfig(self.cfrom,self.cto,self.xml_config)
					print 'status:',status
					print err
					#print local_path,remote_path, config_file
					#sys.exit(0)
					if not err:
						self._tcmode='SYNC'
						(out_dir,remote_loc, worker_file)= pipeline.createPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker)
						worker_loc='%s%s' % (remote_loc,worker_file)
						#Publisher().sendMessage( "copy_status", ('Created worker file at %s.' %  worker_loc,0) )
						#Publisher().sendMessage( "created_worker_file", (os.path.join(out_dir,worker_file)) )

				#Publisher().sendMessage( "deploy_qc_xml", (self.pos_from, self.pos_to, self.data,self.table_to, conf._tcmode) )
			return ((status, err),(local_path,remote_path, config_file),(out_dir,remote_loc, worker_file))
		
	def new_deployXML(*args):
		(a,b,c)=args
		print a,b
		print 'new_deployXML'
		ID=b['ID']
		#sys.exit(1)
		plog.log('new_deployXML',ID)
		return (22)
		
class GenericCopyPanel(wx.Panel):
	def __init__(self, parent,pos,drag_pos, drop_pos, dd_data, sides, lists,title):
		self.ID=wx.NewId()
		wx.Panel.__init__(self, parent,self.ID, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.pos=pos 
		self.parent=parent
		self.frame=parent.frame
		self.run_id=0
		self.title=title
		#self.table_from=table_name
		(self.source,self.target)=sides
		self.lists=lists
		#print lists[0].current_list
		#sys.exit(1)
		self.confLoc={}
		self.workerLoc={}		
		#pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		#pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		#self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		
		#self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_BOTTOM|fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_NO_X_BUTTON)	
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
		if 1:
			self.cfrom=self.frame.getVarsToPath(parent.pos_from)
			self.cto=self.frame.getVarsToPath(parent.pos_to)	
			self.schema_from= self.cfrom.split('/')[-1]
			#print self.schema_from
			#sys.exit(0)
			#self.schema_to=

		else:
			#root/ORACLE/DEV.oracle/test_DEV/OWNER_5 
			#root/ORACLE/DEV.oracle/CVOL_SMARTS1/OWNER_9
			self.cfrom='root/ORACLE/DEV.oracle/test_DEV/CSMARTREF/TEST_TABLE'
			self.cto='root/ORACLE/QA.oracle/test_QA/CSMARTREF/QA_TEST_TABLE'
		#print self.cfrom, self.cto
		#sys.exit(0)
		self.config_panel=PCD_Configuration(self,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, data=self.data,pos=pos, spath=self.cfrom, tpath=self.cto, sides=sides, lists=self.lists)
		#self.nb.AddPage(self.config_panel, 'Configuration')
		#self.code_panel=QcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		#self.nb.AddPage(self.code_panel, 'Code')
		#self.deploy_panel=QcDeployXmlLogPanel(self,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		#self.nb.AddPage(self.deploy_panel, 'Log')		
		sizer.Add(self.config_panel, 1, wx.EXPAND|wx.GROW|wx.ALL, 1)
		#line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		#sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_start = wx.Button(self, ID_START, "Run Data Copy")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		ID_TRIAL = wx.NewId()
		self.btn_trial = wx.Button(self, ID_TRIAL, "Deploy XML", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()

		#self.btn_cancel = wx.Button(self, ID_EXIT, 'Close')
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		btnsizer.Add((3,3),0)
		btnsizer.Add(self.btn_start, 0)
		#btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		btnsizer.Add((35,5),0)
		btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		btnsizer.Add((5,5),1, wx.EXPAND)
		#btnsizer.Add(self.btn_cancel, 0 , wx.RIGHT)
		sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		self.Bind(wx.EVT_BUTTON, self.OnDeployXml, id=ID_TRIAL)
		if 1:
			btnsizer = wx.BoxSizer(wx.HORIZONTAL)
			#self.btn_backgr = wx.Button(self, ID_BACKGROUND, "Background",size=(-1,20))
			#self.btn_backgr.Disable()
			self.btn_stop = wx.Button(self, ID_STOP, "Stop", size=(50,15))

			#button2.Disable()
			#self.btn_close = wx.Button(self, ID_EXIT, "Close", size=(50,20))
			#self.btn_close.Disable()
			self.count=0
			self.gauge = wx.Gauge(self, -1, size=(-1, 12),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
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
			
			sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 0)
			#self.SetSizer(self.sizer)
			#self.sizer.Fit(self)
			#self.timer.Start(100)
		
		


		self.SetSizer(sizer)
		sizer.Fit(self)
		self.status='Exit'
		#self.deploy_panel=None
		#self.code_panel=None
		#self.tcmodes=OrderedDict({'SYNC':'SYNC/sequential copy', 'ASYNC': 'ASYNC/parallel copy'})

		#print self.tcmodes.keys()
		#sys.exit(1)
		if 0:
			Publisher().subscribe(self.onTcDeploymentCompleted,'tc_deployment_completed')
			#Publisher().subscribe(self.onTcDeploymentCompleted,'tc_deployment_completed')
			Publisher().subscribe(self.onCreatedConfigFile, "created_config_file")
			Publisher().subscribe(self.onCreatedWorkerFile, "created_worker_file")
			Publisher().subscribe(self.onCopyDone, "table_copy_done")
			Publisher().subscribe(self.onCopyStatus, "copy_status")
			Publisher().subscribe(self.onShellCode, "shell_code")
		sub(self.__onTcDeploymentCompleted,'tc_deployment_completed')
		sub(self.onCreatedConfigFile, "created_config_file")
		sub(self.onCreatedWorkerFile, "created_worker_file")
		sub(self.__onCopyDone, "table_copy_done")
		sub(self.onCopyStatus, "copy_status")
		#sub(self.onShellCode, "shell_code")
		sub(self.__onJobKilled, "job_killed")
		#sub(self.__onDeployJobKilled, "copy_deploy_killed")
		self._action=None
		#self.SetSize((850,850))
		#'open_xml_viewer'
		sub(self.__onOpenXmlViewer, "open_xml_viewer")
		EVT_SIGNAL(self, self.relaySignal)
		self.job_type='S'
	def __onJobKilled(self, data, extra1, extra2=None):
		print '__onJobKilled'
		print data
		if 1:
			self.btn_start.Enable(True)
			self.btn_trial.Enable(True)
			self.btn_stop.Enable(False)
			self.gauge.SetValue(100)
			self.timer.Stop()
			plog.err('Job aborted.',self.ID)
			end_t= datetime.datetime.now()	
			dt= (end_t-self.start_t)
			elapsed= str(dt).rstrip('0')
			print self.job_type
			if self.job_type in ('T'):
				send( "update_transfer_log", ((self.ID,self.run_id),elapsed,[],'Aborted') )	
			if self.job_type in ('D'):
				send( "update_deploy_log", ((self.ID,self.run_id),elapsed,[],'Aborted') )					
	def __onDeployJobKilled_del(self, data, extra1, extra2=None):
		print '__onJobKilled'
		print data
		if 1:
			self.btn_start.Enable(True)
			self.btn_trial.Enable(True)
			self.btn_stop.Enable(False)
			self.gauge.SetValue(100)
			self.timer.Stop()
			plog.err('Job aborted.',self.ID)
			end_t= datetime.datetime.now()	
			dt= (end_t-self.start_t)
			elapsed= str(dt).rstrip('0')
			send( "update_deploy_log", ((self.ID,self.run_id),elapsed,[],'Aborted') )				
	def getSourceObjectType(self):
			(from_list, to_list)=self.lists
			#print self.lists
			#print t_TABLE_LIST
			#wTmpl= None
			#ppl_template_class_name= 'pipeline_%s_to_%s' % (from_list.current_list,to_list.current_list)
			#exec('ppl=%s(self)' % ppl_template_class_name)
			#print ppl
			#sys.exit(1)
			obj_type='undefined'
			if 1:
				#ppl= block_Sync(self)
				if from_list.current_list in (t_TABLE_LIST):
					# it's table copy
					obj_type='Table'
				elif from_list.current_list in (t_PARTITION_LIST) :
					# it's partition copy
					obj_type='Partition'	
				elif from_list.current_list in (t_SUBPARTITION_LIST) :
					# it's sub-partition copy
					obj_type='Subpartitoin'					
				elif from_list.current_list in (t_COLUMN_LIST) :
					# it's query copy
					obj_type='Query'					
			return obj_type

	def relaySignal(self, msg):
		"""
		Receives data from thread and updates the display
		"""
		print  msg.data
		print  msg.signal
		send(msg.signal,msg.data)
		
	def __onOpenXmlViewer(self, data, extra1, extra2=None):
		print '__onOpenXmlViewer'
		print data
		(panel_ID,run_id,created_dt) = data			
		print run_id,created_dt
		if int(panel_ID)==self.ID:
			useMetal=False
			if 1:
				if 'wxMac' in wx.PlatformInfo:
					useMetal = True
					
				dlg = XmlViewerDialog(self, -1, "%s Copy" % self.getSourceObjectType(), run_id, size=(850, 1050),
								 #style=wx.CAPTION | wx.SYSTEM_MENU | wx.THICK_FRAME,
								 style=wx.wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN|wx.MAXIMIZE_BOX, # & ~wx.CLOSE_BOX,
								 useMetal=useMetal,
								 )
				dlg.CenterOnScreen()
				# this does not return until the dialog is closed.
				val = dlg.ShowModal()


				#if dlg.status=='Start':
				#	#table_to=dlg.table_to	
				#	Publisher().sendMessage( "start_table_copy", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to,dlg._tcmode) )
				#if dlg.status=='DeployXml':
				#	#table_to=dlg.table_to	
				#	Publisher().sendMessage( "deploy_tc_xml", (self.drag_pos,self.drop_pos,self.dd_data,dlg.table_to, dlg.config_panel._tcmode) )
				#else:
				dlg.Destroy()
		else:
			print 'Expecting panel %s, got %s' % (self.ID,panel_ID)
		if 0:
			self.code_panel=PcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
			self.nb.AddPage(self.code_panel, 'Local')
			#self.nb.SetSelection(0)	
			file_loc =self.confLoc[run_id][0]
			print file_loc
			if os.path.isfile(file_loc):
				f = open(file_loc, 'r')			
				self.code_panel.specs.SetValue(f.read())
				f.close()		
		
		
	def updateDisplay(self, msg):
		"""
		Receives data from thread and updates the display
		"""
		t = msg.data
		if isinstance(t, int):
			print ("Time since thread started: %s seconds" % t)
		else:
			print ("%s" % t)


		
	def OnDeployXml(self,e):
		self.table_to={}
		self.job_type='D'
		self._action='D'
		#self.code_panel.shell.SetValue('')
		self.gauge.SetValue(10)
		self.timer.Start(100)
		self.btn_start.Enable(False)
		self.btn_trial.Enable(False)
		self.btn_stop.Enable(True)
		self.run_id +=1
		self.log('started job %d' % self.run_id)
		

		if 1:
			send( 'show_deployment_log',(1))
			#Publisher().sendMessage( 'append_transfer_log', (((self.ID,self.run_id),self.source[-1],'Partition','/'.join(self.cfrom.split('/')[3:]),'/'.join(self.cto.split('/')[3:]),'n/a','Started','n/a','n/a'),))
			send('append_deployment_log', (((self.ID,self.run_id),self.title,self.source[-1],self.getSourceObjectType(),'/'.join(self.cfrom.split('/')[3:]),'/'.join(self.cto.split('/')[3:]),'Started','n/a'),))
		

		self.start_t= datetime.datetime.now()
		if 1:
			((status, err),(self.local_path,self.remote_path, self.config_file),(self.out_dir,self.remote_loc, self.worker_file))=self.deployXML()
			print (status, err)
		if err:	
			if 1:
				#Publisher().sendMessage( "tc_deployment_completed", (status,err,self.obj.pos))	
				end_t= datetime.datetime.now()				
				self.send("tc_deployment_completed", (status,err,self.run_id,self.start_t,end_t))
		else:
			if  1:
				#Publisher().sendMessage( "tc_deployment_completed", ((),err,self.obj.pos))
				end_t= datetime.datetime.now()
				send( "tc_deployment_completed", (status,err,self.run_id,self.start_t,end_t))
		send("append_log", ('Done',self.pos,self.run_id))
		
		if 1:
			self.btn_start.Enable(True)
			self.btn_trial.Enable(True)
			self.btn_stop.Enable(False)
			self.gauge.SetValue(100)
			self.timer.Stop()

	def deployXML(self):
		conf= self.config_panel
		tree=conf.tree

		self.status='DeployXml'

		((status, err),(local_path,remote_path, config_file),(out_dir,remote_loc, worker_file))=((0, None),(None,None, None),(None,None, None))
		if 0 and not self.deploy_panel:
			self.deploy_panel=PcDeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(750, 750))
			self.nb.AddPage(self.deploy_panel, 'Deployment log')
		#self.nb.SetSelection(2)
		pipeline=xml_Table(tree)

		if 1:
			#table_to=dlg.table_to	
			
			if 1:
				(username, password, hostname) = tc_host[tc_srv]
				self.log('Connected to %s.' % hostname)
				#config_file='temp_spec.xml'
				(self.xml_config, self.xml_worker)= pipeline.getXmlFileNames()
				print self.xml_config, self.xml_worker
				rcopy_args =  pipeline.createPipelineConfig(self.cfrom,self.cto,self.xml_config)
				self.confLoc[self.run_id]=rcopy_args
				#(local_file,remote_file, config_file)
				#out_file=os.path.join(out_dir,config_file)
				if 0:
					(status, err)=cu.rcopyFile(rcopy_args[0],rcopy_args[1],(0,1), self.ID)
							
				
				if 0:
					(local_path,remote_path, config_file)= createQcPipelineConfig(self.cfrom,self.cto,self.xml_config)
					config_loc='%s%s' % (remote_path, config_file)
					Publisher().sendMessage( "copy_status", ('Created pipeline config at %s .' % config_loc,0) )
					Publisher().sendMessage( "created_config_file", (os.path.join(local_path,config_file)) )
					
					#count += 10
					#dlg.Update(count)
					#xml_worker='tc_copy_test.xml'
				print 'status:',status
				print err
				#print local_path,remote_path, config_file
				#sys.exit(0)
				if not err:
					self._tcmode='SYNC'
					 
					rcopy_args2= pipeline.createPipelineWorker(self.cfrom,self.cto,self.xml_config,self.xml_worker)
					self.workerLoc[self.run_id]=rcopy_args2
					#(local_file,remote_file, worker_file_name)=
					#worker_loc='%s%s' % (remote_loc,worker_file)
					#Publisher().sendMessage( "copy_status", ('Created worker file at %s.' %  worker_loc,0) )
					#Publisher().sendMessage( "created_worker_file", (os.path.join(out_dir,worker_file)) )
					if 0:
						(status, err)=cu.rcopyFile(self.rcopy_args2[0],self.rcopy_args2[1],(0,1),self.ID)
					if 1:
						#app = wx.App(0)
						#from lib_callback2 import *
						sys._excepthook = libcb.excepthook
						try:
							#depl= dxml()
							#print '-----------------------before tansfer'
							pprint(rcopy_args)
							result = libcb.run_function_as_process_in_dialog(
								parent=self,
								thread_function=cu.pui_rcopyFile,
								title="Pipeline file",
								message="Running pipeline file copy process...",
								args=(rcopy_args[0],rcopy_args[1],(0,1), self.ID),
								#kwargs={'tree':self.config_panel.tree},
								callback=None,
								project_id=self.ID,
								job_id=self.run_id
							)
							print '-----------------------------------------------------------------after transfer'
							
							print result
							#if (result is not None) :
							#print '>>>>>>>>>>>',result
							#print result
							plog.log('Pipeline XML file copy completed.', self.ID)
						except RuntimeError, e :
							#print 'RuntimeError', str(e)
							#pass
							plog.err(str(e),self.ID)
							print 'error', str(e)
						#finally:
						#	print 'error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
						else:
							#print '--------------------else'
							#print 'result', result
							#raise Exception_expected
							plog.log('Success.',self.ID)
						wx.Yield()

					
					if 1:
						#app = wx.App(0)
						#from lib_callback2 import *
						sys._excepthook = libcb.excepthook
						try:
							#depl= dxml()
							print '-----------------------before tansfer'
							pprint(rcopy_args2)
							result = libcb.run_function_as_process_in_dialog(
								parent=self,
								thread_function=cu.pui_rcopyFile,
								title="Worker file",
								message="Running worker file copy process...",
								args=(rcopy_args2[0],rcopy_args2[1],(0,1), self.ID),
								#kwargs={'tree':self.config_panel.tree},
								callback=None
							)
							#print '--------------------after transfer'
							#if (result is not None) :
							#print '>>>>>>>>>>>',result
							#print result
							plog.log('Worker XML file copy completed.', self.ID)
						except RuntimeError, e :
							#print 'RuntimeError', str(e)
							#pass
							plog.err(str(e),self.ID)
						else:
							#print '--------------------else'
							#print 'result', result
							#raise Exception_expected
							plog.log('Success.',self.ID)
						wx.Yield()
			#Publisher().sendMessage( "deploy_qc_xml", (self.pos_from, self.pos_to, self.data,self.table_to, conf._tcmode) )
		return ((status, err),rcopy_args,rcopy_args2)
	def onCopyStatus(self, evt):
		print 'onTableCopyStatus'
		(out,err) = evt.data

		#self.Log(out)
		#Publisher().sendMessage( "tc_deployment_completed", () )	
	def onShellCode_del(self, evt):
		print 'onTableCopyStatus'
		(out,err) = evt.data
		if err:
			self.code_panel.Shell(err)
		self.code_panel.Shell(out)
		#Publisher().sendMessage( "tc_deployment_completed", () )		
	def log(self, msg):
		#global log
		#log(msg,self.pos)
		self.config_panel.log.logList.append(msg)
		#Publisher().sendMessage( "append_log", (msg,self.pos) )
		#self.deploy_panel.Status(msg)
		
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
	def onCopyDone_del(self, evt):
		print 'onCopyDone'
		print evt.data
		(out,err, run_id, start_t, end_t) = evt.data
		dt= (end_t-start_t)
		elapsed= str(dt).rstrip('0')
		status='successfully'
		if 1: 
			if err:
				print '#'*40
				print err
				print '#'*40
				status='with errors'
				#self.Status(err)
				#self.log(err)
			#self.deploy_panel.Status(status)
			self.keepGoing = False
			self.btn_start.Enable(True)
			self.btn_trial.Enable(True)
			self.btn_stop.Enable(False)
			self.gauge.SetValue(100)
			self.timer.Stop()
			#Publisher().sendMessage( "update_transfer_log", ((self.ID,run_id),elapsed,err) )
			send( "update_transfer_log", ((self.ID,run_id),elapsed,err) )
			if 0:
				if out or out==0:
					self.deploy_panel.Status(out)
					self.deploy_panel.Status('Copy completed %s.' % status)

	def __onCopyDone(self, data, extra1, extra2=None):
		print 'onCopyDone'
		print data
		(out,err, run_id, start_t, end_t) = data
		dt= (end_t-start_t)
		elapsed= str(dt).rstrip('0')
		status='successfully'
		if 1: 
			if err:
				print '#'*40
				print err
				print '#'*40
				status='with errors'
				#self.Status(err)
				#self.log(err)
			#self.deploy_panel.Status(status)
			self.keepGoing = False
			self.btn_start.Enable(True)
			self.btn_trial.Enable(True)
			self.btn_stop.Enable(False)
			self.gauge.SetValue(100)
			self.timer.Stop()
			#Publisher().sendMessage( "update_transfer_log", ((self.ID,run_id),elapsed,err) )
			send( "update_transfer_log", ((self.ID,run_id),elapsed,err, 'Completed') )
			if 0:
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
			#self.deploy_panel.Status('Process stopped.')
			#Publisher().sendMessage( "stop_deploy_xml_process", ('Kill deployment thread') )
			send("stop_deploy_xml_process", ('Kill deployment thread'))
		
	def onTcDeploymentCompleted_del(self,e):
		print 'onTcDeploymentCompleted'
		self.btn_start.Enable(True)
		self.btn_trial.Enable(True)
		self.btn_stop.Enable(False)
		self.gauge.SetValue(100)
		self.timer.Stop()
	def __onTcDeploymentCompleted(self,data, extra1, extra2=None):
		print 'onTcDeploymentCompleted'
		self.btn_start.Enable(True)
		self.btn_trial.Enable(True)
		self.btn_stop.Enable(False)
		self.gauge.SetValue(100)
		self.timer.Stop()
		
		(out,err, run_id, start_t, end_t) = data
		dt= (end_t-start_t)
		elapsed= str(dt).rstrip('0')
		status='successfully'
		if 1: 
			if err:
				print '#'*56
				print '#'*20,'Deployment Error', '#'*20
				print err
				print '#'*20,'Deployment Error', '#'*20
				print '#'*56
				status='with errors'

			#Publisher().sendMessage( "update_transfer_log", ((self.ID,run_id),elapsed,err) )
			#send( "update_transfer_log", ((self.ID,run_id),elapsed,err) )			
			send( "update_deployment_log", ((self.ID,run_id),elapsed,err,'Completed') )		
			

	def OnTrial(self,e):
		self.table_to={}	
		if 1:
			for i in range(len(self.data)):
				row=[self.config_panel.listCtrl.GetItem(i, col).GetText() for col in range(self.config_panel.listCtrl.GetColumnCount())]
				#self.table_to[row[0]]=row
				self.table_to[row[0]]=(self.config_panel.listCtrl_t.GetItem(i, 0).GetText(),row)
		self.status='Trial'
		self.Close(True)
	def initParams1(self):		
		if 1:
			(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
			print 'init:', self.parent.drag_pos
			print 'init:', 		self.parent.drop_pos
			print 'init:', 		self.parent.dd_data
	def OnExit(self,e):
		self.Close(True)
	def OnStart(self,e):
		self.job_type='T'
		if 0:
			print self.pos_to
			#print dir(self.parent.getListFromPos(self.pos_to))
			list=self.parent.getListFromPos(self.pos_to)
			#pprint( list.data)			
			table_from=self.parent.self.getVarsToPath(self.pos_from).split('/')[6]
			print table_from
			sys.exit(1)
		self._action='S'
		self.gauge.SetValue(0)
		self.timer.Start(100)
		self.btn_start.Enable(False)
		self.btn_trial.Enable(False)
		self.btn_stop.Enable(True)
		self.run_id +=1
		self.log('started job %d' % self.run_id)
		#((local_path,remote_path, config_file),(out_dir,remote_loc, worker_file)) = self.deployXML()
		#self.btn_start.Enable(False)
		#Publisher().sendMessage( "start_query_copy", ((local_path,remote_path, config_file),(out_dir,remote_loc, worker_file)) )
		#Publisher().sendMessage( 'show_transfer_log',(1))
		if 1:
			send( 'show_transfer_log',(1))
			#Publisher().sendMessage( 'append_transfer_log', (((self.ID,self.run_id),self.source[-1],'Partition','/'.join(self.cfrom.split('/')[3:]),'/'.join(self.cto.split('/')[3:]),'n/a','Started','n/a','n/a'),))
			send('append_transfer_log', (((self.ID,self.run_id),self.title,self.source[-1],self.getSourceObjectType(),'/'.join(self.cfrom.split('/')[3:]),'/'.join(self.cto.split('/')[3:]),'n/a','Started','n/a','n/a'),))
		

		self.start_t= datetime.datetime.now()
		#self.job_type='D'
		((status, err),(self.local_path,self.remote_path, self.config_file),(self.out_dir,self.remote_loc, self.worker_file))=self.deployXML()
		if err:	
			if  1:
				end_t= datetime.datetime.now()
				#Publisher().sendMessage( "table_copy_done",  (status,err,self.run_id,start_t,end_t))
				self.send("table_copy_done",  (status,err,self.run_id,start_t,end_t))

		else:
			if  1:
				#Publisher().sendMessage( "append_log", ('Executing partition copy...',self.obj.pos,self.run_id[0]) )
				send("append_log", ('Executing %s copy...' % self.getSourceObjectType(),(0,1),self.ID) )
				
				(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
				#Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
				#Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
				#Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )				
				config_loc='%s%s' % (self.remote_path, self.config_file)
				worker_loc='%s%s' % (self.remote_loc,self.worker_file)
				#(out,err)=cu.execTaCo(config_loc,worker_loc,self.ID)
				if 1:
					#app = wx.App(0)
					
					sys._excepthook = libcb.excepthook
					try:
						#depl= dxml()
						print '-----------------------before tansfer'
						#self.job_type='T'
						result = libcb.run_function_as_process_in_dialog(
							parent=self,
							thread_function=cu.pui_execTaCo,
							title="Pipeline file",
							message="Executing data %s process..." % self.getSourceObjectType(),
							args=(config_loc,worker_loc,self.ID),
							#kwargs={'tree':self.config_panel.tree},
							callback=None
						)
						print '--------------------after transfer'
						#if (result is not None) :
						#print '>>>>>>>>>>>',result
						print result
						plog.log('Done', self.ID)
					except RuntimeError, e :
						print 'RuntimeError', str(e)
						pass
						plog.err(str(e),self.ID)
					else:
						print '--------------------else'
						print 'result', result
						#raise Exception_expected
						plog.log('Done 3',self.ID)
					wx.Yield()
					
				#pprint (out)
				#print '**************&&&&&&&&&&&&&&&',err
				#sys.exit(0)
				end_t= datetime.datetime.now()
				#Publisher().sendMessage( "table_copy_done",  (out,err,self.run_id, start_t,end_t))
				(out,err)=result
				send( "table_copy_done",  (out,err,self.run_id, self.start_t,end_t))

		send("append_log", ('%s copy done' % self.getSourceObjectType(),(0,1),self.ID))
		
		if 0:
			self.worker = ExecQcThread((self),(self.ID,self.run_id), is_trial=False)
			
			self.worker.start()
			print self.worker.isAlive()	
			
		if 1:
			self.btn_start.Enable(True)
			self.btn_trial.Enable(True)
			self.btn_stop.Enable(False)	
			self.gauge.SetValue(100)
			self.timer.Stop()
			self.log('Done')
			
			
class XmlViewerDialog(wx.Dialog):
	def __init__(
			self, parent, ID, title,run_id, size, 
			style, useMetal=False,pos=wx.DefaultPosition, 
			):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		self.parent=parent
		self.run_id=run_id
		pre = wx.PreDialog()
		pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		# This extra style can be set after the UI object has been created.
		self.splitter =MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE) # wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
		self.splitter.SetOrientation(wx.VERTICAL)		
		self.nb = fnb.FlatNotebook(self.splitter, -1, agwStyle=fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_NO_X_BUTTON)	
		#self.initParams()
		if 0:
			(self.pos_from, self.pos_to, self.data)=(self.parent.drag_pos, self.parent.drop_pos, self.parent.dd_data)
			print 'init:', self.parent.drag_pos
			print 'init:', 		self.parent.drop_pos
			print 'init:', 		self.parent.dd_data
			
		if 'wxMac' in wx.PlatformInfo and useMetal:
			self.SetExtraStyle(wx.DIALOG_EX_METAL)

		
		# Now continue with the normal construction of the dialog
		# contents
		sizer = wx.BoxSizer(wx.VERTICAL)
		#self.config_panel=TCD_Tab1(self,parent,style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, data=self.data)
		#self.nb.AddPage(self.config_panel, 'Configuration')
		self.lcode_panel=PcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		self.nb.AddPage(self.lcode_panel, 'Local')
		self.rcode_panel=PcCodePanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		self.nb.AddPage(self.rcode_panel, 'Remote')		
		#self.deploy_panel=DeployXmlLogPanel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		#self.nb.AddPage(self.deploy_panel, 'Log')		
		#sizer.Add(self.nb, 1, wx.EXPAND|wx.GROW|wx.ALL, 0)
		#line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
		#sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
		#selected_page = self.nb.GetPage(1)
		#selected_page.Enable(False)
		#print dir(selected_page)
		self.nb.EnableTab(1, False)
		
		self.log = UltTacoLogger(self.splitter,(0,1),self.parent.ID) 
		self.log.SetSize((75,300))
		self.splitter.SetMinimumPaneSize(50)
		#self.splitter.SplitHorizontally(self.tree, self.nbe)
		self.splitter.AppendWindow(self.nb,750)				
		self.splitter.AppendWindow(self.log)
		
		#sizer.Add(self.log, 0, wx.EXPAND|wx.ALL, 0)		
		sizer.Add(self.splitter, 1, wx.GROW|wx.EXPAND|wx.ALL, 0)		
		if 1:
			btnsizer = wx.BoxSizer(wx.HORIZONTAL)
			#self.btn_backgr = wx.Button(self, ID_BACKGROUND, "Background",size=(-1,20))
			#self.btn_backgr.Disable()
			#self.btn_stop = wx.Button(self, ID_STOP, "Stop", size=(50,15))

			#button2.Disable()
			#self.btn_close = wx.Button(self, ID_EXIT, "Close", size=(50,20))
			#self.btn_close.Disable()
			self.count=0
			self.gauge = wx.Gauge(self, -1, size=(25, 23),	range=100,style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
			if 1:
				i=wx.NewId()			
				self.Bind(wx.EVT_TIMER, lambda event, i=i: self.TimerHandler0(event, the_id=i), id=i)
				
				self.timer=wx.Timer(self, id=i)
								
			#self.sPanel.statusbar.Add(self.gauge[pos], 0, wx.EXPAND,0)	
			#self.gauge[pos].SetPosition((1,1))
			btnsizer.Add((1,1),0)
			btnsizer.Add(self.gauge, 1, wx.ALL|wx.ALIGN_BOTTOM)		
			#btnsizer.Add((3,3),0)
			#btnsizer.Add(self.btn_backgr, 0)
			#btnsizer.Add((10,5),0)
			#btnsizer.Add(self.btn_stop, 0)
			#btnsizer.Add((1,1),0)
			self.btn_cancel = wx.Button(self, ID_EXIT, "Close", size=(60,25))
			btnsizer.Add(self.btn_cancel, 0 , wx.RIGHT)
			#btnsizer.Add((25,5),1)
			#btnsizer.Add(self.btn_trial, 0)
			#btnsizer.Add((5,5),1, wx.EXPAND)		
			#btnsizer.Add(self.btn_close, 0 , wx.RIGHT)
			
			#self.Bind(wx.EVT_BUTTON, self.OnBackground, id=ID_BACKGROUND)
			#self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
			#self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
			
			#self.gen_bind(wx.EVT_BUTTON,self.btn_stop[pos], self.OnStopDbRequest,(pos))
			
			sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 0)
			#self.SetSizer(self.sizer)
			#self.sizer.Fit(self)
			#self.timer.Start(100)
		#btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		#self.btn_start = wx.Button(self, ID_START, "Start copy")
		#button1.SetBackgroundColour('#FFFFFF')
		#button1.Disable()
		#button2 = wx.Button(self, ID_BUTTON + 2, "Start in background")
		#button2.SetBackgroundColour('#FFFFFF')
		#button2.Disable()
		#ID_TRIAL = wx.NewId()
		#self.btn_trial = wx.Button(self, ID_TRIAL, "Deploy xml", size=(-1,-1))
		#rint dir(button3)
		#button3.SetForegroundColour('#FA5858')
		#SetTextColour(wx.RED)
		#button3.SetBackgroundColour('#FFFFFF')
		#sys.exit(1)
		#button3.Enable()
		#ID_TEST= wx.NewId()
		#self.btn_test = wx.Button(self, ID_TEST, "Test")
		
		#button4.SetForegroundColour('#585858')
		#SetTextColour(wx.RED)
		#button8.SetBackgroundColour('#FFFFFF')		
		#btnsizer.Add((3,3),0)
		#btnsizer.Add(self.btn_start, 0)
		#btnsizer.Add((10,5),0)
		#btnsizer.Add(button2, 0)
		#btnsizer.Add((35,5),0)
		#btnsizer.Add(self.btn_trial, 0)		
		#btnsizer.Add((50,5),0)
		#btnsizer.Add(button3, 0)		
		#btnsizer.Add((5,5),0,wx.EXPAND)
		#btnsizer.Add(button3, 0)
		#btnsizer.Add((5,5),1, wx.EXPAND)
		#btnsizer.Add(self.btn_test, 0 , wx.LEFT)		
		#btnsizer.Add((5,5),1, wx.EXPAND)
		#btnsizer.Add(self.btn_cancel, 0 , wx.RIGHT)
		
		#self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
		#self.Bind(wx.EVT_BUTTON, self.OnTest, id=ID_TEST)
		self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
		#self.Bind(wx.EVT_BUTTON, self.OnDeployXml, id=ID_TRIAL)
		#sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


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
		#sub(self.onTcDeploymentCompleted,'tc_deployment_completed')
		#sub(self.onCreatedConfigFile, "created_config_file")
		#sub(self.onCreatedWorkerFile, "created_worker_file")
		#sub(self.onCopyDone, "copy_done")
		#sub(self.onCopyStatus, "copy_status")
		#sub(self.onShellCode, "shell_code")
		self.loadXml()
		
		self._action=None
		self.SetSize((850,950))
	def getShellCode(self):
		out=[]
		(tc_path, config_path, client_path)=tc_loc[tc_srv][tc_home]			
		#Publisher().sendMessage( "shell_code", ('cd %s' % tc_path,0) )
		out.append('cd %s' % tc_path)
		#Publisher().sendMessage( "shell_code", ('. ./.ora_profile',0) )
		out.append('. ./.ora_profile')
		#Publisher().sendMessage( "shell_code", ('time python tc.py --pipeline_spec=%s%s --pipeline=%s%s' % (config_path, config_file, client_path, worker_file) ,0) )
		out.append('time python tc.py --pipeline_spec=%s%s --pipeline=%s' % (self.parent.confLoc[int(self.run_id)][1],self.parent.confLoc[int(self.run_id)][2], self.parent.workerLoc[int(self.run_id)][1]) )
		#Publisher().sendMessage( "copy_status", ('#%s'% '-'*40,0) )
		return '\n'.join(out)
	
	def loadXml(self):
		print self.parent.confLoc
		print self.run_id
		#print self.parent.confLoc[1]
		file_loc =self.parent.confLoc[int(self.run_id)][0]
		print file_loc
		self.log.msg('Loading spec file.')
		self.log.msg(file_loc)
		if os.path.isfile(file_loc):
			f = open(file_loc, 'r')		
			code=f.read()	
			#print code			
			self.lcode_panel.specs.SetValue(code)
			f.close()	
			
		else:
			self.log.err('Spec file does not exists.')
			#assert 1==2, 'NO FILE %s' % file_loc
		file_loc =self.parent.workerLoc[int(self.run_id)][0]
		print file_loc
		self.log.msg('Loading worker file.')
		self.log.msg(file_loc)		
		if os.path.isfile(file_loc):
			f = open(file_loc, 'r')		
			code=f.read()	
			#print code			
			self.lcode_panel.worker.SetValue(code)
			f.close()	
		else:
			self.log.err('Worker file does not exists.')
			#assert 1==2, 'NO FILE %s' % file_loc
		self.log.msg('Creating shell code.')
		self.lcode_panel.shell.SetValue(self.getShellCode())
		self.log.msg('Done')		
	def Log(self, msg):
		self.deploy_panel.Status(msg)
		

			
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

	def OnExit(self,e):
		self.Close(True)
		
class PcCodePanel(wx.Panel):
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
			