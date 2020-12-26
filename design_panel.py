if 0:
	import wxversion
	import wxversion as wv
	wv.select("3.0")
import wx
import wx.lib.agw.flatnotebook as fnb
from tc_lib import *
from wx.lib.mixins.listctrl import TextEditMixin
from editor import TacoCodeEditor, TacoTextEditor
from tc_init import *
#print t_TABLE_LIST
#sys.exit(0)
#from wx.lib.pubsub import Publisher
from tc_lib import sub
import os, sys
from threading import Thread
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
import xml.dom.minidom
from xml.dom.minidom import Node, Document
from common_utils import *
import datetime
from editor import TacoSqlEditor
from pprint import pprint
import wx.lib.mixins.listctrl as listmix
from collections import OrderedDict
import images
import win32con, win32file
import pywintypes	
#from tc_init import *
import time
import wx.lib.agw.hyperlink as hl



from cache_lib import ifCacheExists, loadCache, writeToCache, readFromCache, gCache
from generic_copy_panel import GenericCopyPanel


use_cache=0
update_cache=1
gTableCache='global.tables'
gTableColumnsCache='global.tables.columns'
gDatabaseCache='global.databases'
gConfigCache='global.config'
gOwnersCache='global.owners'
gEnvironmentCache= 'global.environment'
gConnectListCache='global.connections'
branchingList='ConnectList' #list where we define if it's a db or a host connection
dBtn='N/A'
bLevel=100
iLevel=200
DIR_EXCLUDES = set(['.', '..'])
MASK = win32con.FILE_ATTRIBUTE_DIRECTORY | win32con.FILE_ATTRIBUTE_SYSTEM
REQUIRED = win32con.FILE_ATTRIBUTE_DIRECTORY
FindFilesW = win32file.FindFilesW
########################################################################
class DesignPanelManager(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self, parent,frame,pos,pos_from, pos_to, items_from,item_key):
		""""""

		wx.Panel.__init__(self, parent,  id=wx.NewId())

		self.pos,self.pos_from, self.pos_to, self.items_from, self.item_key= (pos,pos_from, pos_to, items_from,item_key)
		#self.panel_pos=panel_pos

		self.parent=parent
		self.frame=frame
		#print frame
		print frame.getCurrentList(pos_from)
		print frame.getCurrentList(pos_to) 
		#sys.exit(0)
		self.nb = fnb.FlatNotebook(self, -1, agwStyle=fnb.FNB_COLOURFUL_TABS|fnb.FNB_BACKGROUND_GRADIENT|fnb.FNB_SMART_TABS |fnb.FNB_DROPDOWN_TABS_LIST) #|fnb.FNB_DCLICK_CLOSES_TABS|fnb.FNB_X_ON_TAB|fnb.FNB_X|fnb.FNB_TAB_X|fnb.FNB_BACKGROUND_GRADIENT|fnb.FNB_BTN_NONE|fnb.FNB_BTN_PRESSED|fnb.FNB_COLOURFUL_TABS|fnb.FNB_BOTTOM|fnb.FNB_SMART_TABS|fnb.FNB_DROPDOWN_TABS_LIST|fnb.FNB_DROP_DOWN_ARROW|fnb.FNB_BTN_HOVER|fnb.FNB_NO_X_BUTTON) #|fnb.FNB_HIDE_ON_SINGLE_TAB)
		#start=DesignPanel(self,pos,self.panel_pos)
		if not items_from:
			self.items_from=[[15, 15, 'COLUMN_15', 'VARCHAR2', '50', 'column', '15', '02/06/2014 15:35:34']]
		self.appendPanel(pos_from, pos_to, items_from,item_key)
		if 0:
			start=QueryCopyPanel(self,pos,self.pos_from, self.pos_to,self.items_from )
			self.start=start
			#self.list=start.list
			self.active_dlcp=start
			self.nb.AddPage(start,'')
			#self.title=title
			self.nb.SetPageText(0, self.title)
			self.nb.SetSelection(0)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.nb, 1, wx.GROW|wx.EXPAND|wx.ALL, 0)
		self.SetSizer(self.sizer)
		self.SetAutoLayout(True)
		self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.onCloseTab, self.nb)
		#bg = self.nb.GetThemeBackgroundColour()
		#Publisher().subscribe(self.onOpenDesignForm, "open_design_form")
		sub(self.onOpenDesignForm, "open_design_form")
		#Publisher().subscribe(self.onAdjustDesignLogger, "adjust_design_logger")
		
		#open_design_form
		self.qc_id=0
		if 0:
			
			MENU_SELECT_GRADIENT_COLOR_FROM = wx.NewId()
			MENU_SELECT_GRADIENT_COLOR_TO = wx.NewId()
			MENU_SELECT_GRADIENT_COLOR_BORDER = wx.NewId()
			MENU_SET_ACTIVE_TEXT_COLOR = wx.NewId()
			MENU_SET_ACTIVE_TAB_COLOR = wx.NewId()
			MENU_SET_TAB_AREA_COLOR = wx.NewId()
			MENU_SELECT_NONACTIVE_TEXT_COLOR = wx.NewId()

			eventid = MENU_SET_TAB_AREA_COLOR
			if 1:
				data = wx.ColourData()		
				dlg = wx.ColourDialog(self, data)
			#print 'colour----------------------------',dlg.GetColourData().GetColour()
			red=wx.Colour(255, 0, 0, 255)
			blue=wx.Colour(0, 128, 255, 255)
			green= wx.Colour(0, 128, 0, 255)
			light_yellow=wx.Colour(255, 255, 128, 255)		
			light_green=wx.Colour(128, 255, 128, 255)
			light_blue=wx.Colour(128, 255, 255, 255)
			_TAB_AREA_COLOR=red			
			if pos==(0,0):
				_TAB_AREA_COLOR=light_blue
			elif pos==(0,1):
				_TAB_AREA_COLOR=light_yellow
			elif pos==(0,2):
				_TAB_AREA_COLOR=light_green


			if 1 and dlg.ShowModal() == wx.ID_OK:
				if eventid == MENU_SELECT_GRADIENT_COLOR_BORDER:
					self.nb.SetGradientColourBorder(dlg.GetColourData().GetColour())
				elif eventid == MENU_SELECT_GRADIENT_COLOR_FROM:
					self.nb.SetGradientColourFrom(dlg.GetColourData().GetColour())
				elif eventid == MENU_SELECT_GRADIENT_COLOR_TO:
					self.nb.SetGradientColourTo(dlg.GetColourData().GetColour())
				elif eventid == MENU_SET_ACTIVE_TEXT_COLOR:
					print 'colour----------------------------',dlg.GetColourData().GetColour()
					self.nb.SetActiveTabTextColour(dlg.GetColourData().GetColour())
				elif eventid == MENU_SELECT_NONACTIVE_TEXT_COLOR:
					self.nb.SetNonActiveTabTextColour(dlg.GetColourData().GetColour())
				elif eventid == MENU_SET_ACTIVE_TAB_COLOR:
					self.nb.SetActiveTabColour(dlg.GetColourData().GetColour())
				elif eventid == MENU_SET_TAB_AREA_COLOR:
					if 1:
						col = dlg.GetColourData().GetColour()
						print 'colour----------------------------', col, type(col)
					self.nb.SetTabAreaColour(_TAB_AREA_COLOR)
	def appendPanel(self,pos_from, pos_to, items_from,item_key):
		#define panel type
		cPanel =None
		(self.pos_from, self.pos_to) = (pos_from, pos_to)
		(table_name)=item_key
		title='%s.ppl' % table_name
		#from sharded_table_copy_panel import ShardedTableCopyPanel
		
		
		#source=
		_from=self.frame.getVarsToPath(pos_from).split('/')
		_to=self.frame.getVarsToPath(pos_to).split('/')
		source=_from[4:8]
		source.append(table_name)
		target=_to[4:8]
		target.append(table_name)	
		lists=(self.frame.getListFromPos(pos_from),self.frame.getListFromPos(self.pos_to))		
		cPanel=GenericCopyPanel(self,self.pos,pos_from, pos_to,items_from, (source,target),lists,title)
		if 0:
			if self.frame.getCurrentList(pos_from)==t_TABLE_LIST:
				#source is a table 
				

				if 0:
					from table_copy_panel import TableCopyPanel
					cPanel=TableCopyPanel(self,self.pos,pos_from, pos_to,items_from, table_name )
				else:
					#from sharded_table_copy_panel import ShardedTableCopyPanel
					from trunc_comp_stats_sharded_table_copy_panel import ShardedTableCopyPanel
					_from=self.frame.getVarsToPath(pos_from).split('/')
					_to=self.frame.getVarsToPath(pos_to).split('/')
					source=_from[4:7]
					source.append(table_name)
					target=_to[4:7]
					target.append(table_name)				
					cPanel=ShardedTableCopyPanel(self,self.pos,pos_from, pos_to,items_from, table_name, (source,target)  )
					
			elif self.frame.getCurrentList(pos_from)==t_PARTITION_LIST:
				from trunc_comp_stats_sharded_part_copy_panel import ShardedPartitionCopyPanel
				#source=
				_from=self.frame.getVarsToPath(pos_from).split('/')
				_to=self.frame.getVarsToPath(pos_to).split('/')
				source=_from[4:7]
				source.append(table_name)
				target=_to[4:7]
				target.append(table_name)
				cPanel=ShardedPartitionCopyPanel(self,self.pos,pos_from, pos_to,items_from, (source,target) )

			elif self.frame.getCurrentList(pos_from)==t_SUBPARTITION_LIST:
				from trunc_comp_stats_sharded_spart_copy_panel import ShardedSubPartitionCopyPanel
				#source=
				_from=self.frame.getVarsToPath(pos_from).split('/')
				_to=self.frame.getVarsToPath(pos_to).split('/')
				source=_from[4:8]
				source.append(table_name)
				target=_to[4:8]
				target.append(table_name)
				cPanel=ShardedSubPartitionCopyPanel(self,self.pos,pos_from, pos_to,items_from, (source,target) )
			elif self.frame.getCurrentList(pos_from)==t_COLUMN_LIST:
				#source is column
				from query_copy_panel import QueryCopyPanel
				#title='QueryCopy_%d.ppl' % self.qc_id
				_from=self.frame.getVarsToPath(pos_from).split('/')
				_to=self.frame.getVarsToPath(pos_to).split('/')
				source=_from[4:8]
				source.append(table_name)
				target=_to[4:8]
				target.append(table_name)			
				cPanel=QueryCopyPanel(self,self.pos,pos_from, pos_to,items_from, (source,target)  )
			#self.qc_id +=1
			
		#self.start=start
		#self.list=start.list
		self.active_dlcp=cPanel
		self.nb.AddPage(cPanel,'new panel')
		print dir(self.nb)
		#self.title=title
		cnt=self.nb.GetPageCount()-1
		self.nb.SetPageText(cnt, title)
		self.nb.SetSelection(cnt)
		plog.log('Created new pipeline %s.' % title.split('.')[0], cPanel.ID)
		#plog2.log('Plog2:Created new pipeline %s.' % title.split('.')[0], cPanel.ID)
		
		
	#@set_name
	def onOpenDesignForm(self, evt):
		(designer_pos, pos_from, pos_to, items_from, form_template)=evt.data	
		if self.pos==designer_pos:
			print  'onOpenDesignForm'
			print pos_from, pos_to, items_from, form_template
			if 0:
				self.splitter.SetSashPosition(0, 300)
				self.splitter.SetSashPosition(1, 600)
				self.splitter.SizeWindows()
				
	def setTitle(self,title):
		self.nb.SetPageText(0, title)
	def onCloseTab(self, evt):
		print 'onCloseTab'
		if 0:
			
			try:
				tabid = evt.GetSelection()
			except:
				tabid = self.GetSelection()
			print tabid
			if tabid==0:
				evt.Veto()
		else:
			print 'hide design panel'
			#self.panel_size=self.wnd_size[0]/4
			self.parent.SetSashPosition(0, self.frame.panel_size*2)
			self.parent.SetSashPosition(1, 0)
			self.parent.SizeWindows()				
			#adjust border tabs
	def getVarsToPath_(self):
		return self.active_dlcp.getVarsToPath()



			
class DesignPanel(wx.Panel, listmix.ColumnSorterMixin):
	def __init__(self, parent, pos, panel_pos # log
	):
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
		#self.SetDoubleBuffered(True)
		global prog
		self.ulocPanel= wx.Panel(self, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN, size=(-1,50))
		#wx.BoxSizer(wx.HORIZONTAL)
		self.url_locator={}
		self.find_in_btn={}
		self.nav_hist=[]
		self.curr_hist_id=0
		self._histMenu=None
		self._favMenu=None
		self._popUpMenu = {}
		(self.row, self.col) =pos
		self.pos=pos
		self.panel_pos=panel_pos
		#print panel_pos
		#sys.exit(1)
		self.sides={'00':'Left','01':'Right'}
		self.status='Welcome to %s!' % prog
		self.count = {}
		self.root_status="ROOT: Double click on ORACLE to zoom into Table level."
		self.hist_btn=OrderedDict()
		#self.log = log		
		#print (type(parent.Parent))
		tID = wx.NewId()
		self.frame=parent.frame
		#Publisher().subscribe(self.onUpdateLocation, "update_location")
		

		
			



		