# first line below is necessary only in wxPython 2.8.11.0 since default 
# API in this wxPython is pubsub version 1 (expect later versions 
# of wxPython to use the kwargs API by default)
from wx.lib.pubsub import setupkwargs

# regular pubsub import
from wx.lib.pubsub import pub

def _sub(method,  *args, **kwargs):
	print args
	pub.subscribe(method, *args, **kwargs)

def _send(signal,  *args, **kwargs):
	print kwargs
	pub.sendMessage(signal, *args, **kwargs)
	
class SomeReceiver(object):
	def __init__(self):
		#pub.subscribe(self.__onObjectAdded, 'object.added')
		_sub(self.__onObjectAdded, 'object.added')

	def __onObjectAdded(self, data, extra1, extra2=None):
		# no longer need to access data through message.data.
		print 'Object', repr(data), 'is added'
		print extra1
		if extra2:
			print extra2


a = SomeReceiver()
#pub.sendMessage('object.added', data=42, extra1='hello!')
_send('object.added', data=42, extra1='hello!')
#pub.sendMessage('object.added', data=42, extra1='hello!', extra2=[2, 3, 5, 7, 11, 13, 17, 19, 23])
