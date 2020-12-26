import os
from tc_lib import tc_runat, tc_loc, tc_host, tc_home, tc_srv
from tc_lib import cml, getPipelineConfig, activeProjName, activeProjLoc, DEFAULT_PERSPECTIVE, projRootLoc, confDirName, configDirLoc,  appLoc
import xml.dom.minidom
from xml.dom.minidom import Node, Document
import common_utils as cu
from tc_init import *
class xml_Pipeline(object):
	def	__init__(self, tree):
		self.tree=tree
	def getXmlFileNames(self, ts=None):
		if not ts:
			ts= self.tree.form.ts
		return ('pipeline_config_%s.xml' % ts, 'tc_query_copy_%s.xml' % ts)	
	def getXMLConnector(self, doc, conn_env, conn_name):
		conn=doc.getElementsByTagName("connector")[0]
		assert conn, 'Cannot find connector tag.'
		print conn_env
		env_type=conn_env.split('.')[0]
		env=conn.getElementsByTagName(env_type)[0]
		alias_name=conn_env.split('.')[1]
		alias=env.getElementsByTagName(alias_name)[0]
		
		connector=alias.getElementsByTagName(conn_name)[0]	
		return connector
	def createPipelineConfig(self,cfrom,cto,config_file):
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
			#(status, err)=cu.rcopyFile(out_file,'%s/%s' % (remote_loc,config_file),(0,1), self.tree.ID)
			#sys.exit(1)
		return (out_file,remote_loc, config_file)		
class xml_Table(xml_Pipeline):
	def	__init__(self, tree):
		xml_Pipeline.__init__(self, tree)
		#self.tree=tree		
	def createPipelineWorker(self, cfrom,cto,config, worker_file):
		#create config file
		max_shards=20
		print appLoc
		db_from =cfrom.split('/')[3]
		db_to =cto.split('/')[3]
		schema_from =cfrom.split('/')[4]
		schema_to =cto.split('/')[4]
		print cfrom
		print cto
		_globals=self.tree.getGlobals()
		print _globals
		_tcmode=_globals['FLOW_TYPE']
		#sys.exit(1)
		doc_to = Document()
		elem={}
		(root,attr)=self.tree.GetPyData(self.tree.root).GetData()
		root_elem = doc_to.createElement(root)
		
		for key,val in attr.items():
			root_elem.setAttribute(key,val )
		#sys.exit(0)
		root_elem.setAttribute("pipeline_config",config)
		for r in self.tree.root.GetChildren():
			(r_tag, attr)=self.tree.GetPyData(r).GetData()
			print '------------', r_tag
			tag_elem = None
			if r_tag in ('runat'):
				pass
			elif r_tag in ('globals'):
				tag_elem = doc_to.createElement(r_tag)
				if r.GetChildrenCount()>0:
					for par in r.GetChildren():
						(param, attr)=self.tree.GetPyData(par).GetData()
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
					(w_tag, attr)=self.tree.GetPyData(w).GetData()
					print 0,w_tag, attr
					w_elem = doc_to.createElement(w_tag)
					if w_tag in ('worker'):
						for name,value in attr.items():
							w_elem.setAttribute(name,value )
						for t in w.GetChildren():
							#print t.GetText()
							(t_tag, attr)=self.tree.GetPyData(t).GetData()
							print 1,t_tag,attr
							#sys.exit(1)
							t_elem = doc_to.createElement(t_tag)
							t_utils=doc_to.createElement(attr['util_node_name'])
							t_utils.setAttribute('method',attr['util_method'] )
							for v in t.GetChildren():
								print v.GetText()
								(v_tag, attr)=self.tree.GetPyData(v).GetData()
								print 2,v_tag, attr
								if v_tag in ('locals'):
									for p in v.GetChildren():
										(p_tag, attr)=self.tree.GetPyData(p).GetData()
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
			template_name='trunc_comp_stats_sharded_table_copy.xml'
			tmpl_file_loc= os.path.join(tmpl_loc,template_name)
			doc = xml.dom.minidom.parseString(open(tmpl_file_loc, "r").read())
			worker_stab=doc.getElementsByTagName("worker")[0].toxml()
			worker = xml.dom.minidom.parseString(worker_stab).getElementsByTagName("worker")[0]
		#base.appendChild(worker)
		doc_to.appendChild(root_elem)
		
		if 0:
			tmpl_loc=os.path.join(appLoc,'xml_templates')
			template_name='trunc_comp_stats_sharded_table_copy.xml'
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
		#print 'echo %s|pscp %s\\%s bk94994@swmapetldev01.nam.nsroot.net:%s' % (lpwd,out_dir,worker_file,remote_loc)
		#os.system('echo %s|pscp %s\\%s zkqfas6@lrche25546:%s' % (lpwd, out_dir,worker_file,remote_loc))
		#(status, err)=cu.rcopyFile(os.path.join(out_dir,worker_file),'%s/%s' % (remote_loc,worker_file),(0,1),self.tree.ID)
		#create worker file
		return (os.path.join(out_dir,worker_file),'%s/%s' % (remote_loc,worker_file), worker_file)
	
class xml_SubPartition(xml_Pipeline):
	"""SubPartition xmlg generator Class."""
	def	__init__(self, tree):
		xml_Pipeline.__init__(self, tree)
	def createPipelineWorker(self, cfrom,cto,config, worker_file):
		#create config file
		max_shards=20
		print appLoc
		db_from =cfrom.split('/')[3]
		db_to =cto.split('/')[3]
		schema_from =cfrom.split('/')[4]
		schema_to =cto.split('/')[4]
		print cfrom
		print cto
		_globals=self.tree.getGlobals()
		print _globals
		_tcmode=_globals['FLOW_TYPE']
		#sys.exit(1)
		doc_to = Document()
		elem={}
		(root,attr)=self.tree.GetPyData(self.tree.root).GetData()
		root_elem = doc_to.createElement(root)
		
		for key,val in attr.items():
			root_elem.setAttribute(key,val )
		#sys.exit(0)
		root_elem.setAttribute("pipeline_config",config)
		for r in self.tree.root.GetChildren():
			(r_tag, attr)=self.tree.GetPyData(r).GetData()
			print '------------', r_tag
			tag_elem = None
			if r_tag in ('runat'):
				pass
			elif r_tag in ('globals'):
				tag_elem = doc_to.createElement(r_tag)
				if r.GetChildrenCount()>0:
					for par in r.GetChildren():
						(param, attr)=self.tree.GetPyData(par).GetData()
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
					(w_tag, attr)=self.tree.GetPyData(w).GetData()
					print 0,w_tag, attr
					w_elem = doc_to.createElement(w_tag)
					if w_tag in ('worker'):
						for name,value in attr.items():
							w_elem.setAttribute(name,value )
						for t in w.GetChildren():
							#print t.GetText()
							(t_tag, attr)=self.tree.GetPyData(t).GetData()
							print 1,t_tag,attr
							#sys.exit(1)
							t_elem = doc_to.createElement(t_tag)
							t_utils=doc_to.createElement(attr['util_node_name'])
							t_utils.setAttribute('method',attr['util_method'] )
							for v in t.GetChildren():
								(v_tag, attr)=self.tree.GetPyData(v).GetData()
								print 2,v_tag, attr
								if v_tag in ('locals'):
									for p in v.GetChildren():
										(p_tag, attr)=self.tree.GetPyData(p).GetData()
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
		(status, err)=cu.rcopyFile(os.path.join(out_dir,worker_file),'%s/%s' % (remote_loc,worker_file),(0,1),self.tree.ID)
		#create worker file
		return (out_dir,remote_loc, worker_file)