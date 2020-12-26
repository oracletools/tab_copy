
import  sql_keyword as keyword

if 0:
	import wxversion
	import wxversion as wv
	wv.select("3.0")
import wx
import  wx.stc  as  stc

import  images
#from wx.lib.pubsub import Publisher
from tc_lib import send

#----------------------------------------------------------------------

demoText = """\
## This version of the editor has been set up to edit SQL source
## code.  Here is a copy of wxPython/demo/Main.py to play with.


"""

#----------------------------------------------------------------------


if wx.Platform == '__WXMSW__':
	faces = { 'times': 'Times New Roman',
			  'mono' : 'Courier New',
			  'helv' : 'Arial',
			  'other': 'Comic Sans MS',
			  'size' : 10,
			  'size2': 8,
			 }
elif wx.Platform == '__WXMAC__':
	faces = { 'times': 'Times New Roman',
			  'mono' : 'Monaco',
			  'helv' : 'Arial',
			  'other': 'Comic Sans MS',
			  'size' : 12,
			  'size2': 10,
			 }
else:
	faces = { 'times': 'Times',
			  'mono' : 'Courier',
			  'helv' : 'Helvetica',
			  'other': 'new century schoolbook',
			  'size' : 12,
			  'size2': 10,
			 }


#----------------------------------------------------------------------

class SqlSTC(stc.StyledTextCtrl):

	fold_symbols = 2
	
	def __init__(self, parent, ID,
				 pos=wx.DefaultPosition, size=wx.DefaultSize,
				 style=0, ignore_change=True):
		stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

		self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
		self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

		self.SetLexer(stc.STC_LEX_SQL)
		self.SetKeyWords(0, " ".join(keyword.kwlist))

		self.SetProperty("fold", "1")
		self.SetProperty("tab.timmy.whinge.level", "1")
		self.SetMargins(0,0)
		self.changed=False
		self.ignore_change=ignore_change #ignore change on opening existing files
		self.ID=ID
		print 'SqlSTC intit parent=', parent
		self.SetViewWhiteSpace(False)
		#self.SetBufferedDraw(False)
		#self.SetViewEOL(True)
		#self.SetEOLMode(stc.STC_EOL_CRLF)
		#self.SetUseAntiAliasing(True)
		
		self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
		self.SetEdgeColumn(78)

		# Setup a margin to hold fold markers
		#self.SetFoldFlags(16)  ###  WHAT IS THIS VALUE?  WHAT ARE THE OTHER FLAGS?  DOES IT MATTER?
		self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
		self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
		self.SetMarginSensitive(2, True)
		self.SetMarginWidth(2, 12)

		if self.fold_symbols == 0:
			# Arrow pointing right for contracted folders, arrow pointing down for expanded
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_ARROWDOWN, "black", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_ARROW, "black", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "black", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "black", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY,     "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY,     "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY,     "white", "black")
			
		elif self.fold_symbols == 1:
			# Plus for contracted folders, minus for expanded
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_MINUS, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_PLUS,  "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_EMPTY, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_EMPTY, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_EMPTY, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")

		elif self.fold_symbols == 2:
			# Like a flattened tree control using circular headers and curved joins
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_CIRCLEMINUS,          "white", "#404040")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_CIRCLEPLUS,           "white", "#404040")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,                "white", "#404040")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNERCURVE,         "white", "#404040")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_CIRCLEPLUSCONNECTED,  "white", "#404040")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE,         "white", "#404040")

		elif self.fold_symbols == 3:
			# Like a flattened tree control using square headers
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS,          "white", "#808080")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,           "white", "#808080")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,             "white", "#808080")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,           "white", "#808080")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
			self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,           "white", "#808080")


		self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
		self.Bind(stc.EVT_STC_CHANGE, self.OnChangeText)
		self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)

		# Make some styles,  The lexer defines what each style is used for, we
		# just have to define what each style looks like.  This set is adapted from
		# Scintilla sample property files.

		# Global default styles for all languages
		self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
		self.StyleClearAll()  # Reset all to be like the default

		# Global default styles for all languages
		self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
		self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
		self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
		self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
		self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

		# SQL styles
		# Default 
		self.StyleSetSpec(stc.STC_SQL_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
		# Comments
		self.StyleSetSpec(stc.STC_SQL_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
		# Number
		self.StyleSetSpec(stc.STC_SQL_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
		# String
		self.StyleSetSpec(stc.STC_SQL_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
		# Single quoted string
		self.StyleSetSpec(stc.STC_SQL_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
		# Keyword
		self.StyleSetSpec(stc.STC_SQL_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
		# Triple quotes
		#self.StyleSetSpec(stc.STC_SQL_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
		# Triple double quotes
		#self.StyleSetSpec(stc.STC_SQL_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
		# Class name definition
		#self.StyleSetSpec(stc.STC_SQL_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
		# Function or method name definition
		#self.StyleSetSpec(stc.STC_SQL_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
		# Operators
		#self.StyleSetSpec(stc.STC_SQL_OPERATOR, "bold,size:%(size)d" % faces)
		self.StyleSetSpec(wx.stc.STC_SQL_OPERATOR, 'fore:#800000,bold')
		# Identifiers
		self.StyleSetSpec(stc.STC_SQL_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
		# Comment-blocks
		#self.StyleSetSpec(stc.STC_SQL_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
		# End of line where string is not closed
		#self.StyleSetSpec(stc.STC_SQL_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

		self.SetCaretForeground("BLUE")


		# register some images for use in the AutoComplete box.
		self.RegisterImage(1, images.Smiles.GetBitmap())
		self.RegisterImage(2, 
			wx.ArtProvider.GetBitmap(wx.ART_NEW, size=(16,16)))
		self.RegisterImage(3, 
			wx.ArtProvider.GetBitmap(wx.ART_COPY, size=(16,16)))


	def OnKeyPressed(self, event):
		self.ignore_change=False
		if self.CallTipActive():
			self.CallTipCancel()
		key = event.GetKeyCode()

		if key == 32 and event.ControlDown():
			pos = self.GetCurrentPos()

			# Tips
			if event.ShiftDown():
				self.CallTipSetBackground("yellow")
				self.CallTipShow(pos, 'lots of of text: blah, blah, blah\n\n'
								 'show some suff, maybe parameters..\n\n'
								 'fubar(param1, param2)')
			# Code completion
			else:
				#lst = []
				#for x in range(50000):
				#    lst.append('%05d' % x)
				#st = " ".join(lst)
				#print len(st)
				#self.AutoCompShow(0, st)

				kw = keyword.kwlist[:]
				kw.append("from")
				kw.append("select")
				kw.append("where")
				kw.append("between")
				kw.append("zzbaaaa?2")
				kw.append("this_is_a_longer_value")
				#kw.append("this_is_a_much_much_much_much_much_much_much_longer_value")

				kw.sort()  # SQL sorts are case sensitive
				self.AutoCompSetIgnoreCase(False)  # so this needs to match

				# Images are specified with a appended "?type"
				for i in range(len(kw)):
					if kw[i] in keyword.kwlist:
						kw[i] = kw[i] + "?1"

				self.AutoCompShow(0, " ".join(kw))
		else:
			event.Skip()
	def OnChangeText(self, evt):
		# status on text thange
		print 'OnChangeText', self.changed, self.ignore_change
		if not self.changed:
			if not self.ignore_change:
				self.changed=True		
				print 'sending "star_tab_name"' 
				#Publisher().sendMessage( "star_tab_name", (self.ID) )
				send("star_tab_name", (self.ID))
		#self.ignore_change=False

	def OnUpdateUI(self, evt):
		# check for matching braces
		#self.changed=True
		braceAtCaret = -1
		braceOpposite = -1
		charBefore = None
		caretPos = self.GetCurrentPos()

		if caretPos > 0:
			charBefore = self.GetCharAt(caretPos - 1)
			styleBefore = self.GetStyleAt(caretPos - 1)

		# check before
		if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
			braceAtCaret = caretPos - 1

		# check after
		if braceAtCaret < 0:
			charAfter = self.GetCharAt(caretPos)
			styleAfter = self.GetStyleAt(caretPos)

			if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
				braceAtCaret = caretPos

		if braceAtCaret >= 0:
			braceOpposite = self.BraceMatch(braceAtCaret)

		if braceAtCaret != -1  and braceOpposite == -1:
			self.BraceBadLight(braceAtCaret)
		else:
			self.BraceHighlight(braceAtCaret, braceOpposite)
			#pt = self.PointFromPosition(braceOpposite)
			#self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
			#print pt
			#self.Refresh(False)


	def OnMarginClick(self, evt):
		# fold and unfold as needed
		if evt.GetMargin() == 2:
			if evt.GetShift() and evt.GetControl():
				self.FoldAll()
			else:
				lineClicked = self.LineFromPosition(evt.GetPosition())

				if self.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
					if evt.GetShift():
						self.SetFoldExpanded(lineClicked, True)
						self.Expand(lineClicked, True, True, 1)
					elif evt.GetControl():
						if self.GetFoldExpanded(lineClicked):
							self.SetFoldExpanded(lineClicked, False)
							self.Expand(lineClicked, False, True, 0)
						else:
							self.SetFoldExpanded(lineClicked, True)
							self.Expand(lineClicked, True, True, 100)
					else:
						self.ToggleFold(lineClicked)


	def FoldAll(self):
		lineCount = self.GetLineCount()
		expanding = True

		# find out if we are folding or unfolding
		for lineNum in range(lineCount):
			if self.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
				expanding = not self.GetFoldExpanded(lineNum)
				break

		lineNum = 0

		while lineNum < lineCount:
			level = self.GetFoldLevel(lineNum)
			if level & stc.STC_FOLDLEVELHEADERFLAG and \
			   (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

				if expanding:
					self.SetFoldExpanded(lineNum, True)
					lineNum = self.Expand(lineNum, True)
					lineNum = lineNum - 1
				else:
					lastChild = self.GetLastChild(lineNum, -1)
					self.SetFoldExpanded(lineNum, False)

					if lastChild > lineNum:
						self.HideLines(lineNum+1, lastChild)

			lineNum = lineNum + 1



	def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
		lastChild = self.GetLastChild(line, level)
		line = line + 1

		while line <= lastChild:
			if force:
				if visLevels > 0:
					self.ShowLines(line, line)
				else:
					self.HideLines(line, line)
			else:
				if doExpand:
					self.ShowLines(line, line)

			if level == -1:
				level = self.GetFoldLevel(line)

			if level & stc.STC_FOLDLEVELHEADERFLAG:
				if force:
					if visLevels > 1:
						self.SetFoldExpanded(line, True)
					else:
						self.SetFoldExpanded(line, False)

					line = self.Expand(line, doExpand, force, visLevels-1)

				else:
					if doExpand and self.GetFoldExpanded(line):
						line = self.Expand(line, True, force, visLevels-1)
					else:
						line = self.Expand(line, False, force, visLevels-1)
			else:
				line = line + 1

		return line


#----------------------------------------------------------------------

_USE_PANEL = 1

def runTest(frame, nb, log):
	if not _USE_PANEL:
		ed = p = SqlSTC(nb, -1)
	else:
		p = wx.Panel(nb, -1, style = wx.NO_FULL_REPAINT_ON_RESIZE)
		ed = SqlSTC(p, -1)
		s = wx.BoxSizer(wx.HORIZONTAL)
		s.Add(ed, 1, wx.EXPAND)
		p.SetSizer(s)
		p.SetAutoLayout(True)


	ed.SetText(demoText + open('Main.py').read())
	ed.EmptyUndoBuffer()
	ed.Colourise(0, -1)

	# line numbers in the margin
	ed.SetMarginType(1, stc.STC_MARGIN_NUMBER)
	ed.SetMarginWidth(1, 25)

	return p



#----------------------------------------------------------------------


overview = """\
<html><body>
Once again, no docs yet.  <b>Sorry.</b>  But <a href="data/stc.h.html">this</a>
and <a href="http://www.scintilla.org/ScintillaDoc.html">this</a> should
be helpful.
</body><html>
"""


if __name__ == '__main__':
	import sys,os
	import run
	run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])





#----------------------------------------------------------------------
#----------------------------------------------------------------------

