import os, sys
import wx
from tc_lib import tc_runat, tc_loc, tc_host, tc_home, tc_srv
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
import xml.dom.minidom
from xml.dom.minidom import Node, Document
import common_utils as cu
from tc_init import *
from collections import OrderedDict
plog=cu.PanelLog()
from pprint import pprint
		
class pipeline_Template:
	def	__init__(self, tree):
		#self.ppln=ppln
		self.tree=tree
		self.form=tree.form
		#self.gl=gl
		self.to_table={}
		idx=1
		self.to_table[idx]='TMP_QC_%s' % self.form.ts 	
		self.source=self.form.source
		self.target=self.form.target	
		self.template_name=None
		self.p=OrderedDict()
	def setWorkerParams(self):		
		pass
		
	def getValue(self,n):
		return None
	def setGlobals0(self, template_name):
		tmpl_loc=os.path.join(appLoc,'xml_templates')
		
		tmpl_file_loc= os.path.join(tmpl_loc,template_name)
		self.doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
		tmpl=self.doc.getElementsByTagName("etldataflow")[0]
		tmpl_name=tmpl.getAttribute('name')
		self.ppl_name= tmpl_name+ '_%s' % ('.'.join(self.source))
		self.root = self.tree.AddRoot(self.ppl_name)
		#self.tree.SetItemText(self.tree.root, def_ppl_prof, 1)
		#
		if 0:
			flags=_ppl_flags[def_ppl_prof]
			for pid in range(len(flags)):
				print pid
				#self.listCtrl.SetStringItem(0, offset+pid+1, flags[pid])
				self.tree.SetItemText(self.root, flags[pid], offset+pid)
		#self.tree.SetItemText(self.tree.root, 'OFF', 2)
		self.tree.SetItemImage(self.root, self.tree.fldridx, which = wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, self.tree.fldropenidx, which = wx.TreeItemIcon_Expanded)
		self.tree.SetPyData(self.root,wx.TreeItemData(('etldataflow',{'node_type':'etldataflow','name':self.ppl_name})))
		

		self.tree.SetMainColumn(0)	
		#print dir(self.tree)
		#if 1:
		#def createQcPipelineWorker(cfrom,cto,config, worker_file,pipeline,  _tcmode):
		#create config file

		#doc = xml.dom.minidom.parse(tmpl_file_loc)
			
		doc_to = Document()
		base = doc_to.createElement('etldataflow')
		
		#base.setAttribute("pipeline_config",config)
		
		#pprint(dir(base))
		doc_to.appendChild(base)
		self.gl=self.doc.getElementsByTagName("globals")[0]
		runat = self.tree.AppendItem(self.root, 'runat')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.tree.SetPyData(runat,wx.TreeItemData(('runat',{'node_type':'runat'})))
		srv=tc_host[tc_srv][2]
		runat_server = self.tree.AppendItem(runat, 'server = "%s"' % srv)
		#self.tree.SetItemText(runat_server, tc_host[tc_srv][2], 1)
		self.tree.SetPyData(runat_server,wx.TreeItemData(('param',{'node_type':'param','name':'server','value':srv})))
		home=tc_loc[tc_srv][tc_home][0]
		runat_home = self.tree.AppendItem(runat, 'home = "%s"' % home)
		#self.tree.SetItemText(runat_home, tc_loc[tc_srv][tc_home][0], 1)
		self.tree.SetPyData(runat_home,wx.TreeItemData(('param',{'node_type':'param','name':'home','value':home})))
		usr ='ab95022'
		runat_user = self.tree.AppendItem(runat, 'user = "%s"' % usr)
		#self.tree.SetItemText(runat_user, 'ab95022', 1) #tc_host[tc_srv][2]
		self.tree.SetPyData(runat_user,wx.TreeItemData(('param',{'node_type':'param','name':'user','value':usr})))
		
		tc_loc[tc_srv][tc_home][0]
		
		self.tree.Expand(runat)
		self.globals = self.tree.AppendItem(self.root, 'globals')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.tree.SetPyData(self.globals,wx.TreeItemData(('globals',{'node_type':'globals',})))	
		p=0		
		for n in self.gl.getElementsByTagName("param"):
			
			#for i in range(10):
			
			child = self.tree.AppendItem(self.globals, '%s = "%s"' %(n.getAttribute('name'),n.getAttribute('value')))
			#self.tree.SetItemText(child, def_w_prof, idx)
			print n.getAttribute('name'), n.getAttribute('value')
			#self.tree.SetItemText(child, n.getAttribute('value'), 1)
			self.tree.SetPyData(child,wx.TreeItemData(('param',{'node_type':'param','name':n.getAttribute('name'),'value':n.getAttribute('value')})))
			p +=1
	def _setGlobals(self, template_name):
		tmpl_loc=os.path.join(appLoc,'xml_templates')
		
		tmpl_file_loc= os.path.join(tmpl_loc,template_name)
		self.doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
		tmpl=self.doc.getElementsByTagName("etldataflow")[0]
		tmpl_name=tmpl.getAttribute('name')
		self.ppl_name= tmpl_name+ '_%s' % ('.'.join(self.source))
		#self.root = self.tree.AddRoot(self.ppl_name)
		#self.tree.SetItemText(self.tree.root, def_ppl_prof, 1)
		#
		
		if 0:
			flags=_ppl_flags[def_ppl_prof]
			for pid in range(len(flags)):
				print pid
				#self.listCtrl.SetStringItem(0, offset+pid+1, flags[pid])
				self.tree.SetItemText(self.root, flags[pid], offset+pid)
		#self.tree.SetItemText(self.tree.root, 'OFF', 2)
		#self.tree.SetItemImage(self.root, self.tree.fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(self.root, self.tree.fldropenidx, which = wx.TreeItemIcon_Expanded)
		#self.tree.SetPyData(self.root,wx.TreeItemData(('etldataflow',{'node_type':'etldataflow','name':self.ppl_name})))
		

		#self.tree.SetMainColumn(0)	
		#print dir(self.tree)
		#if 1:
		#def createQcPipelineWorker(cfrom,cto,config, worker_file,pipeline,  _tcmode):
		#create config file

		#doc = xml.dom.minidom.parse(tmpl_file_loc)
			
		#doc_to = Document()
		#base = doc_to.createElement('etldataflow')
		
		#base.setAttribute("pipeline_config",config)
		
		#pprint(dir(base))
		#doc_to.appendChild(base)
		self.gl=self.doc.getElementsByTagName("globals")[0]
		#self.initPipelineParams(self.gl)
		#runat = self.tree.AppendItem(self.root, 'runat')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		#self.tree.SetPyData(runat,wx.TreeItemData(('runat',{'node_type':'runat'})))
		#srv=tc_host[tc_srv][2]
		#runat_server = self.tree.AppendItem(runat, 'server = "%s"' % srv)
		#self.tree.SetItemText(runat_server, tc_host[tc_srv][2], 1)
		#self.tree.SetPyData(runat_server,wx.TreeItemData(('param',{'node_type':'param','name':'server','value':srv})))
		#home=tc_loc[tc_srv][tc_home][0]
		#runat_home = self.tree.AppendItem(runat, 'home = "%s"' % home)
		#self.tree.SetItemText(runat_home, tc_loc[tc_srv][tc_home][0], 1)
		#self.tree.SetPyData(runat_home,wx.TreeItemData(('param',{'node_type':'param','name':'home','value':home})))
		#usr ='ab95022'
		#runat_user = self.tree.AppendItem(runat, 'user = "%s"' % usr)
		#self.tree.SetItemText(runat_user, 'ab95022', 1) #tc_host[tc_srv][2]
		#self.tree.SetPyData(runat_user,wx.TreeItemData(('param',{'node_type':'param','name':'user','value':usr})))
		
		#tc_loc[tc_srv][tc_home][0]
		
		#self.tree.Expand(runat)
		#self.globals = self.tree.AppendItem(self.root, 'globals')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		#self.tree.SetPyData(self.globals,wx.TreeItemData(('globals',{'node_type':'globals',})))	
		#p=0		
		#self.p={}
		#for n in self.gl.getElementsByTagName("param"):
		if 0:
			for i, val in self.p.items():
				
				#for i in range(10):
				#self.p[n.getAttribute('name')] = n.getAttribute('value')
				child = self.tree.AppendItem(self.globals, '%s = "%s"' %(i,val))
				#self.tree.SetItemText(child, def_w_prof, idx)
				#print n.getAttribute('name'), n.getAttribute('value')
				#self.tree.SetItemText(child, n.getAttribute('value'), 1)
				self.tree.SetPyData(child,wx.TreeItemData(('param',{'node_type':'param','name':i,'value':val})))
				p +=1
	def setGlobals(self, template_name):
		tmpl_loc=os.path.join(appLoc,'xml_templates')
		
		tmpl_file_loc= os.path.join(tmpl_loc,template_name)
		self.doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
		tmpl=self.doc.getElementsByTagName("etldataflow")[0]
		tmpl_name=tmpl.getAttribute('name')
		self.ppl_name= tmpl_name+ '_%s' % ('.'.join(self.source))
		self.root = self.tree.AddRoot(self.ppl_name)
		#self.tree.SetItemText(self.tree.root, def_ppl_prof, 1)
		#
		
		if 0:
			flags=_ppl_flags[def_ppl_prof]
			for pid in range(len(flags)):
				print pid
				#self.listCtrl.SetStringItem(0, offset+pid+1, flags[pid])
				self.tree.SetItemText(self.root, flags[pid], offset+pid)
		#self.tree.SetItemText(self.tree.root, 'OFF', 2)
		self.tree.SetItemImage(self.root, self.tree.fldridx, which = wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, self.tree.fldropenidx, which = wx.TreeItemIcon_Expanded)
		self.tree.SetPyData(self.root,wx.TreeItemData(('etldataflow',{'node_type':'etldataflow','name':self.ppl_name})))
		

		self.tree.SetMainColumn(0)	
		#print dir(self.tree)
		#if 1:
		#def createQcPipelineWorker(cfrom,cto,config, worker_file,pipeline,  _tcmode):
		#create config file

		#doc = xml.dom.minidom.parse(tmpl_file_loc)
			
		doc_to = Document()
		base = doc_to.createElement('etldataflow')
		
		#base.setAttribute("pipeline_config",config)
		
		#pprint(dir(base))
		doc_to.appendChild(base)
		self.gl=self.doc.getElementsByTagName("globals")[0]
		#print self.gl.getElementsByTagName("param")
		#sys.exit(1)
		self.initPipelineParams(self.gl)
		runat = self.tree.AppendItem(self.root, 'runat')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.tree.SetPyData(runat,wx.TreeItemData(('runat',{'node_type':'runat'})))
		srv=tc_host[tc_srv][2]
		runat_server = self.tree.AppendItem(runat, 'server = "%s"' % srv)
		#self.tree.SetItemText(runat_server, tc_host[tc_srv][2], 1)
		self.tree.SetPyData(runat_server,wx.TreeItemData(('param',{'node_type':'param','name':'server','value':srv})))
		home=tc_loc[tc_srv][tc_home][0]
		runat_home = self.tree.AppendItem(runat, 'home = "%s"' % home)
		#self.tree.SetItemText(runat_home, tc_loc[tc_srv][tc_home][0], 1)
		self.tree.SetPyData(runat_home,wx.TreeItemData(('param',{'node_type':'param','name':'home','value':home})))
		usr ='ab95022'
		runat_user = self.tree.AppendItem(runat, 'user = "%s"' % usr)
		#self.tree.SetItemText(runat_user, 'ab95022', 1) #tc_host[tc_srv][2]
		self.tree.SetPyData(runat_user,wx.TreeItemData(('param',{'node_type':'param','name':'user','value':usr})))
		
		tc_loc[tc_srv][tc_home][0]
		
		self.tree.Expand(runat)
		self.globals = self.tree.AppendItem(self.root, 'globals')
		#self.tree.SetItemImage(globals, fldridx, which = wx.TreeItemIcon_Normal)
		#self.tree.SetItemImage(globals, fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.tree.SetPyData(self.globals,wx.TreeItemData(('globals',{'node_type':'globals',})))	
		#p=0		
		#self.p={}
		#for n in self.gl.getElementsByTagName("param"):
		print self.p
		#sys.exit(1)
		for i, val in self.p.items():
			
			#for i in range(10):
			#self.p[n.getAttribute('name')] = n.getAttribute('value')
			child = self.tree.AppendItem(self.globals, '%s = "%s"' %(i,val))
			#self.tree.SetItemText(child, def_w_prof, idx)
			#print n.getAttribute('name'), n.getAttribute('value')
			#self.tree.SetItemText(child, n.getAttribute('value'), 1)
			self.tree.SetPyData(child,wx.TreeItemData(('param',{'node_type':'param','name':i,'value':val})))
			#p +=1
		#self.tree.Expand(self.globals)

	def initPipelineParams(self,gl):
		#self.p={} #params
		for n in gl.getElementsByTagName("param"):
			#print n.getAttribute('value')
			(key,val)= (n.getAttribute('name'),n.getAttribute('value'))
			#pprint(self.p)
			#sys.exit(1)
			if 1: #rewrite all default in a template
				self.p[n.getAttribute('name')]=n.getAttribute('value')
				if 'FROM_DB' == key:
					self.p['FROM_DB'] =self.form.spath.split('/')[3]
				if 'TO_DB'  == key:
					self.p['TO_DB'] =self.form.tpath.split('/')[3]
				if 'TO_SCHEMA'  == key:
					self.p['FROM_SCHEMA'] =self.form.spath.split('/')[4]
				if 'TO_SCHEMA'  == key:
					self.p['TO_SCHEMA'] =self.form.tpath.split('/')[4]
				
		for i, val in self.p.items():
			print i, val, self.form.ID
			plog.log('Global param %s = "%s"' % (i,val), self.form.ID)
			
		#print self.form.spath
		#print self.form.tpath
		#print self.gl
		#print self.form.spath
		#print self.form.tpath
		_tcmode='SYNC'	
		if 0:
			
			flowt= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+self.p['FROM_DB']+'%')
			#fromschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			#fromschema.setAttribute('value',schema_from)

			todb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+self.p['db_to']+'%')	
			#toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			#toschema.setAttribute('value',schema_to)			
	def setWorker(self, worker):
		self.setWorkerParams()
		worker_ = self.tree.AppendItem(self.pipeline, 'WORKER "%s"' % ('.'.join(self.source)))
		self.tree.SetItemImage(worker_, self.tree.fldridx, which = wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(worker_, self.tree.fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.tree.SetPyData(worker_,wx.TreeItemData(('worker',{'node_type':'worker','name':'.'.join(self.source)})))			
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

						
				
				#self.tree.SetItemText(wk, 'Template: Query Copy', 1)

				task = self.tree.AppendItem(worker_, 'task "%s"' % exec_title)
				#self.tree.SetItemText(wk, 'Template: Query Copy', 1)
				self.tree.SetItemImage(task, self.tree.fldridx, which = wx.TreeItemIcon_Normal)
				self.tree.SetItemImage(task, self.tree.fldropenidx, which = wx.TreeItemIcon_Expanded)			
				self.tree.SetPyData(task,wx.TreeItemData((exec_node.nodeName,{'node_type':'task','node_title':exec_title,'util_node_name':self.util_node.nodeName,'util_method':util_method})))
				
				locals = self.tree.AppendItem(task, 'locals')
				#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
				#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
				self.tree.SetPyData(locals,wx.TreeItemData(('locals',{'node_type':'locals'})))
				p=0
				#if 0:
				for n in self.util_node.getElementsByTagName("param"):
					#print 
					
					#self.tree.SetItemText(child, def_w_prof, idx)
					print n.getAttribute('name'), n.getAttribute('value')
					#self.tree.SetItemText(child, n.getAttribute('value'), 1)
					value=self.getValue(n)
					
					child = self.tree.AppendItem(locals, '%s = "%s"' % (n.getAttribute('name'),value))
					self.tree.SetPyData(child,wx.TreeItemData(('param',{'node_type':'param','name':n.getAttribute('name'),'value':value })))
					p +=1
				#self.Expand(locals)
				#sys.exit(0)
				#self.q=self.createQuery(form.data,form.spath)
				#self.schema_table='.'.join(self.source)
				template = self.tree.AppendItem(task, 'template')
				self.tree.SetPyData(template,wx.TreeItemData(('template',{'node_type':'template'})))
				cd= self.getCDATA(worker,self.util_node)
				cdata = self.tree.AppendItem(template, cd)
				
				#self.tree.SetItemText(query, '%s...' % q[:15], 1)
				
				#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
				#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
				self.setTemplate(cdata,cd)
				#self.Expand(task)
				self.tree.Expand(template)
		self.tree.Expand(worker_)
	def setTemplate(self,cdata,cd):
		
		self.tree.SetPyData(cdata,wx.TreeItemData(('cdata',{'node_type':'sql_template','tag':'sql_template','cdata':cd})))
	def getCDATA(self,worker,util_node):
		return '%s' %[n for n in util_node.getElementsByTagName("sql_template")[0].childNodes if n.nodeType==worker.CDATA_SECTION_NODE][0].data
	def CreatePipelineTree(self):
		
		self.setGlobals(self.template_name)
			
		idx=1
		

		

		#txt = self.to_table[idx]

		p=0

		#self.Expand(self.globals)
		ppl_type='SYNC_PIPELINE'
		self.pipeline = self.tree.AppendItem(self.root, 'SYNC_PIPELINE')
		self.tree.SetItemImage(self.pipeline, self.tree.fldridx, which = wx.TreeItemIcon_Normal)
		self.tree.SetItemImage(self.pipeline, self.tree.fldropenidx, which = wx.TreeItemIcon_Expanded)			
		self.tree.SetPyData(self.pipeline,wx.TreeItemData(('pipeline',{'node_type':'pipeline'})))
		
		if ppl_type =='ASYNC_PIPELINE':
			callbefore = self.tree.AppendItem(self.pipeline, 'CallBefore')
			#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
			#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
			self.tree.SetPyData(callbefore,wx.TreeItemData(('CallBefore',{'node_type':'call_before'})))
		worker_stab=self.doc.getElementsByTagName("worker")[0].toxml()
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
		self.setWorker(worker)
		if ppl_type =='ASYNC_PIPELINE':
			callafter = self.tree.AppendItem(self.pipeline, 'CallAfter')
			#self.tree.SetItemImage(block, fldridx, which = wx.TreeItemIcon_Normal)
			#self.tree.SetItemImage(pipeline, fldropenidx, which = wx.TreeItemIcon_Expanded)			
			self.tree.SetPyData(callafter,wx.TreeItemData(('CallAfter',{'node_type':'call_after'})))	
		self.tree.Expand(self.pipeline)	
		self.tree.Expand(self.root)
class pipeline_TableList_to_TableList(pipeline_Template):
	def	__init__(self, tree):
		pipeline_Template.__init__(self, tree)
		self.template_name='pipeline_TableList_to_TableList.xml'
		#self.tree=tree	
	def setWorkerParams(self):
		self.p={} #params
		self.p['db_from'] =self.form.spath.split('/')[3]
		self.p['db_to'] =self.form.tpath.split('/')[3]
		self.p['schema_from'] =self.form.spath.split('/')[4]
		self.p['schema_to'] =self.form.tpath.split('/')[4]
		print self.form.spath
		print self.form.tpath
		print self.gl
		
		_tcmode='SYNC'	
		if 1:
			flowt= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+self.p['db_from']+'%')
			#fromschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			#fromschema.setAttribute('value',schema_from)

			todb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+self.p['db_to']+'%')	
			#toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			#toschema.setAttribute('value',schema_to)	
	def getValue(self,n):
		value=n.getAttribute('value')
		if n.getAttribute('name') in ('TO_TABLE','TABLE_NAME'):
			value=self.target[1]
		if n.getAttribute('name')in ('TO_SCHEMA','SCHEMA_NAME'):
			value=self.target[0]							
		if n.getAttribute('name')in ('SUBPARTITION') and len(self.target)>3:
			value=self.target[3]	
		else:
			if n.getAttribute('name')in ('PARTITION') and len(self.target)>2:
				value=self.tree.target[2]
		if n.getAttribute('name') in ('DB_CONNECTOR','TO_DB'):
			value='%'+self.p['db_to']+'%'							
		print  value
		return value
	def setTemplate(self,cdata,cd):
		#print self.source
		#print self.target
		self.tree.SetPyData(cdata,wx.TreeItemData(('cdata',{'node_type':'sql_template','tag':'sql_template','cdata':cd})))		
	def getCDATA(self,worker,util_node):
		return '%s' % ('%s.%s' % tuple(self.source))
		
		
class pipeline_PartitionList_to_PartitionList(pipeline_Template):
	def	__init__(self, tree):
		pipeline_Template.__init__(self, tree)
		self.template_name='pipeline_PartitionList_to_PartitionList.xml'
		#self.tree=tree	
	def setWorkerParams(self):
		self.p={} #params
		self.p['db_from'] =self.form.spath.split('/')[3]
		self.p['db_to'] =self.form.tpath.split('/')[3]
		self.p['schema_from'] =self.form.spath.split('/')[4]
		self.p['schema_to'] =self.form.tpath.split('/')[4]
		print self.form.spath
		print self.form.tpath
		print self.gl
		
		_tcmode='SYNC'	
		if 1:
			flowt= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+self.p['db_from']+'%')
			#fromschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			#fromschema.setAttribute('value',schema_from)

			todb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+self.p['db_to']+'%')	
			#toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			#toschema.setAttribute('value',schema_to)	
	def getValue(self,n):
		value=n.getAttribute('value')
		if n.getAttribute('name') in ('TO_TABLE','TABLE_NAME'):
			value=self.target[1]
		if n.getAttribute('name')in ('TO_SCHEMA','SCHEMA_NAME'):
			value=self.target[0]							
		if n.getAttribute('name')in ('SUBPARTITION') and len(self.target)>3:
			value=self.target[3]	
		else:
			if n.getAttribute('name')in ('PARTITION') and len(self.target)>2:
				value=self.tree.target[2]
		if n.getAttribute('name') in ('DB_CONNECTOR','TO_DB'):
			value='%'+self.p['db_to']+'%'							
		print  value
		return value		
class pipeline_SubPartitionList_to_SubPartitionList(pipeline_Template):
	def	__init__(self, tree):
		pipeline_Template.__init__(self, tree)
		self.template_name='pipeline_SubPartitionList_to_SubPartitionList.xml'
		#self.tree=tree	
	def setWorkerParams(self):
		self.p={} #params
		self.p['db_from'] =self.form.spath.split('/')[3]
		self.p['db_to'] =self.form.tpath.split('/')[3]
		self.p['schema_from'] =self.form.spath.split('/')[4]
		self.p['schema_to'] =self.form.tpath.split('/')[4]
		print self.form.spath
		print self.form.tpath
		print self.gl
		
		_tcmode='SYNC'	
		if 1:
			flowt= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+self.p['db_from']+'%')
			#fromschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			#fromschema.setAttribute('value',schema_from)

			todb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+self.p['db_to']+'%')	
			#toschema= [n for n in gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			#toschema.setAttribute('value',schema_to)	
	def getValue(self,n):
		value=n.getAttribute('value')
		if n.getAttribute('name') in ('TO_TABLE','TABLE_NAME'):
			value=self.target[1]
		if n.getAttribute('name')in ('TO_SCHEMA','SCHEMA_NAME'):
			value=self.target[0]							
		if n.getAttribute('name')in ('SUBPARTITION') and len(self.target)>3:
			value=self.target[3]	
		else:
			if n.getAttribute('name')in ('PARTITION') and len(self.target)>2:
				value=self.tree.target[2]
		if n.getAttribute('name') in ('DB_CONNECTOR','TO_DB'):
			value='%'+self.p['db_to']+'%'							
		print  value
		return value
class pipeline_ColumnList_to_TableList(pipeline_Template):
	def	__init__(self, tree):
		pipeline_Template.__init__(self, tree)
		self.template_name='pipeline_ColumnList_to_TableList.xml'
		#self.tree=tree	
	def setWorkerParams(self):
		self.p={} #params
		self.p['db_from'] =self.form.spath.split('/')[3]
		self.p['db_to'] =self.form.tpath.split('/')[3]
		self.p['schema_from'] =self.form.spath.split('/')[4]
		self.p['schema_to'] =self.form.tpath.split('/')[4]
		print self.form.spath
		print self.form.tpath
		print self.gl
		
		_tcmode='SYNC'	
		if 1:
			flowt= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FLOW_TYPE'][0]
			flowt.setAttribute('value',_tcmode)
			fromdb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_DB'][0]
			fromdb.setAttribute('value','%'+self.p['db_from']+'%')
			fromschema= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='FROM_SCHEMA'][0]
			fromschema.setAttribute('value',self.p['schema_from'] )

			todb= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_DB'][0]
			todb.setAttribute('value','%'+self.p['db_to']+'%')	
			toschema= [n for n in self.gl.getElementsByTagName("param") if n.getAttribute('name')=='TO_SCHEMA'][0]
			toschema.setAttribute('value',self.p['schema_to'] )
	def getValue(self,n):
		value=n.getAttribute('value')
		if n.getAttribute('name') in ('TO_TABLE','TABLE_NAME'):
			value=self.source[1]
		if n.getAttribute('name')in ('TO_SCHEMA','SCHEMA_NAME'):
			value=self.source[0]
		if n.getAttribute('name') in ('DB_CONNECTOR','TO_DB'):
			value='%'+db_to+'%'								
		print  value
		return value
	def createQuery(self,data, spath):
			q='SELECT '
			for i in range(len(data)):
				item = data[i]
				q='%s %s\n,' % (q,item[2])
				print item
			#sys.exit(1)
			from_loc=spath
			print spath
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
	def setTemplate(self,cdata,cd):
		self.tree.SetPyData(cdata,wx.TreeItemData(('cdata',{'node_type':'query','tag':'sql_template','cdata':cd})))			
	def getCDATA(self,worker,util_node):
		return '%s' % self.createQuery(self.form.data,self.form.spath)