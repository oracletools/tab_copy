from __future__ import division

# TODO more comprehensive tests

from __future__ import absolute_import # XXX is this necessary?
if 0:
	import wxversion
	import wxversion as wv
	wv.select("3.0")
import wx
import time
from wx.lib.agw import pyprogress
#import wx
from libtbx import thread_utils
#import libtbx.thread_utils
from libtbx import runtime_utils
#from libtbx.utils import Sorry, Abort
from libtbx.utils_new import Sorry, Abort
import threading
from tc_lib import send

JOB_START_ID = wx.NewId()
LOG_UPDATE_ID = wx.NewId()
CALLBACK_ID = wx.NewId()
JOB_EXCEPTION_ID = wx.NewId()
JOB_KILLED_ID = wx.NewId()
JOB_COMPLETE_ID = wx.NewId()
JOB_PAUSE_ID = wx.NewId()
JOB_RESUME_ID = wx.NewId()
DOWNLOAD_COMPLETE_ID = wx.NewId()

class SubprocessEvent (wx.PyEvent) :
  event_id = None

  def __init__ (self, data, **kwds) :
	self.data = data
	self.__dict__.update(kwds)
	wx.PyEvent.__init__(self)
	self.SetEventType(self.event_id)

class JobStartEvent (SubprocessEvent) :
  event_id = JOB_START_ID

class LogEvent (SubprocessEvent) :
  event_id = LOG_UPDATE_ID

class JobExceptionEvent (SubprocessEvent) :
  event_id = JOB_EXCEPTION_ID

class JobKilledEvent (SubprocessEvent) :
  event_id = JOB_KILLED_ID

class JobCompleteEvent (SubprocessEvent) :
  event_id = JOB_COMPLETE_ID

class CallbackEvent (SubprocessEvent) :
  event_id = CALLBACK_ID

class JobPauseEvent (SubprocessEvent) :
  event_id = JOB_PAUSE_ID

class JobResumeEvent (SubprocessEvent) :
  event_id = JOB_RESUME_ID

class DownloadCompleteEvent (SubprocessEvent) :
  event_id = DOWNLOAD_COMPLETE_ID

def setup_stdout_logging_event (window, OnPrint) :
  window.Connect(-1, -1, LOG_UPDATE_ID, OnPrint)

def setup_process_gui_events (
	window,
	OnStart=None,
	OnPrint=None,
	OnUpdate=None,
	OnExcept=None,
	OnAbort=None,
	OnComplete=None,
	OnPause=None,
	OnResume=None) :
  if OnStart is not None :
	assert hasattr(OnStart, "__call__")
	window.Connect(-1, -1, JOB_START_ID, OnStart)
  if OnPrint is not None :
	assert hasattr(OnPrint, "__call__")
	window.Connect(-1, -1, LOG_UPDATE_ID, OnPrint)
  if OnUpdate is not None :
	assert hasattr(OnUpdate, "__call__")
	window.Connect(-1, -1, CALLBACK_ID, OnUpdate)
  if OnExcept is not None :
	assert hasattr(OnExcept, "__call__")
	window.Connect(-1, -1, JOB_EXCEPTION_ID, OnExcept)
  if OnAbort is not None :
	assert hasattr(OnAbort, "__call__")
	window.Connect(-1, -1, JOB_KILLED_ID, OnAbort)
  if OnComplete is not None :
	assert hasattr(OnComplete, "__call__")
	window.Connect(-1, -1, JOB_COMPLETE_ID, OnComplete)
  if OnPause is not None :
	assert hasattr(OnPause, "__call__")
	window.Connect(-1, -1, JOB_PAUSE_ID, OnPause)
  if OnResume is not None :
	assert hasattr(OnResume, "__call__")
	window.Connect(-1, -1, JOB_RESUME_ID, OnResume)

class event_agent (object) :
  def __init__ (self, window, **kwds) :
	self.window = window
	self._kwds = dict(kwds)
	self.__dict__.update(kwds)

  def get_kwds (self) :
	return self._kwds

  def callback_start (self, data) :
	kwds = self.get_kwds()
	event = JobStartEvent(data, **kwds)
	wx.PostEvent(self.window, event)

  def callback_stdout (self, data) :
	kwds = self.get_kwds()
	event = LogEvent(data, **kwds)
	wx.PostEvent(self.window, event)

  def callback_error (self, error, traceback_info) :
	kwds = self.get_kwds()
	event = JobExceptionEvent((error, traceback_info), **kwds)
	wx.PostEvent(self.window, event)

  def callback_abort (self) :
	kwds = self.get_kwds()
	print 'kwds', kwds
	event = JobKilledEvent(None, **kwds)
	print 'event', event
	#wx.PostEvent(self.window, event)
	send( "job_killed", kwds )

  def callback_final (self, result) :
	kwds = self.get_kwds()
	event = JobCompleteEvent(result, **kwds)
	wx.PostEvent(self.window, event)

  def callback_other (self, data) :
	kwds = self.get_kwds()
	event = CallbackEvent(data, **kwds)
	wx.PostEvent(self.window, event)

  def callback_pause (self) :
	kwds = self.get_kwds()
	event = JobPauseEvent(None, **kwds)
	wx.PostEvent(self.window, event)

  def callback_resume (self) :
	kwds = self.get_kwds()
	event = JobResumeEvent(None, **kwds)
	wx.PostEvent(self.window, event)

# simplified for when the window is really the app object
class background_event_agent (event_agent) :
  def callback_stdout (self, data) :
	pass

  def callback_other (self, data) :
	pass

class detached_process (runtime_utils.detached_process_client) :
  def __init__ (self, params, proxy) :
	runtime_utils.detached_process_client.__init__(self, params)
	self.proxy = proxy

  def callback_start (self, data) :
	self.proxy.callback_start(data)

  def callback_stdout (self, data) :
	self.proxy.callback_stdout(data)

  def callback_other (self, data) :
	self.proxy.callback_other(data)

  def callback_abort (self) :
	self.proxy.callback_abort()

  def callback_final (self, result) :
	self.proxy.callback_final(result)

  def callback_error (self, error, traceback_info) :
	self.proxy.callback_error(error, traceback_info)

  def callback_pause (self) :
	self.proxy.callback_pause()

  def callback_resume (self) :
	self.proxy.callback_resume()

  def start (self) :
	pass

# this just adds event posting callbacks to the original class
class process_with_gui_callbacks (thread_utils.process_with_callbacks) :
  def __init__ (self, proxy, target,  args=(), kwargs={},buffer_stdout=True,sleep_after_start=0) :
	thread_utils.process_with_callbacks.__init__(self,
	  target = target,
	  args=args,
	  kwargs=kwargs,
	  callback_stdout = proxy.callback_stdout,
	  callback_final  = proxy.callback_final,
	  callback_err    = proxy.callback_error,
	  callback_abort  = proxy.callback_abort,
	  callback_other  = proxy.callback_other,
	  callback_pause  = proxy.callback_pause,
	  callback_resume = proxy.callback_resume,
	  buffer_stdout   = buffer_stdout,
	  sleep_after_start=sleep_after_start,
	  )

  def set_job (self, job) :
	pass

  def purge_files (self) :
	pass

class simple_gui_process (process_with_gui_callbacks) :
  def __init__ (self, window, target, args=(), kwargs={}) :
	# XXX fix for phenix gui - is this necessary?
	proxy = event_agent(window, project_id=None, job_id=None)
	process_with_gui_callbacks.__init__(self,
	  proxy=proxy,
	  target=target,
	  args=args,
	  kwargs=kwargs,
	  buffer_stdout=True)

class ThreadProgressDialog (pyprogress.PyProgress) :
  def __init__ (self, parent, title, message) :
	pyprogress.PyProgress.__init__(self, parent, -1, title, message,
	  agwStyle=wx.PD_ELAPSED_TIME|wx.PD_APP_MODAL)
	self.SetGaugeProportion(0.15)
	self.SetGaugeSteps(50)
	self.SetGaugeBackground(wx.Colour(235, 235, 235))
	self.SetFirstGradientColour(wx.Colour(235,235,235))
	self.SetSecondGradientColour(wx.Colour(120, 200, 255))

class download_file_basic (object) :
  def __init__ (self, window, dl_func, args) :
	assert isinstance(window, wx.EvtHandler)
	assert hasattr(dl_func, "__call__")
	assert (isinstance(args, list) or isinstance(args, tuple))
	self.window = window
	window.Connect(-1, -1, DOWNLOAD_COMPLETE_ID, self.OnComplete)
	self.dl_func = dl_func
	self.args = args
	self.t = threading.Thread(target=self.run)
	self.t.start()

  def run (self) :
	try :
	  result = self.dl_func(self.args)
	except Exception, e :
	  result = (None, str(e))
	finally :
	  wx.PostEvent(self.window, DownloadCompleteEvent(result))
	return result

  def OnComplete (self, event) :
	if isinstance(event.data, str) :
	  wx.MessageBox(message="File downloaded to %s" % event.data)
	else :
	  wx.MessageBox(message="Error downloading file: %s" % event.data[1],
		caption="Download error", style=wx.ICON_ERROR)
	self.t.join()

def run_function_as_thread_in_dialog (parent, thread_function, title, message) :
  dlg = ThreadProgressDialog(None, title, message)
  t = thread_utils.simple_task_thread(thread_function, dlg)
  t.start()
  while True :
	if t.is_complete() or t.exception_raised() :
	  #dlg.Destroy()
	  dlg.Hide()
	  break
	else :
	  dlg.UpdatePulse()
	wx.MilliSleep(30)
  dlg.Destroy()
  wx.SafeYield()
  if t.exception_raised() :
	raise RuntimeError("An exception occurred while running this process: %s" %
	  t.get_error())
  return t.return_value
  
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
# TODO
class ProcessDialog (wx.Dialog) :
  def __init__ (self, parent, message, caption, panel_id=185,callback=None) :
	wx.Dialog.__init__(self,
	  parent=parent,
	  title=caption,
	  style=wx.RAISED_BORDER|wx.CAPTION)
	self.callback = callback
	self.parent=parent
	#print 'parent--',dir(parent)
	self.process = None
	self._error = None
	self._aborted = False
	self.panel_id=panel_id
	szr = wx.BoxSizer(wx.VERTICAL)
	self.SetSizer(szr)
	szr2 = wx.BoxSizer(wx.VERTICAL)
	szr.Add(szr2, 1, wx.ALL, 5)
	msg_txt = wx.StaticText(self, -1, message)
	msg_txt.Wrap(400)
	szr2.Add(msg_txt, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
	self.gauge = wx.Gauge(parent=self, size=(300,-1))
	self.gauge.SetRange(100)
	szr2.Add(self.gauge, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5)
	abort_btn = wx.Button(parent=self,
	  label="Abort")
	self.Bind(wx.EVT_BUTTON, self.OnAbort, abort_btn)
	szr2.Add(abort_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
	self.SetMinSize((300,100))
	szr.Fit(self)
	self.Centre(wx.BOTH)

  def run (self, process) :
	self.process = process
	self.process.start()
	self.gauge.Pulse()
	#time.sleep(5)
	return self.ShowModal()

  def OnAbort (self, event) :
	self.process.abort()
	self._aborted = True
	self.EndModal(wx.ID_CANCEL)

  def OnError (self, event) :
	self._error = event.data
	self.EndModal(wx.ID_CANCEL)
  def OnPrint(self,msg):
    #print 'on print'
    print msg.data
    self.send("append_log", (msg.data,(0,1),self.parent.ID) )
  def send(self, signal, data):
    wx.PostEvent(self.parent, SignalEvent(signal, data))  
  def exception_raised (self) :
	return (self._error is not None)

  def was_aborted (self) :
	return (self._aborted)

  def handle_error (self) :
	if isinstance(self._error, Exception) :
	  raise event.data
	elif isinstance(self._error, tuple) :
	  exception, traceback = self._error
	  if (isinstance(exception, Sorry)) :
		raise Sorry(str(exception))
	  raise RuntimeError("""\
Error in subprocess!
 Original error: %s
 Original traceback:
%s""" % (str(exception), traceback))
	else :
	  raise Sorry("error in child process: %s" % str(self._error))
   # finally :
   #   self.EndModal(wx.ID_CANCEL)

  def OnComplete (self, event) :
	try :
	  if (self.callback is not None) :
		self.callback(event.data)
	finally :
	  self._result = event.data
	  self.EndModal(wx.ID_OK)

  def get_result (self) :
	
	return getattr(self, "_result", None)

def run_function_as_process_in_dialog (
	parent,
	thread_function,
	title,
	message,
	args=(),
	kwargs={},
	callback=None,
	project_id=None,
	job_id=None) :
  dlg = ProcessDialog(
	parent=parent,
	message=message,
	caption=title,
	callback=callback)
  setup_process_gui_events(
	window=dlg,
	OnExcept=dlg.OnError,
	OnComplete=dlg.OnComplete,
	OnPrint=dlg.OnPrint)
  cb = event_agent(dlg, project_id=project_id, job_id=job_id)
  p = process_with_gui_callbacks(cb,
	target=thread_function, args=args,kwargs=kwargs,
	#callback_final=cb.callback_final,
	#callback_err=cb.callback_error,
	buffer_stdout=False,
	sleep_after_start=0)
  result = None
  abort = False
  
  if (dlg.run(p) == wx.ID_OK) :
	result = dlg.get_result()
  elif dlg.exception_raised() :
	dlg.handle_error()
  elif (dlg.was_aborted()) :
	abort = True
  wx.CallAfter(dlg.Destroy)
  if (abort) :
	raise Abort()
	#print 'aborted'
  return result
class Default: pass
import math
import sys


Exception_expected = RuntimeError("Exception expected.")
Exception_not_expected = RuntimeError("Exception not expected.")
def approx_equal_core(a1, a2, eps, multiplier, out, prefix):
  if isinstance(a1, str) or isinstance(a1, unicode):
	return a1 == a2
  if hasattr(a1, "__len__"): # traverse list
	if (len(a1) != len(a2)):
	  raise AssertionError(
		"approx_equal ERROR: len(a1) != len(a2): %d != %d" % (
		  len(a1), len(a2)))
	for i in xrange(len(a1)):
	  if not approx_equal_core(
				a1[i], a2[i], eps, multiplier, out, prefix+"  "):
		return False
	return True
  is_complex_1 = isinstance(a1, complex)
  is_complex_2 = isinstance(a2, complex)
  if (is_complex_1 and is_complex_2): # complex & complex
	if not approx_equal_core(
			  a1.real, a2.real, eps, multiplier, out, prefix+"real "):
	  return False
	if not approx_equal_core(
			  a1.imag, a2.imag, eps, multiplier, out, prefix+"imag "):
	  return False
	return True
  elif (is_complex_1): # complex & number
	if not approx_equal_core(
			  a1.real, a2, eps, multiplier, out, prefix+"real "):
	  return False
	if not approx_equal_core(
			  a1.imag, 0, eps, multiplier, out, prefix+"imag "):
	  return False
	return True
  elif (is_complex_2): # number & complex
	if not approx_equal_core(
			  a1, a2.real, eps, multiplier, out, prefix+"real "):
	  return False
	if not approx_equal_core(
			  0, a2.imag, eps, multiplier, out, prefix+"imag "):
	  return False
	return True
  ok = True
  d = a1 - a2
  if (abs(d) > eps):
	if (multiplier is None):
	  ok = False
	else:
	  am = max(a1,a2) * multiplier
	  d = (am - d) - am
	  if (d != 0):
		ok = False
  if (out is not None):
	annotation = ""
	if (not ok):
	  annotation = " approx_equal ERROR"
	print >> out, prefix + str(a1) + annotation
	print >> out, prefix + str(a2) + annotation
	print >> out, prefix.rstrip()
	return True
  return ok
def test_function_1 (*args, **kwds) :
	print args
	(a,b,c)=args
	print a, b 
	print 'test_function_1'
	n = 0
	for i in range(25000) :
		x = math.sqrt(i)
		#print x
		n += x
	return n
def test_function_2 (*args, **kwds) :
	print 'test_function_2'
	n = 0
	for i in range(100000) :
		x = math.sqrt(i)
		n += x
	return n
def test_function_3 (*args, **kwds) :
	raise RuntimeError("This is a test!")	
	
def approx_equal(a1, a2, eps=1.e-6, multiplier=1.e10, out=Default, prefix=""):
	ok = approx_equal_core(a1, a2, eps, multiplier, None, prefix)
	if (not ok and out is not None):
		if (out is Default): out = sys.stdout
		print >> out, prefix + "approx_equal eps:", eps
		print >> out, prefix + "approx_equal multiplier:", multiplier
		assert approx_equal_core(a1, a2, eps, multiplier, out, prefix)
	return ok	
def excepthook (*args, **kwds) :
	pass
def Callback_Print(data):
	print data
	print 'Callback_Print'
if (__name__ == "__main__") :
	#from libtbx.test_utils import approx_equal, Exception_expected





	sys._excepthook = excepthook
	app = wx.App(0)
	result = run_function_as_process_in_dialog(
	parent=None,
	thread_function=test_function_1,
	title="Test subprocess",
	message="Running test function as separate process...",
	callback=None)
	if (result is not None) :
		print '>>>>>>>>>>>',result
		assert approx_equal(result, 2635152.11, eps=0.0001)
	#result2 = run_function_as_thread_in_dialog(
	#  parent=None,
	#  thread_function=test_function_2,
	#  title="Test subprocess",
	#  message="Running test function in Python thread...")
	#assert approx_equal(result2, 21081692.7462, eps=0.0001)
	try :
		result = run_function_as_process_in_dialog(
			parent=None,
			thread_function=test_function_2,
			title="Test subprocess",
			message="Running test function as separate process...",
			callback=Callback_Print)
	except RuntimeError, e :
		print 'RuntimeError', str(e)
		pass
	else :
		print result
		#raise Exception_expected
	wx.Yield()
	print "OK"
