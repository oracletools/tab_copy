# first line below is necessary only in wxPython 2.8.11.0 since default 
# API in this wxPython is pubsub version 1 (expect later versions 
# of wxPython to use the kwargs API by default)
from wx.lib.pubsub import setupkwargs

# regular pubsub import
from wx.lib.pubsub import pub
from threading import Thread
from tc_lib import send
class DbThread(Thread):
	"""Worker Thread Class."""
	def __init__(self,a):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		

	def run(self):
		"""Run Worker Thread."""

		#send( "db_thread_event", 1)
		#pub.sendMessage('object.added', data=42, extra1='hello!')
		pub.sendMessage('db_thread_event.added', data=42, extra1='hello!')

class SomeReceiver(object):
	def __init__(self):
		pub.subscribe(self.__onObjectAdded, 'object.added')
		pub.subscribe(self.__onDbEvent, "db_thread_event.added")
	def __onDbEvent(self, data, extra1):
		print 'onDbEvent'
	def __onObjectAdded(self, data, extra1, extra2=None):
		# no longer need to access data through message.data.
		print 'Object', repr(data), 'is added'
		print extra1
		if extra2:
			print extra2

def exect(a):
	worker = DbThread(1)
	worker.start()
	print worker.isAlive()
a = SomeReceiver()
#exec("pub.sendMessage('object.added', data=42, extra1='hello!')")
#exect(1)
#worker = DbThread(1)
#worker.start()
#print worker.isAlive()

exec("exect(1)")
if 0:
	pub.sendMessage('object.added', data=42, extra1='hello!')
	pub.sendMessage('object.added', data=42, extra1='hello!', extra2=[2, 3, 5, 7, 11, 13, 17, 19, 23])
