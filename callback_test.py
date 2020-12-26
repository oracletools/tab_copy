if 0:
	from __future__ import division

	# TODO more comprehensive tests

	from __future__ import absolute_import # XXX is this necessary?
	if 1:
		#import wxversion
		import wxversion as wv
		wv.select("3.0")
	import wx

from lib_callback import *

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
	if 1:
		result = run_function_as_process_in_dialog(
			parent=None,
			thread_function=test_function_2,
			title="Test subprocess",
			message="Running test function as separate process...",
			callback=None)
		print result
	if 0:
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
			print 'result', result
			#raise Exception_expected
	wx.Yield()
	print "OK"
