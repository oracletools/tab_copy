#!/bin/env python
#----------------------------------------------------------------------------
# Name:         Main.py
# Purpose:      Testing lots of stuff, controls, window types, etc.
#
# Author:       Robin Dunn
#
# Created:      A long time ago, in a galaxy far, far away...
# RCS-ID:       $Id: Main.py 67536 2011-04-18 21:00:07Z RD $
# Copyright:    (c) 1999 by Total Control Software
# Licence:      wxWindows license
#----------------------------------------------------------------------------

# FIXME List:
# * Problems with flickering related to ERASE_BACKGROUND
#     and the splitters. Might be a problem with this 2.5 beta...?
#     UPDATE: can't see on 2.5.2 GTK - maybe just a faster machine :)
# * Demo Code menu?
# * Annoying switching between tabs and resulting flicker
#     how to replace a page in the notebook without deleting/adding?
#     Where is SetPage!? tried freeze...tried reparent of dummy panel....
#     AG: It looks like this issue is fixed by Freeze()ing and Thaw()ing the
#         main frame and not the notebook

# TODO List:
# * UI design more professional (is the new version more professional?)
# * save file positions (new field in demoModules) (@ LoadDemoSource)
# * Update main overview

# * Why don't we move _treeList into a separate module

# =====================
# = EXTERNAL Packages =
# =====================
# In order to let a package (like AGW) be included in the wxPython demo,
# the package owner should create a sub-directory of the wxPython demo folder
# in which all the package's demos should live. In addition, the sub-folder
# should contain a Python file called __demo__.py which, when imported, should
# contain the following methods:
#
# * GetDemoBitmap: returns the bitmap to be used in the wxPython demo tree control
#   in a PyEmbeddedImage format;
# * GetRecentAdditions: returns a list of demos which will be displayed under the
#   "Recent Additions/Updates" tree item. This list should be a subset (or the full
#   set) of the package's demos;
# * GetDemos: returns a tuple. The first item of the tuple is the package's name
#   as will be displayed in the wxPython demo tree, right after the "Custom Controls"
#   item. The second element of the tuple is the list of demos for the external package.
# * GetOverview: returns a wx.html-ready representation of the package's documentation.
#
# Please see the __demo__.py file in the demo/agw/ folder for an example.
# Last updated: Andrea Gavana, 20 Oct 2008, 18.00 GMT

import sys, os, time, traceback, types

import wx              
import wx.aui
import wx.html

import version

# We won't import the images module yet, but we'll assign it to this
# global when we do.
images = None

# For debugging
##wx.Trap();
##print "wx.VERSION_STRING = %s (%s)" % (wx.VERSION_STRING, wx.USE_UNICODE and 'unicode' or 'ansi')
##print "pid:", os.getpid()
##raw_input("Press Enter...")


#---------------------------------------------------------------------------

USE_CUSTOMTREECTRL = False
ALLOW_AUI_FLOATING = False
DEFAULT_PERSPECTIVE = "Default Perspective"

#---------------------------------------------------------------------------

_demoPngs = ["overview", "recent", "frame", "dialog", "moredialog", "core",
			 "book", "customcontrol", "morecontrols", "layout", "process", "clipboard",
			 "images", "miscellaneous"]

_treeList = [
	# new stuff
	('Recent Additions/Updates', [
		'RichTextCtrl',
		'Treebook',
		'Toolbook',
		'BitmapFromBuffer',
		'RawBitmapAccess',
		'DragScroller',
		'DelayedResult',
		'ExpandoTextCtrl',
		'AboutBox',
		'AlphaDrawing',
		'GraphicsContext',
		'CollapsiblePane',
		'ComboCtrl',
		'OwnerDrawnComboBox',
		'BitmapComboBox',
		'I18N',
		'Img2PyArtProvider',
		'SearchCtrl',
		'SizedControls',
		'AUI_MDI',
		'TreeMixin',
		'AdjustChannels',
		'RendererNative',
		'PlateButton',
		'ResizeWidget',
		'Cairo',
		'Cairo_Snippets',
		'SystemSettings',
		'GridLabelRenderer',
		'ItemsPicker',
		]),

	# managed windows == things with a (optional) caption you can close
	('Frames and Dialogs', [
		'AUI_DockingWindowMgr',
		'AUI_MDI',
		'Dialog',
		'Frame',
		'MDIWindows',
		'MiniFrame',
		'Wizard',
		]),

	# the common dialogs
	('Common Dialogs', [
		'AboutBox',
		'ColourDialog',
		'DirDialog',
		'FileDialog',
		'FindReplaceDialog',
		'FontDialog',
		'MessageDialog',
		'MultiChoiceDialog',
		'PageSetupDialog',
		'PrintDialog',
		'ProgressDialog',
		'SingleChoiceDialog',
		'TextEntryDialog',
		]),

	# dialogs from libraries
	('More Dialogs', [
		'ImageBrowser',
		'ScrolledMessageDialog',
		]),

	# core controls
	('Core Windows/Controls', [
		'BitmapButton',
		'Button',
		'CheckBox',
		'CheckListBox',
		'Choice',
		'ComboBox',
		'Gauge',
		'Grid',
		'Grid_MegaExample',
		'GridLabelRenderer',
		'ListBox',
		'ListCtrl',
		'ListCtrl_virtual',
		'ListCtrl_edit',
		'Menu',
		'PopupMenu',
		'PopupWindow',
		'RadioBox',
		'RadioButton',
		'SashWindow',
		'ScrolledWindow',
		'SearchCtrl',        
		'Slider',
		'SpinButton',
		'SpinCtrl',
		'SplitterWindow',
		'StaticBitmap',
		'StaticBox',
		'StaticText',
		'StatusBar',
		'StockButtons',
		'TextCtrl',
		'ToggleButton',
		'ToolBar',
		'TreeCtrl',
		'Validator',
		]),
	
	('"Book" Controls', [
		'AUI_Notebook',
		'Choicebook',
		'FlatNotebook',
		'Listbook',
		'Notebook',
		'Toolbook',
		'Treebook',
		]),

	('Custom Controls', [
		'AnalogClock',
		'ColourSelect',
		'ComboTreeBox',
		'Editor',
		'GenericButtons',
		'GenericDirCtrl',
		'ItemsPicker',
		'LEDNumberCtrl',
		'MultiSash',
		'PlateButton',
		'PopupControl',
		'PyColourChooser',
		'TreeListCtrl',
	]),
	
	# controls coming from other libraries
	('More Windows/Controls', [
		'ActiveX_FlashWindow',
		'ActiveX_IEHtmlWindow',
		'ActiveX_PDFWindow',
		'BitmapComboBox',
		'Calendar',
		'CalendarCtrl',
		'CheckListCtrlMixin',
		'CollapsiblePane',
		'ComboCtrl',
		'ContextHelp',
		'DatePickerCtrl',
		'DynamicSashWindow',
		'EditableListBox',
		'ExpandoTextCtrl',
		'FancyText',
		'FileBrowseButton',
		'FloatBar',  
		'FloatCanvas',
		'HtmlWindow',
		'IntCtrl',
		'MVCTree',   
		'MaskedEditControls',
		'MaskedNumCtrl',
		'MediaCtrl',
		'MultiSplitterWindow',
		'OwnerDrawnComboBox',
		'Pickers',
		'PyCrust',
		'PyPlot',
		'PyShell',
		'ResizeWidget',
		'RichTextCtrl',
		'ScrolledPanel',
		'SplitTree',
		'StyledTextCtrl_1',
		'StyledTextCtrl_2',
		'TablePrint',
		'Throbber',
		'Ticker',
		'TimeCtrl',
		'TreeMixin',
		'VListBox',
		]),

	# How to lay out the controls in a frame/dialog
	('Window Layout', [
		'GridBagSizer',
		'LayoutAnchors',
		'LayoutConstraints',
		'Layoutf',
		'RowColSizer',
		'ScrolledPanel',
		'SizedControls',
		'Sizers',
		'XmlResource',
		'XmlResourceHandler',
		'XmlResourceSubclass',
		]),

	# ditto
	('Process and Events', [
		'DelayedResult',
		'EventManager',
		'KeyEvents',
		'Process',
		'PythonEvents',
		'Threads',
		'Timer',
		##'infoframe',    # needs better explanation and some fixing
		]),

	# Clipboard and DnD
	('Clipboard and DnD', [
		'CustomDragAndDrop',
		'DragAndDrop',
		'URLDragAndDrop',
		]),

	# Images
	('Using Images', [
		'AdjustChannels',
		'AlphaDrawing',
		'AnimateCtrl',
		'ArtProvider',
		'BitmapFromBuffer',
		'Cursor',
		'DragImage',
		'Image',
		'ImageAlpha',
		'ImageFromStream',
		'Img2PyArtProvider',
		'Mask',
		'RawBitmapAccess',
		'Throbber',
		]),

	# Other stuff
	('Miscellaneous', [
		'AlphaDrawing',
		'Cairo',
		'Cairo_Snippets',
		'ColourDB',
		##'DialogUnits',   # needs more explanations
		'DragScroller',
		'DrawXXXList',
		'FileHistory',
		'FontEnumerator',
		'GraphicsContext',
		'GLCanvas',
		'I18N',        
		'Joystick',
		'MimeTypesManager',
		'MouseGestures',
		'OGL',
		'PrintFramework',
		'PseudoDC',
		'RendererNative',
		'ShapedWindow',
		'Sound',
		'StandardPaths',
		'SystemSettings',
		'Unicode',
		]),


	('Check out the samples dir too', [
		]),

]



#---------------------------------------------------------------------------
# Show how to derive a custom wxLog class

class MyLog(wx.PyLog):
	def __init__(self, textCtrl, logTime=0):
		wx.PyLog.__init__(self)
		self.tc = textCtrl
		self.logTime = logTime

	def DoLogString(self, message, timeStamp):
		#print message, timeStamp
		#if self.logTime:
		#    message = time.strftime("%X", time.localtime(timeStamp)) + \
		#              ": " + message
		if self.tc:
			self.tc.AppendText(message + '\n')


class MyTP(wx.PyTipProvider):
	def GetTip(self):
		return "This is my tip"

#---------------------------------------------------------------------------
# A class to be used to simply display a message in the demo pane
# rather than running the sample itself.

class MessagePanel(wx.Panel):
	def __init__(self, parent, message, caption='', flags=0):
		wx.Panel.__init__(self, parent)

		# Make widgets
		if flags:
			artid = None
			if flags & wx.ICON_EXCLAMATION:
				artid = wx.ART_WARNING            
			elif flags & wx.ICON_ERROR:
				artid = wx.ART_ERROR
			elif flags & wx.ICON_QUESTION:
				artid = wx.ART_QUESTION
			elif flags & wx.ICON_INFORMATION:
				artid = wx.ART_INFORMATION

			if artid is not None:
				bmp = wx.ArtProvider.GetBitmap(artid, wx.ART_MESSAGE_BOX, (32,32))
				icon = wx.StaticBitmap(self, -1, bmp)
			else:
				icon = (32,32) # make a spacer instead

		if caption:
			caption = wx.StaticText(self, -1, caption)
			caption.SetFont(wx.Font(28, wx.SWISS, wx.NORMAL, wx.BOLD))

		message = wx.StaticText(self, -1, message)

		# add to sizers for layout
		tbox = wx.BoxSizer(wx.VERTICAL)
		if caption:
			tbox.Add(caption)
			tbox.Add((10,10))
		tbox.Add(message)
		
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add((10,10), 1)
		hbox.Add(icon)
		hbox.Add((10,10))
		hbox.Add(tbox)
		hbox.Add((10,10), 1)

		box = wx.BoxSizer(wx.VERTICAL)
		box.Add((10,10), 1)
		box.Add(hbox, 0, wx.EXPAND)
		box.Add((10,10), 2)

		self.SetSizer(box)
		self.Fit()
		

#---------------------------------------------------------------------------
# A class to be used to display source code in the demo.  Try using the
# wxSTC in the StyledTextCtrl_2 sample first, fall back to wxTextCtrl
# if there is an error, such as the stc module not being present.
#

try:
	##raise ImportError     # for testing the alternate implementation
	from wx import stc
	from StyledTextCtrl_2 import PythonSTC

	class DemoCodeEditor(PythonSTC):
		def __init__(self, parent, style=wx.BORDER_NONE):
			PythonSTC.__init__(self, parent, -1, style=style)
			self.SetUpEditor()

		# Some methods to make it compatible with how the wxTextCtrl is used
		def SetValue(self, value):
			if wx.USE_UNICODE:
				value = value.decode('iso8859_1')
			val = self.GetReadOnly()
			self.SetReadOnly(False)
			self.SetText(value)
			self.EmptyUndoBuffer()
			self.SetSavePoint()
			self.SetReadOnly(val)

		def SetEditable(self, val):
			self.SetReadOnly(not val)

		def IsModified(self):
			return self.GetModify()

		def Clear(self):
			self.ClearAll()

		def SetInsertionPoint(self, pos):
			self.SetCurrentPos(pos)
			self.SetAnchor(pos)

		def ShowPosition(self, pos):
			line = self.LineFromPosition(pos)
			#self.EnsureVisible(line)
			self.GotoLine(line)

		def GetLastPosition(self):
			return self.GetLength()

		def GetPositionFromLine(self, line):
			return self.PositionFromLine(line)

		def GetRange(self, start, end):
			return self.GetTextRange(start, end)

		def GetSelection(self):
			return self.GetAnchor(), self.GetCurrentPos()

		def SetSelection(self, start, end):
			self.SetSelectionStart(start)
			self.SetSelectionEnd(end)

		def SelectLine(self, line):
			start = self.PositionFromLine(line)
			end = self.GetLineEndPosition(line)
			self.SetSelection(start, end)
			
		def SetUpEditor(self):
			"""
			This method carries out the work of setting up the demo editor.            
			It's seperate so as not to clutter up the init code.
			"""
			import keyword
			
			self.SetLexer(stc.STC_LEX_PYTHON)
			self.SetKeyWords(0, " ".join(keyword.kwlist))
	
			# Enable folding
			self.SetProperty("fold", "1" ) 

			# Highlight tab/space mixing (shouldn't be any)
			self.SetProperty("tab.timmy.whinge.level", "1")

			# Set left and right margins
			self.SetMargins(2,2)
	
			# Set up the numbers in the margin for margin #1
			self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
			# Reasonable value for, say, 4-5 digits using a mono font (40 pix)
			self.SetMarginWidth(1, 40)
	
			# Indentation and tab stuff
			self.SetIndent(4)               # Proscribed indent size for wx
			self.SetIndentationGuides(True) # Show indent guides
			self.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
			self.SetTabIndents(True)        # Tab key indents
			self.SetTabWidth(4)             # Proscribed tab size for wx
			self.SetUseTabs(False)          # Use spaces rather than tabs, or
											# TabTimmy will complain!    
			# White space
			self.SetViewWhiteSpace(False)   # Don't view white space
	
			# EOL: Since we are loading/saving ourselves, and the
			# strings will always have \n's in them, set the STC to
			# edit them that way.            
			self.SetEOLMode(wx.stc.STC_EOL_LF)
			self.SetViewEOL(False)
			
			# No right-edge mode indicator
			self.SetEdgeMode(stc.STC_EDGE_NONE)
	
			# Setup a margin to hold fold markers
			self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
			self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
			self.SetMarginSensitive(2, True)
			self.SetMarginWidth(2, 12)
	
			# and now set up the fold markers
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,    "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS, "white", "black")
	
			# Global default style
			if wx.Platform == '__WXMSW__':
				self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
								  'fore:#000000,back:#FFFFFF,face:Courier New')
			elif wx.Platform == '__WXMAC__':
				# TODO: if this looks fine on Linux too, remove the Mac-specific case 
				# and use this whenever OS != MSW.
				self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
								  'fore:#000000,back:#FFFFFF,face:Monaco')
			else:
				defsize = wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT).GetPointSize()
				self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
								  'fore:#000000,back:#FFFFFF,face:Courier,size:%d'%defsize)
	
			# Clear styles and revert to default.
			self.StyleClearAll()

			# Following style specs only indicate differences from default.
			# The rest remains unchanged.

			# Line numbers in margin
			self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,'fore:#000000,back:#99A9C2')    
			# Highlighted brace
			self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,'fore:#00009D,back:#FFFF00')
			# Unmatched brace
			self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,'fore:#00009D,back:#FF0000')
			# Indentation guide
			self.StyleSetSpec(wx.stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")
	
			# Python styles
			self.StyleSetSpec(wx.stc.STC_P_DEFAULT, 'fore:#000000')
			# Comments
			self.StyleSetSpec(wx.stc.STC_P_COMMENTLINE,  'fore:#008000,back:#F0FFF0')
			self.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, 'fore:#008000,back:#F0FFF0')
			# Numbers
			self.StyleSetSpec(wx.stc.STC_P_NUMBER, 'fore:#008080')
			# Strings and characters
			self.StyleSetSpec(wx.stc.STC_P_STRING, 'fore:#800080')
			self.StyleSetSpec(wx.stc.STC_P_CHARACTER, 'fore:#800080')
			# Keywords
			self.StyleSetSpec(wx.stc.STC_P_WORD, 'fore:#000080,bold')
			# Triple quotes
			self.StyleSetSpec(wx.stc.STC_P_TRIPLE, 'fore:#800080,back:#FFFFEA')
			self.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, 'fore:#800080,back:#FFFFEA')
			# Class names
			self.StyleSetSpec(wx.stc.STC_P_CLASSNAME, 'fore:#0000FF,bold')
			# Function names
			self.StyleSetSpec(wx.stc.STC_P_DEFNAME, 'fore:#008080,bold')
			# Operators
			self.StyleSetSpec(wx.stc.STC_P_OPERATOR, 'fore:#800000,bold')
			# Identifiers. I leave this as not bold because everything seems
			# to be an identifier if it doesn't match the above criterae
			self.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, 'fore:#000000')

			# Caret color
			self.SetCaretForeground("BLUE")
			# Selection background
			self.SetSelBackground(1, '#66CCFF')

			self.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
			self.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

		def RegisterModifiedEvent(self, eventHandler):
			self.Bind(wx.stc.EVT_STC_CHANGE, eventHandler)


except ImportError:
	class DemoCodeEditor(wx.TextCtrl):
		def __init__(self, parent):
			wx.TextCtrl.__init__(self, parent, -1, style =
								 wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH2 | wx.TE_NOHIDESEL)

		def RegisterModifiedEvent(self, eventHandler):
			self.Bind(wx.EVT_TEXT, eventHandler)

		def SetReadOnly(self, flag):
			self.SetEditable(not flag)
			# NOTE: STC already has this method
	
		def GetText(self):
			return self.GetValue()

		def GetPositionFromLine(self, line):
			return self.XYToPosition(0,line)

		def GotoLine(self, line):
			pos = self.GetPositionFromLine(line)
			self.SetInsertionPoint(pos)
			self.ShowPosition(pos)

		def SelectLine(self, line):
			start = self.GetPositionFromLine(line)
			end = start + self.GetLineLength(line)
			self.SetSelection(start, end)


#---------------------------------------------------------------------------
# Constants for module versions

modOriginal = 0
modModified = 1
modDefault = modOriginal

#---------------------------------------------------------------------------

class DemoCodePanel(wx.Panel):
	"""Panel for the 'Demo Code' tab"""
	def __init__(self, parent, mainFrame):
		wx.Panel.__init__(self, parent, size=(1,1))
		if 'wxMSW' in wx.PlatformInfo:
			self.Hide()
		self.mainFrame = mainFrame
		self.editor = DemoCodeEditor(self)
		self.editor.RegisterModifiedEvent(self.OnCodeModified)

		self.btnSave = wx.Button(self, -1, "Save Changes")
		self.btnRestore = wx.Button(self, -1, "Delete Modified")
		self.btnSave.Enable(False)
		self.btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
		self.btnRestore.Bind(wx.EVT_BUTTON, self.OnRestore)

		self.radioButtons = { modOriginal: wx.RadioButton(self, -1, "Original", style = wx.RB_GROUP),
							  modModified: wx.RadioButton(self, -1, "Modified") }

		self.controlBox = wx.BoxSizer(wx.HORIZONTAL)
		self.controlBox.Add(wx.StaticText(self, -1, "Active Version:"), 0,
							wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
		for modID, radioButton in self.radioButtons.items():
			self.controlBox.Add(radioButton, 0, wx.EXPAND | wx.RIGHT, 5)
			radioButton.modID = modID # makes it easier for the event handler
			radioButton.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
			
		self.controlBox.Add(self.btnSave, 0, wx.RIGHT, 5)
		self.controlBox.Add(self.btnRestore, 0)

		self.box = wx.BoxSizer(wx.VERTICAL)
		self.box.Add(self.controlBox, 0, wx.EXPAND)
		self.box.Add(wx.StaticLine(self), 0, wx.EXPAND)
		self.box.Add(self.editor, 1, wx.EXPAND)
		
		self.box.Fit(self)
		self.SetSizer(self.box)


	# Loads a demo from a DemoModules object
	def LoadDemo(self, demoModules):
		self.demoModules = demoModules
		if (modDefault == modModified) and demoModules.Exists(modModified):
			demoModules.SetActive(modModified)
		else:
			demoModules.SetActive(modOriginal)
		self.radioButtons[demoModules.GetActiveID()].Enable(True)
		self.ActiveModuleChanged()


	def ActiveModuleChanged(self):
		self.LoadDemoSource(self.demoModules.GetSource())
		self.UpdateControlState()
		self.mainFrame.pnl.Freeze()        
		self.ReloadDemo()
		self.mainFrame.pnl.Thaw()

		
	def LoadDemoSource(self, source):
		self.editor.Clear()
		self.editor.SetValue(source)
		self.JumpToLine(0)
		self.btnSave.Enable(False)


	def JumpToLine(self, line, highlight=False):
		self.editor.GotoLine(line)
		self.editor.SetFocus()
		if highlight:
			self.editor.SelectLine(line)
		
	   
	def UpdateControlState(self):
		active = self.demoModules.GetActiveID()
		# Update the radio/restore buttons
		for moduleID in self.radioButtons:
			btn = self.radioButtons[moduleID]
			if moduleID == active:
				btn.SetValue(True)
			else:
				btn.SetValue(False)

			if self.demoModules.Exists(moduleID):
				btn.Enable(True)
				if moduleID == modModified:
					self.btnRestore.Enable(True)
			else:
				btn.Enable(False)
				if moduleID == modModified:
					self.btnRestore.Enable(False)

					
	def OnRadioButton(self, event):
		radioSelected = event.GetEventObject()
		modSelected = radioSelected.modID
		if modSelected != self.demoModules.GetActiveID():
			busy = wx.BusyInfo("Reloading demo module...")
			self.demoModules.SetActive(modSelected)
			self.ActiveModuleChanged()


	def ReloadDemo(self):
		if self.demoModules.name != __name__:
			self.mainFrame.RunModule()

				
	def OnCodeModified(self, event):
		self.btnSave.Enable(self.editor.IsModified())

		
	def OnSave(self, event):
		if self.demoModules.Exists(modModified):
			if self.demoModules.GetActiveID() == modOriginal:
				overwriteMsg = "You are about to overwrite an already existing modified copy\n" + \
							   "Do you want to continue?"
				dlg = wx.MessageDialog(self, overwriteMsg, "wxPython Demo",
									   wx.YES_NO | wx.NO_DEFAULT| wx.ICON_EXCLAMATION)
				result = dlg.ShowModal()
				if result == wx.ID_NO:
					return
				dlg.Destroy()
			
		self.demoModules.SetActive(modModified)
		modifiedFilename = GetModifiedFilename(self.demoModules.name)

		# Create the demo directory if one doesn't already exist
		if not os.path.exists(GetModifiedDirectory()):
			try:
				os.makedirs(GetModifiedDirectory())
				if not os.path.exists(GetModifiedDirectory()):
					wx.LogMessage("BUG: Created demo directory but it still doesn't exist")
					raise AssertionError
			except:
				wx.LogMessage("Error creating demo directory: %s" % GetModifiedDirectory())
				return
			else:
				wx.LogMessage("Created directory for modified demos: %s" % GetModifiedDirectory())
			
		# Save
		f = open(modifiedFilename, "wt")
		source = self.editor.GetText()
		try:
			f.write(source)
		finally:
			f.close()
			
		busy = wx.BusyInfo("Reloading demo module...")
		self.demoModules.LoadFromFile(modModified, modifiedFilename)
		self.ActiveModuleChanged()

		self.mainFrame.SetTreeModified(True)


	def OnRestore(self, event): # Handles the "Delete Modified" button
		modifiedFilename = GetModifiedFilename(self.demoModules.name)
		self.demoModules.Delete(modModified)
		os.unlink(modifiedFilename) # Delete the modified copy
		busy = wx.BusyInfo("Reloading demo module...")
		
		self.ActiveModuleChanged()

		self.mainFrame.SetTreeModified(False)


#---------------------------------------------------------------------------

def opj(path):
	"""Convert paths to the platform-specific separator"""
	st = apply(os.path.join, tuple(path.split('/')))
	# HACK: on Linux, a leading / gets lost...
	if path.startswith('/'):
		st = '/' + st
	return st


def GetDataDir():
	"""
	Return the standard location on this platform for application data
	"""
	sp = wx.StandardPaths.Get()
	return sp.GetUserDataDir()


def GetModifiedDirectory():
	"""
	Returns the directory where modified versions of the demo files
	are stored
	"""
	return os.path.join(GetDataDir(), "modified")


def GetModifiedFilename(name):
	"""
	Returns the filename of the modified version of the specified demo
	"""
	if not name.endswith(".py"):
		name = name + ".py"
	return os.path.join(GetModifiedDirectory(), name)


def GetOriginalFilename(name):
	"""
	Returns the filename of the original version of the specified demo
	"""
	if not name.endswith(".py"):
		name = name + ".py"

	if os.path.isfile(name):
		return name
	
	originalDir = os.getcwd()
	listDir = os.listdir(originalDir)
	# Loop over the content of the demo directory
	for item in listDir:
		if not os.path.isdir(item):
			# Not a directory, continue
			continue
		dirFile = os.listdir(item)
		# See if a file called "name" is there
		if name in dirFile:        
			return os.path.join(item, name)

	# We must return a string...
	return ""


def DoesModifiedExist(name):
	"""Returns whether the specified demo has a modified copy"""
	if os.path.exists(GetModifiedFilename(name)):
		return True
	else:
		return False


def GetConfig():
	if not os.path.exists(GetDataDir()):
		os.makedirs(GetDataDir())

	config = wx.FileConfig(
		localFilename=os.path.join(GetDataDir(), "options"))
	return config


def SearchDemo(name, keyword):
	""" Returns whether a demo contains the search keyword or not. """
	fid = open(GetOriginalFilename(name), "rt")
	fullText = fid.read()
	fid.close()
	if type(keyword) is unicode:
		fullText = fullText.decode('iso8859-1')
	if fullText.find(keyword) >= 0:
		return True

	return False    


def HuntExternalDemos():
	"""
	Searches for external demos (i.e. packages like AGW) in the wxPython
	demo sub-directories. In order to be found, these external packages
	must have a __demo__.py file in their directory.
	"""

	externalDemos = {}
	originalDir = os.getcwd()
	listDir = os.listdir(originalDir)
	# Loop over the content of the demo directory
	for item in listDir:
		if not os.path.isdir(item):
			# Not a directory, continue
			continue
		dirFile = os.listdir(item)
		# See if a __demo__.py file is there
		if "__demo__.py" in dirFile:
			# Extend sys.path and import the external demos
			sys.path.append(item)
			externalDemos[item] = __import__("__demo__")

	if not externalDemos:
		# Nothing to import...
		return {}

	# Modify the tree items and icons
	index = 0
	for category, demos in _treeList:
		# We put the external packages right before the
		# More Windows/Controls item
		if category == "More Windows/Controls":
			break
		index += 1

	# Sort and reverse the external demos keys so that they
	# come back in alphabetical order
	keys = externalDemos.keys()
	keys.sort()
	keys.reverse()

	# Loop over all external packages
	for extern in keys:
		package = externalDemos[extern]
		# Insert a new package in the _treeList of demos
		_treeList.insert(index, package.GetDemos())
		# Get the recent additions for this package
		_treeList[0][1].extend(package.GetRecentAdditions())
		# Extend the demo bitmaps and the catalog
		_demoPngs.insert(index+1, extern)
		images.catalog[extern] = package.GetDemoBitmap()

	# That's all folks...
	return externalDemos


def LookForExternals(externalDemos, demoName):
	"""
	Checks if a demo name is in any of the external packages (like AGW) or
	if the user clicked on one of the external packages parent items in the
	tree, in which case it returns the html overview for the package.
	"""

	pkg = overview = None
	# Loop over all the external demos
	for key, package in externalDemos.items():
		# Get the tree item name for the package and its demos
		treeName, treeDemos = package.GetDemos()
		# Get the overview for the package
		treeOverview = package.GetOverview()
		if treeName == demoName:
			# The user clicked on the parent tree item, return the overview
			return pkg, treeOverview
		elif demoName in treeDemos:
			# The user clicked on a real demo, return the package
			return key, overview

	# No match found, return None for both
	return pkg, overview
	
#---------------------------------------------------------------------------

class ModuleDictWrapper:
	"""Emulates a module with a dynamically compiled __dict__"""
	def __init__(self, dict):
		self.dict = dict
		
	def __getattr__(self, name):
		if name in self.dict:
			return self.dict[name]
		else:
			raise AttributeError

class DemoModules:
	"""
	Dynamically manages the original/modified versions of a demo
	module
	"""
	def __init__(self, name):
		self.modActive = -1
		self.name = name
		
		#              (dict , source ,  filename , description   , error information )        
		#              (  0  ,   1    ,     2     ,      3        ,          4        )        
		self.modules = [[dict(),  ""    ,    ""     , "<original>"  ,        None],
						[dict(),  ""    ,    ""     , "<modified>"  ,        None]]
		
		for i in [modOriginal, modModified]:
			self.modules[i][0]['__file__'] = \
				os.path.join(os.getcwdu(), GetOriginalFilename(name))
			
		# load original module
		self.LoadFromFile(modOriginal, GetOriginalFilename(name))
		self.SetActive(modOriginal)

		# load modified module (if one exists)
		if DoesModifiedExist(name):
			self.LoadFromFile(modModified, GetModifiedFilename(name))


	def LoadFromFile(self, modID, filename):
		self.modules[modID][2] = filename
		file = open(filename, "rt")
		self.LoadFromSource(modID, file.read())
		file.close()


	def LoadFromSource(self, modID, source):
		self.modules[modID][1] = source
		self.LoadDict(modID)


	def LoadDict(self, modID):
		if self.name != __name__:
			source = self.modules[modID][1]
			description = self.modules[modID][2]
			description = description.encode(sys.getfilesystemencoding())
			
			try:
				code = compile(source, description, "exec")        
				exec code in self.modules[modID][0]
			except:
				self.modules[modID][4] = DemoError(sys.exc_info())
				self.modules[modID][0] = None
			else:
				self.modules[modID][4] = None


	def SetActive(self, modID):
		if modID != modOriginal and modID != modModified:
			raise LookupError
		else:
			self.modActive = modID


	def GetActive(self):
		dict = self.modules[self.modActive][0]
		if dict is None:
			return None
		else:
			return ModuleDictWrapper(dict)


	def GetActiveID(self):
		return self.modActive

	
	def GetSource(self, modID = None):
		if modID is None:
			modID = self.modActive
		return self.modules[modID][1]


	def GetFilename(self, modID = None):
		if modID is None:
			modID = self.modActive
		return self.modules[self.modActive][2]


	def GetErrorInfo(self, modID = None):
		if modID is None:
			modID = self.modActive
		return self.modules[self.modActive][4]


	def Exists(self, modID):
		return self.modules[modID][1] != ""


	def UpdateFile(self, modID = None):
		"""Updates the file from which a module was loaded
		with (possibly updated) source"""
		if modID is None:
			modID = self.modActive

		source = self.modules[modID][1]
		filename = self.modules[modID][2]

		try:        
			file = open(filename, "wt")
			file.write(source)
		finally:
			file.close()


	def Delete(self, modID):
		if self.modActive == modID:
			self.SetActive(0)

		self.modules[modID][0] = None
		self.modules[modID][1] = ""
		self.modules[modID][2] = ""


#---------------------------------------------------------------------------

class DemoError:
	"""Wraps and stores information about the current exception"""
	def __init__(self, exc_info):
		import copy
		
		excType, excValue = exc_info[:2]
		# traceback list entries: (filename, line number, function name, text)
		self.traceback = traceback.extract_tb(exc_info[2])

		# --Based on traceback.py::format_exception_only()--
		if type(excType) == types.ClassType:
			self.exception_type = excType.__name__
		else:
			self.exception_type = excType

		# If it's a syntax error, extra information needs
		# to be added to the traceback
		if excType is SyntaxError:
			try:
				msg, (filename, lineno, self.offset, line) = excValue
			except:
				pass
			else:
				if not filename:
					filename = "<string>"
				line = line.strip()
				self.traceback.append( (filename, lineno, "", line) )
				excValue = msg
		try:
			self.exception_details = str(excValue)
		except:
			self.exception_details = "<unprintable %s object>" & type(excValue).__name__

		del exc_info
		
	def __str__(self):
		ret = "Type %s \n \
		Traceback: %s \n \
		Details  : %s" % ( str(self.exception_type), str(self.traceback), self.exception_details )
		return ret

#---------------------------------------------------------------------------

class DemoErrorPanel(wx.Panel):
	"""Panel put into the demo tab when the demo fails to run due  to errors"""

	def __init__(self, parent, codePanel, demoError, log):
		wx.Panel.__init__(self, parent, -1)#, style=wx.NO_FULL_REPAINT_ON_RESIZE)
		self.codePanel = codePanel
		self.nb = parent
		self.log = log

		self.box = wx.BoxSizer(wx.VERTICAL)

		# Main Label
		self.box.Add(wx.StaticText(self, -1, "An error has occurred while trying to run the demo")
					 , 0, wx.ALIGN_CENTER | wx.TOP, 10)

		# Exception Information
		boxInfo      = wx.StaticBox(self, -1, "Exception Info" )
		boxInfoSizer = wx.StaticBoxSizer(boxInfo, wx.VERTICAL ) # Used to center the grid within the box
		boxInfoGrid  = wx.FlexGridSizer(0, 2, 0, 0)
		textFlags    = wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT | wx.TOP
		boxInfoGrid.Add(wx.StaticText(self, -1, "Type: "), 0, textFlags, 5 )
		boxInfoGrid.Add(wx.StaticText(self, -1, str(demoError.exception_type)) , 0, textFlags, 5 )
		boxInfoGrid.Add(wx.StaticText(self, -1, "Details: ") , 0, textFlags, 5 )
		boxInfoGrid.Add(wx.StaticText(self, -1, demoError.exception_details) , 0, textFlags, 5 )
		boxInfoSizer.Add(boxInfoGrid, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
		self.box.Add(boxInfoSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
	   
		# Set up the traceback list
		# This one automatically resizes last column to take up remaining space
		from ListCtrl import TestListCtrl
		self.list = TestListCtrl(self, -1, style=wx.LC_REPORT  | wx.SUNKEN_BORDER)
		self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.list.InsertColumn(0, "Filename")
		self.list.InsertColumn(1, "Line", wx.LIST_FORMAT_RIGHT)
		self.list.InsertColumn(2, "Function")
		self.list.InsertColumn(3, "Code")
		self.InsertTraceback(self.list, demoError.traceback)
		self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		self.box.Add(wx.StaticText(self, -1, "Traceback:")
					 , 0, wx.ALIGN_CENTER | wx.TOP, 5)
		self.box.Add(self.list, 1, wx.GROW | wx.ALIGN_CENTER | wx.ALL, 5)
		self.box.Add(wx.StaticText(self, -1, "Entries from the demo module are shown in blue\n"
										   + "Double-click on them to go to the offending line")
					 , 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)

		self.box.Fit(self)
		self.SetSizer(self.box)


	def InsertTraceback(self, list, traceback):
		#Add the traceback data
		for x in range(len(traceback)):
			data = traceback[x]
			list.InsertStringItem(x, os.path.basename(data[0])) # Filename
			list.SetStringItem(x, 1, str(data[1]))              # Line
			list.SetStringItem(x, 2, str(data[2]))              # Function
			list.SetStringItem(x, 3, str(data[3]))              # Code
			
			# Check whether this entry is from the demo module
			if data[0] == "<original>" or data[0] == "<modified>": # FIXME: make more generalised
				self.list.SetItemData(x, int(data[1]))   # Store line number for easy access
				# Give it a blue colour
				item = self.list.GetItem(x)
				item.SetTextColour(wx.BLUE)
				self.list.SetItem(item)
			else:
				self.list.SetItemData(x, -1)        # Editor can't jump into this one's code
	   

	def OnItemSelected(self, event):
		# This occurs before OnDoubleClick and can be used to set the
		# currentItem. OnDoubleClick doesn't get a wxListEvent....
		self.currentItem = event.m_itemIndex
		event.Skip()

		
	def OnDoubleClick(self, event):
		# If double-clicking on a demo's entry, jump to the line number
		line = self.list.GetItemData(self.currentItem)
		if line != -1:
			self.nb.SetSelection(1) # Switch to the code viewer tab
			wx.CallAfter(self.codePanel.JumpToLine, line-1, True)
		event.Skip()
		

#---------------------------------------------------------------------------

class DemoTaskBarIcon(wx.TaskBarIcon):
	TBMENU_RESTORE = wx.NewId()
	TBMENU_CLOSE   = wx.NewId()
	TBMENU_CHANGE  = wx.NewId()
	TBMENU_REMOVE  = wx.NewId()
	
	def __init__(self, frame):
		wx.TaskBarIcon.__init__(self)
		self.frame = frame

		# Set the image
		icon = self.MakeIcon(images.WXPdemo.GetImage())
		self.SetIcon(icon, "wxPython Demo")
		self.imgidx = 1
		
		# bind some events
		self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
		self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
		self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
		self.Bind(wx.EVT_MENU, self.OnTaskBarChange, id=self.TBMENU_CHANGE)
		self.Bind(wx.EVT_MENU, self.OnTaskBarRemove, id=self.TBMENU_REMOVE)


	def CreatePopupMenu(self):
		"""
		This method is called by the base class when it needs to popup
		the menu for the default EVT_RIGHT_DOWN event.  Just create
		the menu how you want it and return it from this function,
		the base class takes care of the rest.
		"""
		menu = wx.Menu()
		menu.Append(self.TBMENU_RESTORE, "Restore wxPython Demo")
		menu.Append(self.TBMENU_CLOSE,   "Close wxPython Demo")
		menu.AppendSeparator()
		menu.Append(self.TBMENU_CHANGE, "Change the TB Icon")
		menu.Append(self.TBMENU_REMOVE, "Remove the TB Icon")
		return menu


	def MakeIcon(self, img):
		"""
		The various platforms have different requirements for the
		icon size...
		"""
		if "wxMSW" in wx.PlatformInfo:
			img = img.Scale(16, 16)
		elif "wxGTK" in wx.PlatformInfo:
			img = img.Scale(22, 22)
		# wxMac can be any size upto 128x128, so leave the source img alone....
		icon = wx.IconFromBitmap(img.ConvertToBitmap() )
		return icon
	

	def OnTaskBarActivate(self, evt):
		if self.frame.IsIconized():
			self.frame.Iconize(False)
		if not self.frame.IsShown():
			self.frame.Show(True)
		self.frame.Raise()


	def OnTaskBarClose(self, evt):
		wx.CallAfter(self.frame.Close)


	def OnTaskBarChange(self, evt):
		names = [ "WXPdemo", "Mondrian", "Pencil", "Carrot" ]                  
		name = names[self.imgidx]
		
		eImg = getattr(images, name)
		self.imgidx += 1
		if self.imgidx >= len(names):
			self.imgidx = 0
			
		icon = self.MakeIcon(eImg.Image)
		self.SetIcon(icon, "This is a new icon: " + name)


	def OnTaskBarRemove(self, evt):
		self.RemoveIcon()

import wx.lib.agw.aui as aui

import wx
#import wx.html
import wx.aui
#import wx.lib.agw.aui as aui
import  wx.grid             as  gridlib
#import sys, re, os,traceback, types
import dbi
import odbc, time, datetime
from pprint import pprint
#import images

class AUIManager(aui.AuiManager):
	""" from MikeDriscoll's AUI AGW tutorial on wxPyWiki 
	suggested as a way to run multiple AUI instances """
	def __init__(self, managed_window):
		aui.AuiManager.__init__(self)
		self.SetManagedWindow(managed_window)
try:
	##raise ImportError     # for testing the alternate implementation
	from wx import stc
	from StyledTextCtrl_sql import SqlSTC

	class CodeEditor(SqlSTC):
		def __init__(self, parent, style=wx.BORDER_NONE):
			SqlSTC.__init__(self, parent, -1, style=style)
			self.SetUpEditor()

		# Some methods to make it compatible with how the wxTextCtrl is used
		def SetValue(self, value):
			if wx.USE_UNICODE:
				value = value.decode('iso8859_1')
			val = self.GetReadOnly()
			#self.SetReadOnly(False)
			self.SetText(value)
			self.EmptyUndoBuffer()
			self.SetSavePoint()
			#self.SetReadOnly(val)

		#def SetEditable(self, val):
		#	self.SetReadOnly(not val)

		def IsModified(self):
			return self.GetModify()

		def Clear(self):
			self.ClearAll()

		def SetInsertionPoint(self, pos):
			self.SetCurrentPos(pos)
			self.SetAnchor(pos)

		def ShowPosition(self, pos):
			line = self.LineFromPosition(pos)
			#self.EnsureVisible(line)
			self.GotoLine(line)

		def GetLastPosition(self):
			return self.GetLength()

		def GetPositionFromLine(self, line):
			return self.PositionFromLine(line)

		def GetRange(self, start, end):
			return self.GetTextRange(start, end)

		def GetSelection(self):
			return self.GetAnchor(), self.GetCurrentPos()

		def SetSelection(self, start, end):
			self.SetSelectionStart(start)
			self.SetSelectionEnd(end)

		def SelectLine(self, line):
			start = self.PositionFromLine(line)
			end = self.GetLineEndPosition(line)
			self.SetSelection(start, end)
			
		def SetUpEditor(self):
			"""
			This method carries out the work of setting up the demo editor.            
			It's seperate so as not to clutter up the init code.
			"""
			import sql_keyword as keyword
			
			self.SetLexer(stc.STC_LEX_SQL)
			self.SetKeyWords(0, " ".join(keyword.kwlist))
	
			# Enable folding
			self.SetProperty("fold", "1" ) 

			# Highlight tab/space mixing (shouldn't be any)
			self.SetProperty("tab.timmy.whinge.level", "1")

			# Set left and right margins
			self.SetMargins(2,2)
	
			# Set up the numbers in the margin for margin #1
			self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
			# Reasonable value for, say, 4-5 digits using a mono font (40 pix)
			self.SetMarginWidth(1, 40)
	
			# Indentation and tab stuff
			self.SetIndent(4)               # Proscribed indent size for wx
			self.SetIndentationGuides(True) # Show indent guides
			self.SetBackSpaceUnIndents(True)# Backspace unindents rather than delete 1 space
			self.SetTabIndents(True)        # Tab key indents
			self.SetTabWidth(4)             # Proscribed tab size for wx
			self.SetUseTabs(False)          # Use spaces rather than tabs, or
											# TabTimmy will complain!    
			# White space
			self.SetViewWhiteSpace(False)   # Don't view white space
	
			# EOL: Since we are loading/saving ourselves, and the
			# strings will always have \n's in them, set the STC to
			# edit them that way.            
			self.SetEOLMode(wx.stc.STC_EOL_LF)
			self.SetViewEOL(False)
			
			# No right-edge mode indicator
			self.SetEdgeMode(stc.STC_EDGE_NONE)
	
			# Setup a margin to hold fold markers
			self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
			self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
			self.SetMarginSensitive(2, True)
			self.SetMarginWidth(2, 12)
	
			# and now set up the fold markers
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,    "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS, "white", "black")
	
			# Global default style
			if wx.Platform == '__WXMSW__':
				self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
								  'fore:#000000,back:#FFFFFF,face:Courier New')
			elif wx.Platform == '__WXMAC__':
				# TODO: if this looks fine on Linux too, remove the Mac-specific case 
				# and use this whenever OS != MSW.
				self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
								  'fore:#000000,back:#FFFFFF,face:Monaco')
			else:
				defsize = wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT).GetPointSize()
				self.StyleSetSpec(stc.STC_STYLE_DEFAULT, 
								  'fore:#000000,back:#FFFFFF,face:Courier,size:%d'%defsize)
	
			# Clear styles and revert to default.
			self.StyleClearAll()

			# Following style specs only indicate differences from default.
			# The rest remains unchanged.

			# Line numbers in margin
			self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,'fore:#000000,back:#99A9C2')    
			# Highlighted brace
			self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,'fore:#00009D,back:#FFFF00')
			# Unmatched brace
			self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,'fore:#00009D,back:#FF0000')
			# Indentation guide
			self.StyleSetSpec(wx.stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")
	
			# SQL styles
			self.StyleSetSpec(wx.stc.STC_SQL_DEFAULT, 'fore:#000000')
			# Comments
			self.StyleSetSpec(wx.stc.STC_SQL_COMMENTLINE,  'fore:#006600') #back:#F0FFF0,back:#FFFFCC
			self.StyleSetSpec(wx.stc.STC_SQL_COMMENT, 'fore:#006600')
			self.StyleSetSpec(wx.stc.STC_SQL_COMMENTDOC, 'fore:#006600')
			# Numbers
			self.StyleSetSpec(wx.stc.STC_SQL_NUMBER, 'fore:#008080')
			# Strings and characters
			self.StyleSetSpec(wx.stc.STC_SQL_STRING, 'fore:#800080')
			self.StyleSetSpec(wx.stc.STC_SQL_CHARACTER, 'fore:#FF0000')
			# Keywords
			self.StyleSetSpec(wx.stc.STC_SQL_WORD, 'fore:#00009D,bold')
			self.StyleSetSpec(wx.stc.STC_SQL_WORD2, 'fore:#00009D,bold')
			# Triple quotes
			self.StyleSetSpec(wx.stc.STC_SQL_QUOTEDIDENTIFIER, 'fore:#800080,back:#FFFFEA')
			self.StyleSetSpec(wx.stc.STC_SQL_SQLPLUS, 'fore:#800080,back:#FFFFEA')
			# Class names
			self.StyleSetSpec(wx.stc.STC_SQL_COMMENTLINEDOC, 'fore:#0000FF,bold')
			# Function names
			self.StyleSetSpec(wx.stc.STC_SQL_COMMENTDOCKEYWORD, 'fore:#008080,bold')
			# Operators
			self.StyleSetSpec(wx.stc.STC_SQL_OPERATOR, 'fore:#800000,bold')
			# Identifiers. I leave this as not bold because everything seems
			# to be an identifier if it doesn't match the above criterae
			self.StyleSetSpec(wx.stc.STC_SQL_IDENTIFIER, 'fore:#000000')

			# Caret color
			self.SetCaretForeground("BLACK")
			# Selection background
			self.SetSelBackground(1, '#66CCFF')

			self.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
			self.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

		def RegisterModifiedEvent(self, eventHandler):
			self.Bind(wx.stc.EVT_STC_CHANGE, eventHandler)


except ImportError:
		print 'cannot init class CodeEditor(SqlSTC)'
		sys.exit(1)

class SimpleGrid(gridlib.Grid): ##, mixins.GridAutoEditMixin):
	def __init__(self, parent, log):
		gridlib.Grid.__init__(self, parent, -1)
		##mixins.GridAutoEditMixin.__init__(self)
		self.log = log
		self.moveTo = None

		self.Bind(wx.EVT_IDLE, self.OnIdle)

		rows=10
		cols=25
		self.CreateGrid(rows, cols)#, gridlib.Grid.SelectRows)
		self.SetColFormatFloat(2,-1,2)
		
		
		# test all the events
		self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
		self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
		self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
		self.Bind(gridlib.EVT_GRID_CELL_RIGHT_DCLICK, self.OnCellRightDClick)

		self.Bind(gridlib.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
		self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
		self.Bind(gridlib.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)
		self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_DCLICK, self.OnLabelRightDClick)

		self.Bind(gridlib.EVT_GRID_ROW_SIZE, self.OnRowSize)
		self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnColSize)

		self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
		self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
		self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.OnSelectCell)

		self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnEditorShown)
		self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)
		self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnEditorCreated)
		self.Bind(wx.EVT_KEY_DOWN, self.onTextKeyEvent)
		#wx.EVT_KEY_DOWN, self.onTextKeyEvent,

	def UpdateGrid(self, sql):
		db = odbc.odbc("Driver={NetezzaSQL};servername=lltws01ypdbd1v;port=5480;database=MRR_BI;username=MRR_ETL_USER;password=Nynj2011;")
		cur = db.cursor()
		#select cob_dt_id,count(*) from CUBE_DATA_20130702173203_ab group by cob_dt_id;
		#sql="select * from CUBE_DATA_20130702173203_ab LIMIT 15;"
		pprint(sql);
		#pprint("select * from CUBE_DATA_20130702173203_ab LIMIT 15;");
		#cleanup
		sql = re.sub('(\n(\s+)?\n)', '',sql)
		sql = re.sub('[\r\n]+', '',sql)
		print '#'*20
		pprint (sql)
		print '#'*20
		print '%d' % cur.execute ("%s" % sql)
		
		#print [d[0] for d in c.description]
		#print 'cur.rowcount= ',cur.rowcount
		rs=cur.fetchall()

		rows=len(rs)
		cols=len(rs[0])
		print "new:  ", rows, cols
		print "Existing:  ",self.GetNumberRows(), self.GetNumberCols()
		#pprint(dir(self))
		self.ClearGrid()
		#self.DeleteGrid()
		newcols=cols-self.GetNumberCols()
		if newcols>=0: self.AppendCols(newcols)
		else: self.DeleteCols(cols,newcols)
		newrows=rows-self.GetNumberRows()
		if newrows>=0: self.AppendRows(newrows)
		else: self.DeleteRows(rows,newrows)
		#self.CreateGrid(rows, cols)#, gridlib.Grid.SelectRows)
		#self.EnableEditing(False)
		
		for r in range(rows):			
			for c in range(cols):			
				#print rs[r][c]
				self.SetCellValue(r, c, str(rs[r][c]))
			
		headers=cur.description
		for d in range(len(headers)):
			#print headers[d]
			self.SetColLabelValue(d, headers[d][0])

		self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
		print "Updating grid"

	def UpdateLimitedGrid(self, sql):
		#global d
		db = odbc.odbc("Driver={NetezzaSQL};servername=lltws01ypdbd1v;port=5480;database=MRR_BI;username=MRR_ETL_USER;password=Nynj2011;")
		cur = db.cursor()
		#select cob_dt_id,count(*) from CUBE_DATA_20130702173203_ab group by cob_dt_id;
		#sql="select * from CUBE_DATA_20130702173203_ab LIMIT 15;"
		pprint(sql);
		#pprint("select * from CUBE_DATA_20130702173203_ab LIMIT 15;");
		#cleanup
		#sql = re.sub('(\n(\s+)?\n)', '',sql)
		#sql = re.sub('[\r\n]+', '',sql)
		print '#'*20
		pprint (sql)
		print '#'*20
		#print 'before exec'
		status=0
		rowcount=0
		headers=[]
		err=''
		i=1
		#rowcount=0
		self.ClearGrid()
		try:
			d = PBI.PyBusyInfo('Executing query...', title='NZ SQL')
			wx.Yield()
			status=cur.execute ("%s" % sql)
			pprint(dir(cur))
			print cur.description
			#print 'cur.rowcount= ',cur.arraysize
		except dbi.progError, e:
			del d
			print 'dbi.progError! '
			status=1
			err=e
		except dbi.internalError, e:
			del d
			print 'dbi.internalError! ', status
			status=1
			err=e
			
		#print 'after exec: ', status
		
		#print [d[0] for d in c.description]

			
		if err: # or (not status and not cur.description) :
			#print(dir(d))
			print '#'*60
			print err
			print '#'*60
			print status
			self.ClearGrid()
			#self.DeleteCols(0,self.GetNumberCols(), True)
			print 'self.GetNumberCols()= ',self.GetNumberCols()
		else:
			headers=cur.description
			if headers:
				print 'self.GetNumberCols()= ',self.GetNumberCols()
				print "Status: ", status
				print dir(cur)
				print 'fetch# %d' % i
				rs=cur.fetchone()
				#print(dir(self))
				
				if rs:
					
					self.ForceRefresh()
					self.BeginBatch()
					#self.ClearGrid()
					while rs and i<101:
						#self.BeginBatch()
						rows=i # len(rs)
						cols=len(rs)
						#print "new:  ", rows, cols
						#print "Existing:  ",self.GetNumberRows(), self.GetNumberCols()
						#			
						#self.DeleteGrid()
						#print "newrows1"

						if i==1:
							attr = gridlib.GridCellAttr()
							#pprint(dir(attr))
						newcols=cols-self.GetNumberCols()
						#print 'Columns1: ', cols, self.GetNumberCols(), newcols
						if newcols>=0: 					
							if newcols>0: 
								#print "appending cols1"
								self.AppendCols(newcols)
							#else:
							#	#print "no cols change 1"
							#	pass
						else:
							#print "deleting cols1"
							self.DeleteCols(cols,newcols)

						newrows=rows-self.GetNumberRows()
						#print 'Rows1: ', rows, self.GetNumberRows(), newrows
						if newrows>=0: 
							#print 'appending rows 1:', newrows
							self.AppendRows(newrows)
						else: self.DeleteRows(rows,newrows)
						
						#self.CreateGrid(rows, cols)#, gridlib.Grid.SelectRows)
						#self.EnableEditing(False)
						
						#for r in range(rows):	
						#print 'range cols1: ', i
						#print rs
						for c in range(cols):			
							#print 1,c,str(rs[c])
							#print 'setting val 1: ', i-1, c, str(rs[c])
							self.SetCellValue(i-1, c, str(rs[c]))
							#self.Refresh()
						#headers=cur.description
						for d in range(len(headers)):
							#print headers[d]
							self.SetColLabelValue(d, headers[d][0])

						self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
						#print "Updating limited grid"
						i+=1
						#self.EndBatch()
						
						rs=cur.fetchone()
						
						#time.sleep(5)
					self.EndBatch()
					rowcount=i-1
				else:
					#self.BeginBatch()
					if self.GetNumberRows()>0:
						#self.DeleteRows(0,self.GetNumberRows())
						#self.UpdateAttrRows(0,self.GetNumberRows())
						#msg = wx.grid.GridTableMessage(self.GetTable(), wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, 0,self.GetNumberRows() )
						#self.GetTable().GetView().ProcessTableMessage(wx.grid.GridTableMessage( self.GetTable(),wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,  self.GetNumberRows()))
						#self.ForceRefresh()
						#self.Refresh()
						#pprint(dir(self.GetTable()))
						self.ClearGrid()
						
					#self.ForceRefresh()
					#headers=cur.description
					cols=len(headers)
					newcols=cols-self.GetNumberCols()
					print 'Columns0: ', cols, self.GetNumberCols(), newcols
					#pprint(headers)
					#print 'Columns1: ', cols, self.GetNumberCols(), newcols
					#self.ResetGrid()
					if newcols>=0: 					
						if newcols>0: 
							print "appending cols1"
							self.AppendCols(newcols)
						#else:
						#	#print "no cols change 1"
						#	pass
					else:
						print "deleting cols1"
						self.DeleteCols(cols,newcols)	
					#self.ResetGrid()
					print 'after append cols'
					if self.GetNumberCols()>0:
						for d in range(len(headers)):
							#print headers[d]
							self.SetColLabelValue(d, headers[d][0])
					#pass
					#self.EndBatch()
					#self.ForceRefresh()
					err='0 records returned.'
			else:
				del d
				print 'Success status= ',status
				print err
				print cur.error()
				print 
				if status>0:
					print 'Rows affected: %d' % status
					#rowcount=status
				#err='Success.'
			#pprint(dir(self))	
		return (status, err, rowcount,headers)
	def ClearGrid(self):
		self.GetTable().Clear()		
		numr=self.GetNumberRows()
		if numr<0: numr=0;
		print "after delete: ", numr
		if numr>0:
			self.DeleteRows(0,numr)
			self.GetTable().GetView().ProcessTableMessage(wx.grid.GridTableMessage( self.GetTable(),wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,  self.GetNumberRows(),1))
		print "after delete fix: ", self.GetNumberRows()	
	def OnCellLeftClick(self, evt):
		self.log.write("OnCellLeftClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnCellRightClick(self, evt):
		self.log.write("OnCellRightClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnCellLeftDClick(self, evt):
		self.log.write("OnCellLeftDClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnCellRightDClick(self, evt):
		self.log.write("OnCellRightDClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelLeftClick(self, evt):
		self.log.write("OnLabelLeftClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelRightClick(self, evt):
		self.log.write("OnLabelRightClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelLeftDClick(self, evt):
		self.log.write("OnLabelLeftDClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnLabelRightDClick(self, evt):
		self.log.write("OnLabelRightDClick: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()

	def OnRowSize(self, evt):
		self.log.write("OnRowSize: row %d, %s\n" %
					   (evt.GetRowOrCol(), evt.GetPosition()))
		evt.Skip()

	def OnColSize(self, evt):
		self.log.write("OnColSize: col %d, %s\n" %
					   (evt.GetRowOrCol(), evt.GetPosition()))
		evt.Skip()

	def OnRangeSelect(self, evt):
		if evt.Selecting():
			msg = 'Selected'
		else:
			msg = 'Deselected'
		self.log.write("OnRangeSelect: %s  top-left %s, bottom-right %s\n" %
						   (msg, evt.GetTopLeftCoords(), evt.GetBottomRightCoords()))
		evt.Skip()


	def OnCellChange(self, evt):
		self.log.write("OnCellChange: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))

		# Show how to stay in a cell that has bad data.  We can't just
		# call SetGridCursor here since we are nested inside one so it
		# won't have any effect.  Instead, set coordinates to move to in
		# idle time.
		value = self.GetCellValue(evt.GetRow(), evt.GetCol())

		if value == 'no good':
			self.moveTo = evt.GetRow(), evt.GetCol()


	def OnIdle(self, evt):
		if self.moveTo != None:
			self.SetGridCursor(self.moveTo[0], self.moveTo[1])
			self.moveTo = None

		evt.Skip()


	def OnSelectCell(self, evt):
		if evt.Selecting():
			msg = 'Selected'
		else:
			msg = 'Deselected'
		self.log.write("OnSelectCell: %s (%d,%d) %s\n" %
					   (msg, evt.GetRow(), evt.GetCol(), evt.GetPosition()))

		# Another way to stay in a cell that has a bad value...
		row = self.GetGridCursorRow()
		col = self.GetGridCursorCol()

		if self.IsCellEditControlEnabled():
			self.HideCellEditControl()
			self.DisableCellEditControl()

		value = self.GetCellValue(row, col)

		if value == 'no good 2':
			return  # cancels the cell selection

		evt.Skip()


	def OnEditorShown(self, evt):
		if evt.GetRow() == 6 and evt.GetCol() == 3 and \
		   wx.MessageBox("Are you sure you wish to edit this cell?",
						"Checking", wx.YES_NO) == wx.NO:
			evt.Veto()
			return

		self.log.write("OnEditorShown: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()


	def OnEditorHidden(self, evt):
		if evt.GetRow() == 6 and evt.GetCol() == 3 and \
		   wx.MessageBox("Are you sure you wish to  finish editing this cell?",
						"Checking", wx.YES_NO) == wx.NO:
			evt.Veto()
			return

		self.log.write("OnEditorHidden: (%d,%d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetPosition()))
		evt.Skip()


	def OnEditorCreated(self, evt):
		self.log.write("OnEditorCreated: (%d, %d) %s\n" %
					   (evt.GetRow(), evt.GetCol(), evt.GetControl()))

	def onTextKeyEvent(self, event):
		keycode = event.GetKeyCode()
		#print keycode
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
		event.Skip()					   
	def copy(self):
		print "Copy method"
		# Number of rows and cols
		# data variable contain text that must be set in the clipboard
		
		data = ''
		#print(dir(self))

		
		if self.GetSelectionBlockTopLeft() and self.GetSelectionBlockBottomRight():
			#print "copy blocks %s , %s" % (self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight())
			#rows = self.GetSelectionBlockBottomRight()[0][0] - self.GetSelectionBlockTopLeft()[0][0] + 1
			#cols = self.GetSelectionBlockBottomRight()[0][1] - self.GetSelectionBlockTopLeft()[0][1] + 1
			rows_from = []
			rows_to = []
			for r in self.GetSelectionBlockTopLeft():
				rows_from.append(r[0])
			for r in self.GetSelectionBlockBottomRight():
				rows_to.append(r[0])
			cols = []
			for c in range(len(self.GetSelectionBlockTopLeft())):
				cols.append(range(self.GetSelectionBlockTopLeft()[c][1],self.GetSelectionBlockBottomRight()[c][1]+1))
			#print rows_from,rows_to, cols
			#sys.exit(1)
			
			#set([1,2]).union(set([2,3]))
			data=''
			for colset in cols:
				#print self.GetColLabelValue(i)
				for c in colset:
					data = data+self.GetColLabelValue(c) + '\t'	
			data = data + '\n'	
			#print 			self.GetColLabelValue([0,1])
			#print data
			#sys.exit(1)
			# For each cell in selected range append the cell value in the data variable
			# Tabs '\t' for cols and '\r' for rows
			for r in range(min(rows_from),max(rows_to)):
				#print 'r=',r
				for cs in range(len(cols)):
					#print 'cs=', cs
					for c in range(len(cols[cs])):	
						#print c, cols[cs][c]
						if r>=rows_from[cs] and r<=rows_to[cs]:
							#print r, 'value= ',self.GetCellValue(r, cols[cs][c])
							data = data + str(self.GetCellValue(r, cols[cs][c]))
						#else:
						#	data = data + '\t'
						#data = data + str(self.GetCellValue(self.GetSelectionBlockTopLeft()[0][0] + r, self.GetSelectionBlockTopLeft()[0][1] + c))
						if c < len(cols[cs]) - 1:						
							data = data + '\t'
					if cs < len(cols) - 1:						
						data = data + '\t'
					#print '\n'
				data = data + '\n'
			#print data
		if self.GetSelectedCols():
			rows=self.GetNumberRows()
			cols =len(self.GetSelectedCols())
			for c in range(cols):
				#print self.GetColLabelValue(i)
				data = data+self.GetColLabelValue(self.GetSelectedCols()[0]+c) + '\t'	
			data = data + '\n'
			print "copy cols %s " % self.GetSelectedCols()
			#pprint (self.GetNumberRows())
			print cols			
			for r in range(rows):
				for c in range(cols):
					data = data + str(self.GetCellValue(r, self.GetSelectedCols()[0]+c))
					if c < cols - 1:
						data = data + '\t'
				data = data + '\n'	
		if self.GetSelectedRows():
			rows=len(self.GetSelectedRows())
			cols =self.GetNumberCols()	
			for c in range(cols):
				#print self.GetColLabelValue(i)
				data = data+self.GetColLabelValue(c) + '\t'
			data = data + '\n'

			print "copy rows, cols  %s %s"  %  (rows,cols)			
			#sys.exit(1)
			#pprint (self.GetNumberRows())
			print cols			
			for r in range(rows):
				for c in range(cols):
					data = data + str(self.GetCellValue(self.GetSelectedRows()[0]+r, c))
					if c < cols - 1:
						data = data + '\t'
				data = data + '\n'	
		if self.GetSelectedCells():
			data=str(self.GetSelectedCells())
		if not data:
			row = self.GetGridCursorRow()
			col = self.GetGridCursorCol()

			data = self.GetCellValue(row, col)
			
		# Create text data object
		clipboard = wx.TextDataObject()
		# Set data object value
		clipboard.SetText(data)
		# Put the data in the clipboard
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(clipboard)
			wx.TheClipboard.Close()
		else:
			wx.MessageBox("Can't open the clipboard", "Error")		

	def copy0(self):
		print "Copy method"
		# Number of rows and cols
		# data variable contain text that must be set in the clipboard
		
		data = ''
		#print(dir(self))

		
		if self.GetSelectionBlockTopLeft() and self.GetSelectionBlockBottomRight():
			print "copy blocks %s %s" % (self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight())
			rows = self.GetSelectionBlockBottomRight()[0][0] - self.GetSelectionBlockTopLeft()[0][0] + 1
			cols = self.GetSelectionBlockBottomRight()[0][1] - self.GetSelectionBlockTopLeft()[0][1] + 1
			print rows, cols
			for c in range(cols):
				#print self.GetColLabelValue(i)
				data = data+self.GetColLabelValue(self.GetSelectionBlockTopLeft()[0][1]+c) + '\t'	
			data = data + '\n'			

			# For each cell in selected range append the cell value in the data variable
			# Tabs '\t' for cols and '\r' for rows
			for r in range(rows):
				print r
				for c in range(cols):
					print c
					data = data + str(self.GetCellValue(self.GetSelectionBlockTopLeft()[0][0] + r, self.GetSelectionBlockTopLeft()[0][1] + c))
					if c < cols - 1:
						
						data = data + '\t'
				data = data + '\n'
			
		if self.GetSelectedCols():

			rows=self.GetNumberRows()
			cols =len(self.GetSelectedCols())
			for c in range(cols):
				#print self.GetColLabelValue(i)
				data = data+self.GetColLabelValue(self.GetSelectedCols()[0]+c) + '\t'	
			data = data + '\n'
			print "copy cols %s " % self.GetSelectedCols()
			#pprint (self.GetNumberRows())
			print cols			
			for r in range(rows):
				for c in range(cols):
					data = data + str(self.GetCellValue(r, self.GetSelectedCols()[0]+c))
					if c < cols - 1:
						data = data + '\t'
				data = data + '\n'	
		if self.GetSelectedRows():
			rows=len(self.GetSelectedRows())
			cols =self.GetNumberCols()	
			for c in range(cols):
				#print self.GetColLabelValue(i)
				data = data+self.GetColLabelValue(c) + '\t'
			data = data + '\n'

			print "copy rows, cols  %s %s"  %  (rows,cols)			
			#sys.exit(1)
			#pprint (self.GetNumberRows())
			print cols			
			for r in range(rows):
				for c in range(cols):
					data = data + str(self.GetCellValue(self.GetSelectedRows()[0]+r, c))
					if c < cols - 1:
						data = data + '\t'
				data = data + '\n'	
			
		# Create text data object
		clipboard = wx.TextDataObject()
		# Set data object value
		clipboard.SetText(data)
		# Put the data in the clipboard
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(clipboard)
			wx.TheClipboard.Close()
		else:
			wx.MessageBox("Can't open the clipboard", "Error")			
#----------------------------------------------------------------------
class OutputPanel(wx.Panel):
	"""
	SQL exucution status messages
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		sizer = wx.BoxSizer(wx.VERTICAL)
		#txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
		#txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")
		#page = wx.TextCtrl(self, -1, text, style=wx.TE_MULTILINE)
		#nb = wx.aui.AuiNotebook(self)
		#self.grid = SimpleGrid(self, sys.stdout)
		#l4 = wx.StaticText(self, -1, "Rich Text")
		#pprint(dir(time))
		self.status = wx.TextCtrl(self, -1, str(datetime.datetime.now()),
							wx.DefaultPosition, wx.Size(50,300),
							wx.NO_BORDER | wx.TE_MULTILINE|wx.TE_RICH2)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		#sizer.Add(txtOne, 0, wx.ALL, 5)
		#sizer.Add(txtTwo, 0, wx.ALL, 5)
		sizer.Add(self.status,  -1, wx.EXPAND)
		#sizer.Add(nb,  1, wx.EXPAND)
		self.SetSizer(sizer)
	def Error(self,err):
		#print(dir(self.status))
		self.status.SetValue(str(err))
		self.status.SetInsertionPoint(0)
		points = self.status.GetFont().GetPointSize() 
		style = self.status.GetFont().GetStyle()
		weight= self.status.GetFont().GetWeight()
		f = wx.Font(points+3,wx.FONTFAMILY_DEFAULT,style,weight)
		self.status.SetStyle(6, len(str(err)), wx.TextAttr("RED", wx.NullColour,f))
		 # get the current size
		#f = wx.Font(points, wx.ROMAN, None, wx.BOLD, True)
		#self.status.SetStyle(0, 5, wx.TextAttr("BLUE", wx.NullColour, f))
		self.SetFocus()
	def Status(self,status):
		#print(dir(self.status))
		self.status.SetValue("%s" % (str(status)))
		#self.status.SetInsertionPoint(0)
		#points = self.status.GetFont().GetPointSize() 
		#style = self.status.GetFont().GetStyle()
		#weight= self.status.GetFont().GetWeight()
		#f = wx.Font(points+3,wx.FONTFAMILY_DEFAULT,style,weight)
		#self.status.SetStyle(0, len(str(status)), wx.TextAttr("GREEN", wx.NullColour,f))
		 # get the current size
		#f = wx.Font(points, wx.ROMAN, None, wx.BOLD, True)
		#self.status.SetStyle(0, 5, wx.TextAttr("BLUE", wx.NullColour, f))
		self.SetFocus()
		
	def Elapsed(self,delta):
		#print(dir(self.status))
		
		self.status.SetValue("%s\nElapsed: %s seconds." % (self.status.GetValue(),delta))
	
#----------------------------------------------------------------------
class ExportPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		sizer = wx.BoxSizer(wx.VERTICAL)
		#txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
		#txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")
		#page = wx.TextCtrl(self, -1, text, style=wx.TE_MULTILINE)
		#nb = wx.aui.AuiNotebook(self)
		#self.grid = SimpleGrid(self, sys.stdout)
		text2 = wx.TextCtrl(self, -1, 'Export - sample text',
							wx.DefaultPosition, wx.Size(50,300),
							wx.NO_BORDER | wx.TE_MULTILINE)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		#sizer.Add(txtOne, 0, wx.ALL, 5)
		#sizer.Add(txtTwo, 0, wx.ALL, 5)
		sizer.Add(text2,  -1, wx.EXPAND)
		#sizer.Add(nb,  1, wx.EXPAND)
		self.SetSizer(sizer)		
#----------------------------------------------------------------------
class ResultsPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		sizer = wx.BoxSizer(wx.VERTICAL)
		#txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
		#txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")
		#page = wx.TextCtrl(self, -1, text, style=wx.TE_MULTILINE)
		#nb = wx.aui.AuiNotebook(self)
		self.grid = SimpleGrid(self, sys.stdout)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		#sizer.Add(txtOne, 0, wx.ALL, 5)
		#sizer.Add(txtTwo, 0, wx.ALL, 5)
		sizer.Add(self.grid,  -1, wx.EXPAND)
		#sizer.Add(nb,  1, wx.EXPAND)
		self.SetSizer(sizer)
	def onTextKeyEvent(self, event):
		keycode = event.GetKeyCode()
		print keycode
		controlDown = event.CmdDown()
		print 'res ctrl: ',controlDown
		if controlDown and keycode == 65:
			print "res Ctrl-A"
			#self.page.SetSelection(-1, -1)
		#if keycode==344: #F5 
		#	self.ExecSQL()
		event.Skip()
class ResultsNbPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		# create the AuiNotebook instance
		nb = wx.aui.AuiNotebook(self)

		# add some pages to the notebook
		self.pages = [(ResultsPanel(nb), "Results"),
				 (OutputPanel(nb), "Output"),
				 (ExportPanel(nb), "Export")]
		for page, label in self.pages:
			nb.AddPage(page, label)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(nb, 1, wx.EXPAND)
		self.SetSizer(sizer)
		
text = """\
select * from CUBE_DATA_20130702173203_ab LIMIT 15;"""
d=None
class QueryPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		sizer = wx.BoxSizer(wx.VERTICAL)
		#txtOne = wx.TextCtrl(self, wx.ID_ANY, "")
		#txtTwo = wx.TextCtrl(self, wx.ID_ANY, "")

		
		b = wx.Button(self, 10, "Execute", (20, 20))
		self.Bind(wx.EVT_BUTTON, self.OnClick, b)
		b.SetDefault()
		b.SetSize(b.GetBestSize())
		self.parent=parent



		sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer.Add(txtOne, 0, wx.ALL, 5)
		#sizer.Add(txtTwo, 0, wx.ALL, 5)
		sizer.Add(b, 0, wx.ALL, 5)

		self.editor = CodeEditor(self)
		self.page = self.onWidgetSetup(self.editor,
								 wx.EVT_KEY_DOWN, self.onTextKeyEvent,
								 sizer)
		#font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
		#self.page.SetFont(font1)

		#self.page.SetDimensions(x=150, y=60, width=100, height=20)
		
		#sizer.Add(self.page,  1, wx.EXPAND)
		#sizer.Add(nb,  1, wx.EXPAND)
		
		self.SetSizer(sizer)
	def onWidgetSetup(self, widget, event, handler, sizer):
		widget.Bind(event, handler)
		#sizer.Add(widget, 0, wx.ALL, 5)
		sizer.Add(widget,  1, wx.EXPAND)
		return widget
	def onTextKeyEvent(self, event):
		keycode = event.GetKeyCode()
		print keycode
		controlDown = event.CmdDown()
		print 'ctrl: ',controlDown
		if controlDown and keycode == 65:
			print "Ctrl-A"
			self.page.SetSelection(-1, -1)
		#if controlDown and keycode == 83:
		#	print "Ctrl-S"
		#	wx.PyCommandEvent(wx.ID_SAVE, self.GetId())
		#	self.GetEventHandler().ProcessEvent(event)
			
		if keycode==344: #F5 
			self.ExecSQL()
		if keycode==345: #F6 
			self.ExplainSQL()			
		event.Skip()

		
	def OnClick(self, event):
		msg = 'Retrieving data...'
		title = 'NZ SQL'

		self.ExecSQL();
		#del d
	def ExecSQL(self):
		sys.stdout.write(self.page.GetText())
		start, end = self.page.GetSelection()
		print '#'*40
		print '\nSelection:-------', start, end,(end-start)
		#if wx.Platform == "__WXMSW__":  # This is why GetStringSelection was added
		#	#self.page.SetValue(self.page.GetValue().replace('\n', '\r\n')) 
		text = self.page.GetText()
		#if wx.Platform == "__WXMSW__":  # This is why GetStringSelection was added
		#	text = text.replace('\n', '\r\n')	
				
		if abs(end-start)>0:
			if end<start:
				end, start=start, end
			sql=text[start:end]
			print 'selection: ', sql
		else:
			

			ip = self.page.GetCurrentPos() #GetInsertionPoint()
			lp = self.page.GetLastPosition()
			print "Coordinates: ",ip, lp
			#sys.exit(1)
			before=text[:ip] #.rstrip(" ")

			print ">%s<" % before
			after=text[ip:]
			print after
			for m in re.finditer('\n(\s+)?\n', before):
				
				print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
				last=m
			last = list(re.finditer('\n(\s+)?\n', before))[-1:]
			print last
			(q_start, q_end) = (-1,-1)
			if len(last)==1:
				#last = last2[0]
				(ignore, q_start, white) = (last[0].start(), last[0].end(), last[0].group(0))
				print q_start
			
			sql=text
			m =list(re.finditer('\n(\s+)?\n', after))
			if m:
				#last = last2[0]
				(q_end, ignore, white) = (m[0].start(), m[0].end(), m[0].group(0))
				print q_end, ignore, white
			
			(q_from, q_to) = (q_start,len(before)+q_end)
			if q_end==-1:
				(q_from, q_to) = (q_start,lp)
				sql=text[q_start:lp]
			if q_start==-1:
				(q_from, q_to) = (0,len(before)+q_end)
				sql=text[0:len(before)+q_end]
			
			
			if q_start==-1 and q_end==-1:
				print "resetting..."
				q_from, q_to = (-1, -1)
				sql=text
				
			print "cuts: ", q_start, q_end
			print "highlighting: ", q_from, q_to	
			self.page.SetSelection(q_from, q_to)
			if q_from>0 and q_to>0:
				sql=text[q_from:q_to]
		#print "executing: ", sql
		#self.parent.GetPage(0).grid.UpdateLimitedGrid(sql)
		start_time = time.time()
		(status, err, rowcount, headers)=self.parent.rp.pages[0][0].grid.UpdateLimitedGrid(sql)
		print 'out= %s,%s,%s,%s ' % (status, err, rowcount, headers)
		if status and err: self.parent.rp.pages[1][0].Error(err)
		else: 	
			if not status and headers:
				if rowcount>0:
					self.parent.rp.pages[1][0].Status('%d rows returned.' % rowcount)
					self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
					self.parent.rp.pages[0][0].SetFocus()
					self.SetFocus()
				else:
					self.parent.rp.pages[1][0].Status(err)
					self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
					self.parent.rp.pages[1][0].SetFocus()
					self.SetFocus()
			else:
				if status>0 and not headers:
					self.parent.rp.pages[1][0].Status('%d rows affected.' % status)
					self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
					self.parent.rp.pages[1][0].SetFocus()	
					self.SetFocus()
				else:
					if status==-1 and not headers and not rowcount:
						self.parent.rp.pages[1][0].Status('DROP/TRUNCATE success.')
						self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
						self.parent.rp.pages[1][0].SetFocus()
						self.SetFocus()
					if status==0 and not headers and not rowcount:
						self.parent.rp.pages[1][0].Status('CREATE/UPDATE success.')
						self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
						self.parent.rp.pages[1][0].SetFocus()	
						self.SetFocus()				
					
				
		#print status, err
	def ExplainSQL(self):
		sys.stdout.write(self.page.GetText())
		start, end = self.page.GetSelection()
		print '#'*40
		print '\nSelection:-------', start, end,(end-start)
		#if wx.Platform == "__WXMSW__":  # This is why GetStringSelection was added
		#	#self.page.SetValue(self.page.GetValue().replace('\n', '\r\n')) 
		text = self.page.GetText()
		#if wx.Platform == "__WXMSW__":  # This is why GetStringSelection was added
		#	text = text.replace('\n', '\r\n')	
				
		if abs(end-start)>0:
			if end<start:
				end, start=start, end
			sql=text[start:end]
			print 'selection: ', sql
		else:
			

			ip = self.page.GetCurrentPos() #GetInsertionPoint()
			lp = self.page.GetLastPosition()
			print "Coordinates: ",ip, lp
			#sys.exit(1)
			before=text[:ip] #.rstrip(" ")

			print ">%s<" % before
			after=text[ip:]
			print after
			for m in re.finditer('\n(\s+)?\n', before):
				
				print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
				last=m
			last = list(re.finditer('\n(\s+)?\n', before))[-1:]
			print last
			(q_start, q_end) = (-1,-1)
			if len(last)==1:
				#last = last2[0]
				(ignore, q_start, white) = (last[0].start(), last[0].end(), last[0].group(0))
				print q_start
			
			sql=text
			m =list(re.finditer('\n(\s+)?\n', after))
			if m:
				#last = last2[0]
				(q_end, ignore, white) = (m[0].start(), m[0].end(), m[0].group(0))
				print q_end, ignore, white
			
			(q_from, q_to) = (q_start,len(before)+q_end)
			if q_end==-1:
				(q_from, q_to) = (q_start,lp)
				sql=text[q_start:lp]
			if q_start==-1:
				(q_from, q_to) = (0,len(before)+q_end)
				sql=text[0:len(before)+q_end]
			
			
			if q_start==-1 and q_end==-1:
				print "resetting..."
				q_from, q_to = (-1, -1)
				sql=text
				
			print "cuts: ", q_start, q_end
			print "highlighting: ", q_from, q_to	
			self.page.SetSelection(q_from, q_to)
			if q_from>0 and q_to>0:
				sql=text[q_from:q_to]
		#print "executing: ", sql
		#self.parent.GetPage(0).grid.UpdateLimitedGrid(sql)
		start_time = time.time()
		(status, err, rowcount, headers)=self.parent.rp.pages[0][0].grid.UpdateLimitedGrid("EXPLAIN PLAN FOR %s" % sql)
		print 'out= %s,%s,%s,%s ' % (status, err, rowcount, headers)
		if status and err: self.parent.rp.pages[1][0].Error(err)
		else: 	
			if not status and headers:
				if rowcount>0:
					self.parent.rp.pages[1][0].Status('%d rows returned.' % rowcount)
					self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
					self.parent.rp.pages[0][0].SetFocus()
					self.SetFocus()
				else:
					self.parent.rp.pages[1][0].Status(err)
					self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
					self.parent.rp.pages[1][0].SetFocus()
					self.SetFocus()
			else:
				if status>0 and not headers:
					self.parent.rp.pages[1][0].Status('%d rows affected.' % status)
					self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
					self.parent.rp.pages[1][0].SetFocus()	
					self.SetFocus()
				else:
					if status==-1 and not headers and not rowcount:
						self.parent.rp.pages[1][0].Status('DROP/TRUNCATE success.')
						self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
						self.parent.rp.pages[1][0].SetFocus()
						self.SetFocus()
					if status==0 and not headers and not rowcount:
						self.parent.rp.pages[1][0].Status('CREATE success.')
						self.parent.rp.pages[1][0].Elapsed(time.time() - start_time)			
						self.parent.rp.pages[1][0].SetFocus()	
						self.SetFocus()				
					
				
		#print status, err		
class TabPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""

		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		self._mgr = AUIManager(self)
		# create several text controls
		#text1 = wx.TextCtrl(self, -1, 'Pane 1 - sample text',
		#					wx.DefaultPosition, wx.Size(500,500),
		#					wx.NO_BORDER | wx.TE_MULTILINE)
		self.qp=QueryPanel(self)
		self.rp=ResultsNbPanel(self)
		#text2 = wx.TextCtrl(self, -1, 'Pane 2 - sample text',
		#					wx.DefaultPosition, wx.Size(50,300),
		#					wx.NO_BORDER | wx.TE_MULTILINE)
		#self.grid = SimpleGrid(self, sys.stdout)
		#text3 = wx.TextCtrl(self, -1, 'Main content window',
		#					wx.DefaultPosition, wx.Size(50,100),
		#					wx.NO_BORDER | wx.TE_MULTILINE)
		
		# add the panes to the manager
		self._mgr.AddPane(self.qp, wx.CENTER)
		self._mgr.AddPane(self.rp, wx.CENTER)
		#self._mgr.AddPane(text3, wx.CENTER)

		# tell the manager to 'commit' all the changes just made
		self._mgr.Update()

		
		

class SQLPanel(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent):
		""""""
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

		# create the AuiNotebook instance
		self.nb = wx.aui.AuiNotebook(self)

		# add some pages to the notebook
		"""self.pages = [(TabPanel(self.nb), "SQL_1"),
				 (TabPanel(self.nb), "SQL_2"),
				 (TabPanel(self.nb), "SQL_3")]
		"""
		self.pages=[]
		self.new=0
		for p in range(3):
			self.AddNew("SQL_%d.sql" % p, text)
			self.new=p+1
			
		
		#sizer = wx.BoxSizer(wx.VERTICAL)
		#sizer.Add(self.nb, 1, wx.EXPAND)
		#self.SetSizer(sizer)
		#self.bind_events()
	def AddNew(self, label='', value=''):
		print "on new2"
		if not label:
			label="SQL_%d.sql" % (len(self.pages)+1)		
		
		page = TabPanel(self.nb)
		page.file_name=label
		page.saved=False
		self.pages.append((page, label));
		#(page, label) = self.pages[-1:][0]
		#print page, label
		self.nb.AddPage(page, label)
		page.qp.page.SetValue(value)
		
		#self.SetFocus()
		print self.nb.PageCount
		selected_page = self.nb.GetPage(self.nb.PageCount-1)
		#print (dir(self.nb))
		self.nb.SetFocus()
		selected_page.SetFocus()
		#return page
	#def bind_events(self):
	#	self.Bind(wx.EVT_MENU, self.on_new, id=ID_New) 
	
#---------------------------------------------------------------------------
class wxPythonDemo(wx.Frame):
	overviewText = "wxPython Overview"

	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title, size = (970, 720),
						  style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

		self.SetMinSize((640,480))

		# Use a panel under the AUI panes in order to work around a
		# bug on PPC Macs
		pnl = wx.Panel(self)
		self.pnl = pnl
		
		self.mgr = wx.aui.AuiManager()
		self.mgr.SetManagedWindow(pnl)

		self.loaded = False
		self.cwd = os.getcwd()
		self.curOverview = ""
		self.demoPage = None
		self.codePage = None
		self.shell = None
		self.firstTime = True
		self.finddlg = None

		icon = images.WXPdemo.GetIcon()
		self.SetIcon(icon)

		try:
			self.tbicon = DemoTaskBarIcon(self)
		except:
			self.tbicon = None
			
		self.otherWin = None
		self.Bind(wx.EVT_IDLE, self.OnIdle)
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
		self.Bind(wx.EVT_MAXIMIZE, self.OnMaximize)

		self.Centre(wx.BOTH)
		self.CreateStatusBar(1, wx.ST_SIZEGRIP)

		self.dying = False
		self.skipLoad = False
		
		def EmptyHandler(evt): pass

		self.ReadConfigurationFile()
		self.externalDemos = HuntExternalDemos()        
		
		# Create a Notebook
		self.nb = wx.Notebook(pnl, -1, style=wx.CLIP_CHILDREN)
		imgList = wx.ImageList(16, 16)
		for png in ["overview", "code", "demo"]:
			bmp = images.catalog[png].GetBitmap()
			imgList.Add(bmp)
		self.nb.AssignImageList(imgList)

		self.BuildMenuBar()
		
		self.finddata = wx.FindReplaceData()
		self.finddata.SetFlags(wx.FR_DOWN)

		# Create a TreeCtrl
		leftPanel = wx.Panel(pnl, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)
		self.treeMap = {}
		self.searchItems = {}
		
		self.tree = wxPythonDemoTree(leftPanel)
		
		self.filter = wx.SearchCtrl(leftPanel, style=wx.TE_PROCESS_ENTER)
		self.filter.ShowCancelButton(True)
		self.filter.Bind(wx.EVT_TEXT, self.RecreateTree)
		self.filter.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnSearchCancelBtn)
		self.filter.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)

		searchMenu = wx.Menu()
		item = searchMenu.AppendRadioItem(-1, "Sample Name")
		self.Bind(wx.EVT_MENU, self.OnSearchMenu, item)
		item = searchMenu.AppendRadioItem(-1, "Sample Content")
		self.Bind(wx.EVT_MENU, self.OnSearchMenu, item)
		self.filter.SetMenu(searchMenu)

		self.RecreateTree()
		self.tree.SetExpansionState(self.expansionState)
		self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded)
		self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
		self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnTreeLeftDown)
		
		# Set up a wx.html.HtmlWindow on the Overview Notebook page
		# we put it in a panel first because there seems to be a
		# refresh bug of some sort (wxGTK) when it is directly in
		# the notebook...
		
		if 0:  # the old way
			self.ovr = wx.html.HtmlWindow(self.nb, -1, size=(400, 400))
			self.nb.AddPage(self.ovr, self.overviewText, imageId=0)

		else:  # hopefully I can remove this hacky code soon, see SF bug #216861
			panel = wx.Panel(self.nb, -1, style=wx.CLIP_CHILDREN)
			self.ovr = wx.html.HtmlWindow(panel, -1, size=(400, 400))
			self.nb.AddPage(panel, self.overviewText, imageId=0)

			def OnOvrSize(evt, ovr=self.ovr):
				ovr.SetSize(evt.GetSize())
			panel.Bind(wx.EVT_SIZE, OnOvrSize)
			panel.Bind(wx.EVT_ERASE_BACKGROUND, EmptyHandler)

		if "gtk2" in wx.PlatformInfo:
			self.ovr.SetStandardFonts()
		self.SetOverview(self.overviewText, mainOverview)


		# Set up a log window
		self.log = wx.TextCtrl(pnl, -1,
							  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		if wx.Platform == "__WXMAC__":
			self.log.MacCheckSpelling(False)

		# Set the wxWindows log target to be this textctrl
		#wx.Log_SetActiveTarget(wx.LogTextCtrl(self.log))

		# But instead of the above we want to show how to use our own wx.Log class
		wx.Log_SetActiveTarget(MyLog(self.log))

		# Set up a log window
		self.log2 = wx.TextCtrl(pnl, -1,
							  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		if wx.Platform == "__WXMAC__":
			self.log2.MacCheckSpelling(False)

		# Set the wxWindows log target to be this textctrl
		#wx.Log_SetActiveTarget(wx.LogTextCtrl(self.log))

		# But instead of the above we want to show how to use our own wx.Log class
		wx.Log_SetActiveTarget(MyLog(self.log2))
		
		# Set up a log window
		self.log3 = wx.TextCtrl(pnl, -1,
							  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		if wx.Platform == "__WXMAC__":
			self.log3.MacCheckSpelling(False)

		# Set the wxWindows log target to be this textctrl
		#wx.Log_SetActiveTarget(wx.LogTextCtrl(self.log))

		# But instead of the above we want to show how to use our own wx.Log class
		wx.Log_SetActiveTarget(MyLog(self.log3))		
		# for serious debugging
		#wx.Log_SetActiveTarget(wx.LogStderr())
		#wx.Log_SetTraceMask(wx.TraceMessages)

		self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
		wx.GetApp().Bind(wx.EVT_ACTIVATE_APP, self.OnAppActivate)

		# add the windows to the splitter and split it.
		leftBox = wx.BoxSizer(wx.VERTICAL)
		leftBox.Add(self.tree, 1, wx.EXPAND)
		leftBox.Add(wx.StaticText(leftPanel, label = "Filter Demos:"), 0, wx.TOP|wx.LEFT, 5)
		leftBox.Add(self.filter, 0, wx.EXPAND|wx.ALL, 5)
		if 'wxMac' in wx.PlatformInfo:
			leftBox.Add((5,5))  # Make sure there is room for the focus ring
		leftPanel.SetSizer(leftBox)

		# select initial items
		self.nb.SetSelection(0)
		self.tree.SelectItem(self.root)

		# Load 'Main' module
		self.LoadDemo(self.overviewText)
		self.loaded = True

		# select some other initial module?
		if len(sys.argv) > 1:
			arg = sys.argv[1]
			if arg.endswith('.py'):
				arg = arg[:-3]
			selectedDemo = self.treeMap.get(arg, None)
			if selectedDemo:
				self.tree.SelectItem(selectedDemo)
				self.tree.EnsureVisible(selectedDemo)

		# Use the aui manager to set up everything
		self.mgr.AddPane(self.nb, wx.aui.AuiPaneInfo().CenterPane().Name("Notebook"))
		self.mgr.AddPane(leftPanel,
						 wx.aui.AuiPaneInfo().
						 Left().Layer(2).BestSize((240, -1)).
						 MinSize((160, -1)).
						 Floatable(ALLOW_AUI_FLOATING).FloatingSize((240, 700)).
						 Caption("wxPython Demos").
						 CloseButton(False).
						 Name("DemoTree"))
		self.mgr.AddPane(self.log,
						 wx.aui.AuiPaneInfo().
						 CenterPane().BestSize((-1, 100)).
						 MinSize((-1, 40)).
						 Floatable(ALLOW_AUI_FLOATING).FloatingSize((500, 160)).
						 Caption("Demo Log Messages").
						 CloseButton(True).
						 Name("LogWindow"))	
		#spnl = SQLPanel(self) # wx.Panel(self)
		#self.spnl = spnl
		#self.spnl.Hide()
		# add the windows to the splitter and split it.
		self.midPanel =SQLPanel(self) # wx.Panel(self)
		#midBox = wx.BoxSizer(wx.VERTICAL)
		
		#midBox.Add(self.midPanel,  0, wx.EXPAND|wx.ALL, 5)
		
		#if 'wxMac' in wx.PlatformInfo:
		#	midBox.Add((5,5))  # Make sure there is room for the focus ring
		
		#self.midPanel.SetSizer(midBox)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.midPanel, 1, wx.EXPAND)
		self.midPanel.SetSizer(sizer)
		
		self.mgr.AddPane(self.midPanel,
						 wx.aui.AuiPaneInfo().
						 CenterPane().BestSize((-1, 150)).
						 MinSize((-1, 100)).
						 Floatable(ALLOW_AUI_FLOATING).FloatingSize((500, 160)).
						 Caption("Demo Log Messages2").
						 CloseButton(True).
						 Name("LogWindow2"))
		"""self.mgr.AddPane(self.log3,
						 wx.aui.AuiPaneInfo().
						 Bottom().BestSize((-1, 100)).
						 MinSize((-1, 40)).
						 Floatable(ALLOW_AUI_FLOATING).FloatingSize((500, 160)).
						 Caption("Demo Log Messages2").
						 CloseButton(True).
						 Name("LogWindow3"))"""					 

		self.log.Hide()
		self.auiConfigurations[DEFAULT_PERSPECTIVE] = self.mgr.SavePerspective()
		self.mgr.Update()

		self.mgr.SetFlags(self.mgr.GetFlags() ^ wx.aui.AUI_MGR_TRANSPARENT_DRAG)
		


	def ReadConfigurationFile(self):

		self.auiConfigurations = {}
		self.expansionState = [0, 1]

		config = GetConfig()
		val = config.Read('ExpansionState')
		if val:
			self.expansionState = eval(val)

		val = config.Read('AUIPerspectives')
		if val:
			self.auiConfigurations = eval(val)
		

	def BuildMenuBar(self):

		# Make a File menu
		self.mainmenu = wx.MenuBar()
		menu = wx.Menu()
		item = menu.Append(-1, '&Redirect Output',
						   'Redirect print statements to a window',
						   wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.OnToggleRedirect, item)
 
		exitItem = wx.MenuItem(menu, -1, 'E&xit\tCtrl-Q', 'Get the heck outta here!')
		exitItem.SetBitmap(images.catalog['exit'].GetBitmap())
		menu.AppendItem(exitItem)
		self.Bind(wx.EVT_MENU, self.OnFileExit, exitItem)
		wx.App.SetMacExitMenuItemId(exitItem.GetId())
		self.mainmenu.Append(menu, '&File')

		# Make a Demo menu
		menu = wx.Menu()
		for indx, item in enumerate(_treeList[:-1]):
			menuItem = wx.MenuItem(menu, -1, item[0])
			submenu = wx.Menu()
			for childItem in item[1]:
				mi = submenu.Append(-1, childItem)
				self.Bind(wx.EVT_MENU, self.OnDemoMenu, mi)
			menuItem.SetBitmap(images.catalog[_demoPngs[indx+1]].GetBitmap())
			menuItem.SetSubMenu(submenu)
			menu.AppendItem(menuItem)
		self.mainmenu.Append(menu, '&Demo')

		# Make an Option menu
		# If we've turned off floatable panels then this menu is not needed
		if ALLOW_AUI_FLOATING:
			menu = wx.Menu()
			auiPerspectives = self.auiConfigurations.keys()
			auiPerspectives.sort()
			perspectivesMenu = wx.Menu()
			item = wx.MenuItem(perspectivesMenu, -1, DEFAULT_PERSPECTIVE, "Load startup default perspective", wx.ITEM_RADIO)
			self.Bind(wx.EVT_MENU, self.OnAUIPerspectives, item)
			perspectivesMenu.AppendItem(item)
			for indx, key in enumerate(auiPerspectives):
				if key == DEFAULT_PERSPECTIVE:
					continue
				item = wx.MenuItem(perspectivesMenu, -1, key, "Load user perspective %d"%indx, wx.ITEM_RADIO)
				perspectivesMenu.AppendItem(item)
				self.Bind(wx.EVT_MENU, self.OnAUIPerspectives, item)

			menu.AppendMenu(wx.ID_ANY, "&AUI Perspectives", perspectivesMenu)
			self.perspectives_menu = perspectivesMenu

			item = wx.MenuItem(menu, -1, 'Save Perspective', 'Save AUI perspective')
			item.SetBitmap(images.catalog['saveperspective'].GetBitmap())
			menu.AppendItem(item)
			self.Bind(wx.EVT_MENU, self.OnSavePerspective, item)

			item = wx.MenuItem(menu, -1, 'Delete Perspective', 'Delete AUI perspective')
			item.SetBitmap(images.catalog['deleteperspective'].GetBitmap())
			menu.AppendItem(item)
			self.Bind(wx.EVT_MENU, self.OnDeletePerspective, item)

			menu.AppendSeparator()

			item = wx.MenuItem(menu, -1, 'Restore Tree Expansion', 'Restore the initial tree expansion state')
			item.SetBitmap(images.catalog['expansion'].GetBitmap())
			menu.AppendItem(item)
			self.Bind(wx.EVT_MENU, self.OnTreeExpansion, item)

			self.mainmenu.Append(menu, '&Options')
		
		# Make a Help menu
		menu = wx.Menu()
		findItem = wx.MenuItem(menu, -1, '&Find\tCtrl-F', 'Find in the Demo Code')
		findItem.SetBitmap(images.catalog['find'].GetBitmap())
		if 'wxMac' not in wx.PlatformInfo:
			findNextItem = wx.MenuItem(menu, -1, 'Find &Next\tF3', 'Find Next')
		else:
			findNextItem = wx.MenuItem(menu, -1, 'Find &Next\tCtrl-G', 'Find Next')
		findNextItem.SetBitmap(images.catalog['findnext'].GetBitmap())
		menu.AppendItem(findItem)
		menu.AppendItem(findNextItem)
		menu.AppendSeparator()

		shellItem = wx.MenuItem(menu, -1, 'Open Py&Shell Window\tF5',
								'An interactive interpreter window with the demo app and frame objects in the namesapce')
		shellItem.SetBitmap(images.catalog['pyshell'].GetBitmap())
		menu.AppendItem(shellItem)
		inspToolItem = wx.MenuItem(menu, -1, 'Open &Widget Inspector\tF6',
								   'A tool that lets you browse the live widgets and sizers in an application')
		inspToolItem.SetBitmap(images.catalog['inspect'].GetBitmap())
		menu.AppendItem(inspToolItem)
		if 'wxMac' not in wx.PlatformInfo:
			menu.AppendSeparator()
		helpItem = menu.Append(-1, '&About wxPython Demo', 'wxPython RULES!!!')
		wx.App.SetMacAboutMenuItemId(helpItem.GetId())

		self.Bind(wx.EVT_MENU, self.OnOpenShellWindow, shellItem)
		self.Bind(wx.EVT_MENU, self.OnOpenWidgetInspector, inspToolItem)
		self.Bind(wx.EVT_MENU, self.OnHelpAbout, helpItem)
		self.Bind(wx.EVT_MENU, self.OnHelpFind,  findItem)
		self.Bind(wx.EVT_MENU, self.OnFindNext,  findNextItem)
		self.Bind(wx.EVT_FIND, self.OnFind)
		self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
		self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
		self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFindItems, findItem)
		self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFindItems, findNextItem)
		self.mainmenu.Append(menu, '&Help')
		self.SetMenuBar(self.mainmenu)

		if False:
			# This is another way to set Accelerators, in addition to
			# using the '\t<key>' syntax in the menu items.
			aTable = wx.AcceleratorTable([(wx.ACCEL_ALT,  ord('X'), exitItem.GetId()),
										  (wx.ACCEL_CTRL, ord('H'), helpItem.GetId()),
										  (wx.ACCEL_CTRL, ord('F'), findItem.GetId()),
										  (wx.ACCEL_NORMAL, wx.WXK_F3, findNextItem.GetId()),
										  (wx.ACCEL_NORMAL, wx.WXK_F9, shellItem.GetId()),
										  ])
			self.SetAcceleratorTable(aTable)
			

	#---------------------------------------------    
	def RecreateTree(self, evt=None):
		# Catch the search type (name or content)
		searchMenu = self.filter.GetMenu().GetMenuItems()
		fullSearch = searchMenu[1].IsChecked()
			
		if evt:
			if fullSearch:
				# Do not`scan all the demo files for every char
				# the user input, use wx.EVT_TEXT_ENTER instead
				return

		expansionState = self.tree.GetExpansionState()

		current = None
		item = self.tree.GetSelection()
		if item:
			prnt = self.tree.GetItemParent(item)
			if prnt:
				current = (self.tree.GetItemText(item),
						   self.tree.GetItemText(prnt))
					
		self.tree.Freeze()
		self.tree.DeleteAllItems()
		self.root = self.tree.AddRoot("wxPython Overview")
		self.tree.SetItemImage(self.root, 0)
		self.tree.SetItemPyData(self.root, 0)

		treeFont = self.tree.GetFont()
		catFont = self.tree.GetFont()

		# The old native treectrl on MSW has a bug where it doesn't
		# draw all of the text for an item if the font is larger than
		# the default.  It seems to be clipping the item's label as if
		# it was the size of the same label in the default font.
		if 'wxMSW' not in wx.PlatformInfo or wx.GetApp().GetComCtl32Version() >= 600:
			treeFont.SetPointSize(treeFont.GetPointSize()+2)
			treeFont.SetWeight(wx.BOLD)
			catFont.SetWeight(wx.BOLD)
			
		self.tree.SetItemFont(self.root, treeFont)
		
		firstChild = None
		selectItem = None
		filter = self.filter.GetValue()
		count = 0
		
		for category, items in _treeList:
			count += 1
			if filter:
				if fullSearch:
					items = self.searchItems[category]
				else:
					items = [item for item in items if filter.lower() in item.lower()]
			if items:
				child = self.tree.AppendItem(self.root, category, image=count)
				self.tree.SetItemFont(child, catFont)
				self.tree.SetItemPyData(child, count)
				if not firstChild: firstChild = child
				for childItem in items:
					image = count
					if DoesModifiedExist(childItem):
						image = len(_demoPngs)
					theDemo = self.tree.AppendItem(child, childItem, image=image)
					self.tree.SetItemPyData(theDemo, count)
					self.treeMap[childItem] = theDemo
					if current and (childItem, category) == current:
						selectItem = theDemo
						
					
		self.tree.Expand(self.root)
		if firstChild:
			self.tree.Expand(firstChild)
		if filter:
			self.tree.ExpandAll()
		elif expansionState:
			self.tree.SetExpansionState(expansionState)
		if selectItem:
			self.skipLoad = True
			self.tree.SelectItem(selectItem)
			self.skipLoad = False
		
		self.tree.Thaw()
		self.searchItems = {}


	def OnSearchMenu(self, event):

		# Catch the search type (name or content)
		searchMenu = self.filter.GetMenu().GetMenuItems()
		fullSearch = searchMenu[1].IsChecked()
		
		if fullSearch:
			self.OnSearch()
		else:
			self.RecreateTree()
			

	def OnSearch(self, event=None):

		value = self.filter.GetValue()
		if not value:
			self.RecreateTree()
			return

		wx.BeginBusyCursor()
		
		for category, items in _treeList:
			self.searchItems[category] = []
			for childItem in items:
				if SearchDemo(childItem, value):
					self.searchItems[category].append(childItem)

		wx.EndBusyCursor()
		self.RecreateTree()            


	def OnSearchCancelBtn(self, event):
		self.filter.SetValue('')
		self.OnSearch()
		

	def SetTreeModified(self, modified):
		item = self.tree.GetSelection()
		if modified:
			image = len(_demoPngs)
		else:
			image = self.tree.GetItemPyData(item)
		self.tree.SetItemImage(item, image)
		
		
	def WriteText(self, text):
		if text[-1:] == '\n':
			text = text[:-1]
		wx.LogMessage(text)

	def write(self, txt):
		self.WriteText(txt)

	#---------------------------------------------
	def OnItemExpanded(self, event):
		item = event.GetItem()
		wx.LogMessage("OnItemExpanded: %s" % self.tree.GetItemText(item))
		event.Skip()

	#---------------------------------------------
	def OnItemCollapsed(self, event):
		item = event.GetItem()
		wx.LogMessage("OnItemCollapsed: %s" % self.tree.GetItemText(item))
		event.Skip()

	#---------------------------------------------
	def OnTreeLeftDown(self, event):
		# reset the overview text if the tree item is clicked on again
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		if item == self.tree.GetSelection():
			self.SetOverview(self.tree.GetItemText(item)+" Overview", self.curOverview)
		event.Skip()

	#---------------------------------------------
	def OnSelChanged(self, event):
		if self.dying or not self.loaded or self.skipLoad:
			return

		item = event.GetItem()
		itemText = self.tree.GetItemText(item)
		self.LoadDemo(itemText)

	#---------------------------------------------
	def LoadDemo(self, demoName):
		try:
			wx.BeginBusyCursor()
			self.pnl.Freeze()
			
			os.chdir(self.cwd)
			self.ShutdownDemoModule()
			print demoName, __name__
			if demoName == self.overviewText:
				# User selected the "wxPython Overview" node
				# ie: _this_ module
				# Changing the main window at runtime not yet supported...
				self.demoModules = DemoModules(__name__)
				self.SetOverview(self.overviewText, mainOverview)
				self.LoadDemoSource()
				self.UpdateNotebook(0)
			else:
				if os.path.exists(GetOriginalFilename(demoName)):
					wx.LogMessage("Loading demo %s.py..." % demoName)
					self.demoModules = DemoModules(demoName)
					self.LoadDemoSource()

				else:

					package, overview = LookForExternals(self.externalDemos, demoName)

					if package:
						wx.LogMessage("Loading demo %s.py..." % ("%s/%s"%(package, demoName)))
						self.demoModules = DemoModules("%s/%s"%(package, demoName))
						self.LoadDemoSource()
					elif overview:
						self.SetOverview(demoName, overview)
						self.codePage = None
						self.UpdateNotebook(0)
					else:
						self.SetOverview("wxPython", mainOverview)
						self.codePage = None
						self.UpdateNotebook(0)

		finally:
			wx.EndBusyCursor()
			self.pnl.Thaw()

	#---------------------------------------------
	def LoadDemoSource(self):
		self.codePage = None
		self.codePage = DemoCodePanel(self.nb, self)
		self.codePage.LoadDemo(self.demoModules)
		
	#---------------------------------------------
	def RunModule(self):
		"""Runs the active module"""

		module = self.demoModules.GetActive()
		self.ShutdownDemoModule()
		overviewText = ""
		
		# o The RunTest() for all samples must now return a window that can
		#   be palced in a tab in the main notebook.
		# o If an error occurs (or has occurred before) an error tab is created.
		
		if module is not None:
			wx.LogMessage("Running demo module...")
			if hasattr(module, "overview"):
				overviewText = module.overview

			try:
				self.demoPage = module.runTest(self, self.nb, self)
			except:
				self.demoPage = DemoErrorPanel(self.nb, self.codePage,
											   DemoError(sys.exc_info()), self)

			bg = self.nb.GetThemeBackgroundColour()
			if bg:
				self.demoPage.SetBackgroundColour(bg)

			assert self.demoPage is not None, "runTest must return a window!"
			
		else:
			# There was a previous error in compiling or exec-ing
			self.demoPage = DemoErrorPanel(self.nb, self.codePage,
										   self.demoModules.GetErrorInfo(), self)
			
		self.SetOverview(self.demoModules.name + " Overview", overviewText)

		if self.firstTime:
			# change to the demo page the first time a module is run
			self.UpdateNotebook(2)
			self.firstTime = False
		else:
			# otherwise just stay on the same tab in case the user has changed to another one
			self.UpdateNotebook()

	#---------------------------------------------
	def ShutdownDemoModule(self):
		if self.demoPage:
			# inform the window that it's time to quit if it cares
			if hasattr(self.demoPage, "ShutdownDemo"):
				self.demoPage.ShutdownDemo()
			wx.YieldIfNeeded() # in case the page has pending events
			self.demoPage = None
			
	#---------------------------------------------
	def UpdateNotebook(self, select = -1):
		nb = self.nb
		debug = False
		self.pnl.Freeze()
		
		def UpdatePage(page, pageText):
			pageExists = False
			pagePos = -1
			for i in range(nb.GetPageCount()):
				if nb.GetPageText(i) == pageText:
					pageExists = True
					pagePos = i
					break
				
			if page:
				if not pageExists:
					# Add a new page
					nb.AddPage(page, pageText, imageId=nb.GetPageCount())
					if debug: wx.LogMessage("DBG: ADDED %s" % pageText)
				else:
					if nb.GetPage(pagePos) != page:
						# Reload an existing page
						nb.DeletePage(pagePos)
						nb.InsertPage(pagePos, page, pageText, imageId=pagePos)
						if debug: wx.LogMessage("DBG: RELOADED %s" % pageText)
					else:
						# Excellent! No redraw/flicker
						if debug: wx.LogMessage("DBG: SAVED from reloading %s" % pageText)
			elif pageExists:
				# Delete a page
				nb.DeletePage(pagePos)
				if debug: wx.LogMessage("DBG: DELETED %s" % pageText)
			else:
				if debug: wx.LogMessage("DBG: STILL GONE - %s" % pageText)
				
		if select == -1:
			select = nb.GetSelection()

		UpdatePage(self.codePage, "Demo Code")
		UpdatePage(self.demoPage, "Demo")

		if select >= 0 and select < nb.GetPageCount():
			nb.SetSelection(select)

		self.pnl.Thaw()
		
	#---------------------------------------------
	def SetOverview(self, name, text):
		self.curOverview = text
		lead = text[:6]
		if lead != '<html>' and lead != '<HTML>':
			text = '<br>'.join(text.split('\n'))
		if wx.USE_UNICODE:
			text = text.decode('iso8859_1')  
		self.ovr.SetPage(text)
		self.nb.SetPageText(0, os.path.split(name)[1])

	#---------------------------------------------
	# Menu methods
	def OnFileExit(self, *event):
		self.Close()

	def OnToggleRedirect(self, event):
		app = wx.GetApp()
		if event.Checked():
			app.RedirectStdio()
			print "Print statements and other standard output will now be directed to this window."
		else:
			app.RestoreStdio()
			print "Print statements and other standard output will now be sent to the usual location."


	def OnAUIPerspectives(self, event):
		perspective = self.perspectives_menu.GetLabel(event.GetId())
		self.mgr.LoadPerspective(self.auiConfigurations[perspective])
		self.mgr.Update()


	def OnSavePerspective(self, event):
		dlg = wx.TextEntryDialog(self, "Enter a name for the new perspective:", "AUI Configuration")
		
		dlg.SetValue(("Perspective %d")%(len(self.auiConfigurations)+1))
		if dlg.ShowModal() != wx.ID_OK:
			return

		perspectiveName = dlg.GetValue()
		menuItems = self.perspectives_menu.GetMenuItems()
		for item in menuItems:
			if item.GetLabel() == perspectiveName:
				wx.MessageBox("The selected perspective name:\n\n%s\n\nAlready exists."%perspectiveName,
							  "Error", style=wx.ICON_ERROR)
				return
				
		item = wx.MenuItem(self.perspectives_menu, -1, dlg.GetValue(),
						   "Load user perspective %d"%(len(self.auiConfigurations)+1),
						   wx.ITEM_RADIO)
		self.Bind(wx.EVT_MENU, self.OnAUIPerspectives, item)                
		self.perspectives_menu.AppendItem(item)
		item.Check(True)
		self.auiConfigurations.update({dlg.GetValue(): self.mgr.SavePerspective()})


	def OnDeletePerspective(self, event):
		menuItems = self.perspectives_menu.GetMenuItems()[1:]
		lst = []
		loadDefault = False
		
		for item in menuItems:
			lst.append(item.GetLabel())
			
		dlg = wx.MultiChoiceDialog(self, 
								   "Please select the perspectives\nyou would like to delete:",
								   "Delete AUI Perspectives", lst)

		if dlg.ShowModal() == wx.ID_OK:
			selections = dlg.GetSelections()
			strings = [lst[x] for x in selections]
			for sel in strings:
				self.auiConfigurations.pop(sel)
				item = menuItems[lst.index(sel)]
				if item.IsChecked():
					loadDefault = True
					self.perspectives_menu.GetMenuItems()[0].Check(True)
				self.perspectives_menu.DeleteItem(item)
				lst.remove(sel)

		if loadDefault:
			self.mgr.LoadPerspective(self.auiConfigurations[DEFAULT_PERSPECTIVE])
			self.mgr.Update()


	def OnTreeExpansion(self, event):
		self.tree.SetExpansionState(self.expansionState)
		
 
	def OnHelpAbout(self, event):
		from About import MyAboutBox
		about = MyAboutBox(self)
		about.ShowModal()
		about.Destroy()

	def OnHelpFind(self, event):
		if self.finddlg != None:
			return
		
		self.nb.SetSelection(1)
		self.finddlg = wx.FindReplaceDialog(self, self.finddata, "Find",
						wx.FR_NOMATCHCASE | wx.FR_NOWHOLEWORD)
		self.finddlg.Show(True)


	def OnUpdateFindItems(self, evt):
		evt.Enable(self.finddlg == None)


	def OnFind(self, event):
		editor = self.codePage.editor
		self.nb.SetSelection(1)
		end = editor.GetLastPosition()
		textstring = editor.GetRange(0, end).lower()
		findstring = self.finddata.GetFindString().lower()
		backward = not (self.finddata.GetFlags() & wx.FR_DOWN)
		if backward:
			start = editor.GetSelection()[0]
			loc = textstring.rfind(findstring, 0, start)
		else:
			start = editor.GetSelection()[1]
			loc = textstring.find(findstring, start)
		if loc == -1 and start != 0:
			# string not found, start at beginning
			if backward:
				start = end
				loc = textstring.rfind(findstring, 0, start)
			else:
				start = 0
				loc = textstring.find(findstring, start)
		if loc == -1:
			dlg = wx.MessageDialog(self, 'Find String Not Found',
						  'Find String Not Found in Demo File',
						  wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
		if self.finddlg:
			if loc == -1:
				self.finddlg.SetFocus()
				return
			else:
				self.finddlg.Destroy()
				self.finddlg = None
		editor.ShowPosition(loc)
		editor.SetSelection(loc, loc + len(findstring))



	def OnFindNext(self, event):
		if self.finddata.GetFindString():
			self.OnFind(event)
		else:
			self.OnHelpFind(event)

	def OnFindClose(self, event):
		event.GetDialog().Destroy()
		self.finddlg = None


	def OnOpenShellWindow(self, evt):
		if self.shell:
			# if it already exists then just make sure it's visible
			s = self.shell
			if s.IsIconized():
				s.Iconize(False)
			s.Raise()
		else:
			# Make a PyShell window
			from wx import py
			namespace = { 'wx'    : wx,
						  'app'   : wx.GetApp(),
						  'frame' : self,
						  }
			self.shell = py.shell.ShellFrame(None, locals=namespace)
			self.shell.SetSize((640,480))
			self.shell.Show()

			# Hook the close event of the main frame window so that we
			# close the shell at the same time if it still exists            
			def CloseShell(evt):
				if self.shell:
					self.shell.Close()
				evt.Skip()
			self.Bind(wx.EVT_CLOSE, CloseShell)


	def OnOpenWidgetInspector(self, evt):
		# Activate the widget inspection tool
		from wx.lib.inspection import InspectionTool
		if not InspectionTool().initialized:
			InspectionTool().Init()

		# Find a widget to be selected in the tree.  Use either the
		# one under the cursor, if any, or this frame.
		wnd = wx.FindWindowAtPointer()
		if not wnd:
			wnd = self
		InspectionTool().Show(wnd, True)

		
	#---------------------------------------------
	def OnCloseWindow(self, event):
		self.dying = True
		self.demoPage = None
		self.codePage = None
		self.mainmenu = None
		if self.tbicon is not None:
			self.tbicon.Destroy()

		config = GetConfig()
		config.Write('ExpansionState', str(self.tree.GetExpansionState()))
		config.Write('AUIPerspectives', str(self.auiConfigurations))
		config.Flush()

		self.Destroy()


	#---------------------------------------------
	def OnIdle(self, event):
		if self.otherWin:
			self.otherWin.Raise()
			self.demoPage = self.otherWin
			self.otherWin = None


	#---------------------------------------------
	def ShowTip(self):
		config = GetConfig()
		showTipText = config.Read("tips")
		if showTipText:
			showTip, index = eval(showTipText)
		else:
			showTip, index = (1, 0)
			
		if showTip:
			tp = wx.CreateFileTipProvider(opj("data/tips.txt"), index)
			##tp = MyTP(0)
			showTip = wx.ShowTip(self, tp)
			index = tp.GetCurrentTip()
			config.Write("tips", str( (showTip, index) ))
			config.Flush()

	#---------------------------------------------
	def OnDemoMenu(self, event):
		try:
			selectedDemo = self.treeMap[self.mainmenu.GetLabel(event.GetId())]
		except:
			selectedDemo = None
		if selectedDemo:
			self.tree.SelectItem(selectedDemo)
			self.tree.EnsureVisible(selectedDemo)



	#---------------------------------------------
	def OnIconfiy(self, evt):
		wx.LogMessage("OnIconfiy: %s" % evt.Iconized())
		evt.Skip()

	#---------------------------------------------
	def OnMaximize(self, evt):
		print 'onmax'
		#wx.LogMessage("OnMaximize")
		evt.Skip()

	#---------------------------------------------
	def OnActivate(self, evt):
		wx.LogMessage("OnActivate: %s" % evt.GetActive())
		evt.Skip()

	#---------------------------------------------
	def OnAppActivate(self, evt):
		wx.LogMessage("OnAppActivate: %s" % evt.GetActive())
		evt.Skip()

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

class MySplashScreen(wx.SplashScreen):
	def __init__(self):
		bmp = wx.Image(opj("bitmaps/splash.png")).ConvertToBitmap()
		wx.SplashScreen.__init__(self, bmp,
								 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
								 5000, None, -1)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.fc = wx.FutureCall(2000, self.ShowMain)


	def OnClose(self, evt):
		# Make sure the default handler runs too so this window gets
		# destroyed
		evt.Skip()
		self.Hide()
		
		# if the timer is still running then go ahead and show the
		# main frame now
		if self.fc.IsRunning():
			self.fc.Stop()
			self.ShowMain()


	def ShowMain(self):
		frame = wxPythonDemo(None, "wxPython: (A Demonstration)")
		frame.Show()
		if self.fc.IsRunning():
			self.Raise()
		wx.CallAfter(frame.ShowTip)




#---------------------------------------------------------------------------

from wx.lib.mixins.treemixin import ExpansionState
if USE_CUSTOMTREECTRL:
	import wx.lib.customtreectrl as CT
	TreeBaseClass = CT.CustomTreeCtrl
else:
	TreeBaseClass = wx.TreeCtrl
	

class wxPythonDemoTree(ExpansionState, TreeBaseClass):
	def __init__(self, parent):
		TreeBaseClass.__init__(self, parent, style=wx.TR_DEFAULT_STYLE|
							   wx.TR_HAS_VARIABLE_ROW_HEIGHT)
		self.BuildTreeImageList()
		if USE_CUSTOMTREECTRL:
			self.SetSpacing(10)
			self.SetWindowStyle(self.GetWindowStyle() & ~wx.TR_LINES_AT_ROOT)

	def AppendItem(self, parent, text, image=-1, wnd=None):
		if USE_CUSTOMTREECTRL:
			item = TreeBaseClass.AppendItem(self, parent, text, image=image, wnd=wnd)
		else:
			item = TreeBaseClass.AppendItem(self, parent, text, image=image)
		return item
			
	def BuildTreeImageList(self):
		imgList = wx.ImageList(16, 16)
		for png in _demoPngs:
			imgList.Add(images.catalog[png].GetBitmap())
			
		# add the image for modified demos.
		imgList.Add(images.catalog["custom"].GetBitmap())

		self.AssignImageList(imgList)


	def GetItemIdentity(self, item):
		return self.GetPyData(item)


#---------------------------------------------------------------------------

class MyApp(wx.App):
	def OnInit(self):

		# Check runtime version
		if version.VERSION_STRING != wx.VERSION_STRING:
			wx.MessageBox(caption="Warning",
						  message="You're using version %s of wxPython, but this copy of the demo was written for version %s.\n"
						  "There may be some version incompatibilities..."
						  % (wx.VERSION_STRING, version.VERSION_STRING))

		# Now that we've warned the user about possibile problems,
		# lets import images
		import images as i
		global images
		images = i
		
		# Create and show the splash screen.  It will then create and show
		# the main frame when it is time to do so.
		wx.SystemOptions.SetOptionInt("mac.window-plain-transition", 1)
		self.SetAppName("wxPyDemo")
		
		# For debugging
		#self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

		# Normally when using a SplashScreen you would create it, show
		# it and then continue on with the applicaiton's
		# initialization, finally creating and showing the main
		# application window(s).  In this case we have nothing else to
		# do so we'll delay showing the main frame until later (see
		# ShowMain above) so the users can see the SplashScreen effect.        
		splash = MySplashScreen()
		splash.Show()

		return True



#---------------------------------------------------------------------------

def main():
	try:
		demoPath = os.path.dirname(__file__)
		os.chdir(demoPath)
	except:
		pass
	app = MyApp(False)
	app.MainLoop()

#---------------------------------------------------------------------------


mainOverview = """<html><body>
<h2>wxPython</h2>

<p> wxPython is a <b>GUI toolkit</b> for the Python programming
language.  It allows Python programmers to create programs with a
robust, highly functional graphical user interface, simply and easily.
It is implemented as a Python extension module (native code) that
wraps the popular wxWindows cross platform GUI library, which is
written in C++.

<p> Like Python and wxWindows, wxPython is <b>Open Source</b> which
means that it is free for anyone to use and the source code is
available for anyone to look at and modify.  Or anyone can contribute
fixes or enhancements to the project.

<p> wxPython is a <b>cross-platform</b> toolkit.  This means that the
same program will run on multiple platforms without modification.
Currently supported platforms are 32-bit Microsoft Windows, most Unix
or unix-like systems, and Macintosh OS X. Since the language is
Python, wxPython programs are <b>simple, easy</b> to write and easy to
understand.

<p> <b>This demo</b> is not only a collection of test cases for
wxPython, but is also designed to help you learn about and how to use
wxPython.  Each sample is listed in the tree control on the left.
When a sample is selected in the tree then a module is loaded and run
(usually in a tab of this notebook,) and the source code of the module
is loaded in another tab for you to browse and learn from.

"""


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

if __name__ == '__main__':
	__name__ = 'Main'
	main()

#----------------------------------------------------------------------------







