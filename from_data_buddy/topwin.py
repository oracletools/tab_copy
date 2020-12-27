import win32con
import win32gui
import array
import ctypes
import struct
import sys
import win32api
from ctypes import *
import time
results = []
topWindows = []
chatHwnd = 0
windowTitleText = "test_flip: Closing in 9"
#The text that the wanted window string begins with, so we can find it
windowStartText = "Welcome"


'''Handler to enumerate the window with param hwnd
Returns resultsList; the window details as an array,
with hwnd, text and class'''
def _windowEnumerationHandler(hwnd, resultList):
	resultList.append((hwnd,
					   win32gui.GetWindowText(hwnd),
					   win32gui.GetClassName(hwnd)))
'''Recursive function, checks the text of all the children of
the window with handle param hwnd until it reaches the text that
we require, returns the String of this data'''
def searchChildWindows(hwnd):
	childWindows = []
	try:
		#get child windows
		win32gui.EnumChildWindows(hwnd, _windowEnumerationHandler, childWindows)
	except win32gui.error, exception:
		# This seems to mean that the control does not or cannot have child windows
		return

	#get details of each child window
	for childHwnd, windowText, windowClass in childWindows:
		#create text buffer
		buf_size = 1 + win32gui.SendMessage(childHwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
		buffer = win32gui.PyMakeBuffer(buf_size)
		#get text from Window using hardware call. (getWindowText() did not return anything)
		win32gui.SendMessage(childHwnd, win32con.WM_GETTEXT, buf_size, buffer)
		#check to see if it's the data we want...
		if buffer[0:buf_size].find(windowStartText)>-1:
			#return the hwnd

			#global chatHwnd
			#chatHwnd = childHwnd
			return int(childHwnd)
		#else recurse, checking this window for children
		#might not be needed...
		#searchChildWindows(childHwnd)					   
if __name__ == '__main__':
	#declare global
	#global chatHwnd
	#enumerate all open windows, return topWindows
	win32gui.EnumWindows(_windowEnumerationHandler, topWindows)
	#print topWindows
	#check each window to fin the one we need
	for hwnd, windowText, windowClass in topWindows:
		#print windowText
		if windowText.find(windowTitleText)>-1:
				#search the child windows
				# save the window handle
				chatHwnd = searchChildWindows(hwnd)
				print chatHwnd
				#set the appropriate window focus (if needed)
				#win32gui.SetFocus(hwnd)
				win32gui.SetForegroundWindow(hwnd)

				initBuff = 0
				#get text
				while hwnd>0:
					linecount = win32gui.SendMessage(hwnd, win32con.EM_GETLINECOUNT, 0, 0)
					print linecount
					MAX_LENGTH = 1024

					#handle = # A handle returned from FindWindowEx, for example

					buffer = win32gui.PyMakeBuffer(MAX_LENGTH)
					length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, MAX_LENGTH, buffer)

					result = buffer[:length]
					print result
					buf_size = 1 + win32gui.SendMessage(chatHwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
					print buf_size
					buffer = win32gui.PyMakeBuffer(buf_size)
					# send a win GETTEXT request to the window and read into buffer
					win32gui.SendMessage(chatHwnd, win32con.WM_GETTEXT, buf_size, buffer)
					if buf_size-initBuff>1:
						  print buffer[initBuff:buf_size]

					initBuff = buf_size
					#after 5 seconds, get any new text
					time.sleep(5)
					# needed for Java to read the output correctly
					sys.stdout.flush()



