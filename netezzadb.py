class NetezzaDb(object):
	"""Worker Thread Class."""
	def __init__(self,pos):
		self.result=None
		self.worker=None
		self.pos=pos
		Publisher().subscribe(self.onStopDbRequest, "stop_db_request")
	def onStopDbRequest(self, evt):
		print 'aborting db request'
		
		if self.worker:			
			#terminate_thread(self.worker)
			#
			#self.worker.join()
			print self.worker.isAlive()
			if self.worker.isAlive():
				
				print 'it''s alive, aborting...'
				#self.worker.abort()
				#self.worker.terminate()
				terminate_thread(self.worker)
				Publisher().sendMessage( "db_thread_event", ('aborted',self.pos,None, None) )
				#return
		else:
			print 'no worker thread'		
			#Publisher().sendMessage( "db_thread_event", ('done',self.worker.pos,self.worker.cache,self.worker.result) )
		
	def getConfigs(self,configDirLoc):
		ta={}		
		if ifCacheExists(gConfigCache):
			print 'getConfigs cache exists',cache
			ta=readFromCache(gConfigCache)
			#print ta
			#sys.exit(1)
		else:	
			#print configDirLoc 

			files = os.listdir(configDirLoc)

			#print files
			#files.sort(reverse=True)
			for i in range(len(files)):
				f=files[i]
				st= os.stat(os.path.join(configDirLoc,f))
				#pprint(st)
				r = (f,'config',st.st_size,time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(st.st_atime)))
				#print time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(st.st_atime))
				#print r
				ta[i]=r
			#sys.exit(1)
			
			#ta=out
			#updateCache(gConfigCache,ta)
		
		return ta
		
	def getDatabases(self,login):
		ta={}
		(user,db,pwd) = login
		cache='%s.%s_%s' % (gDatabaseCache,user,db)
		#print cache
		if use_cache and ifCacheExists(cache):	
			print 'cache exists ',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select v.database,type, TO_CHAR(size,'999,999,999,999.9'),db.createdate FROM
	(select database, 'database' Type, ROUND(sum(used_bytes)/1024/1024,1) size
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	--where objname = 'UPPERCASE_TABLE_NAME'
	group by database) v, _v_database db
	where v.database=db.database order by 1"""
			#Publisher().sendMessage( "show_progress", ((0, 0)) )
			#app.frame.gaugeStart(self.pos)
			Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			
			#time.sleep(1)

			#wx.Yield()
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			self.worker = DbThread(self.pos,gDatabaseCache,q, (user,db,pwd), limit=None)
			self.worker.start()
			print self.worker.isAlive()
			#self.worker.join()
			#pprint(dir(self.worker))
			#app.frame.gaugeStop()
			if 0:
				i=0
				for rec in out:
					ta[i]=rec
					i +=1
				#updateCache(cache,ta)

		#return ta
		

	def getOwners(self,login, database='MRR_BI'):
		(user,db,pwd) = login	
		ta={}
		cache='%s.%s_%s.%s' % (gOwnersCache,user,db,database)
		if  use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select owner,type, TO_CHAR(size,'999,999,999,999.99') size,u .createdate from 
	(select owner, 'owner' type, ROUND(sum(used_bytes)/1024/1024,1) size
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	where database = '%s'
	group by owner) v, (select username, createdate from _v_user) u
	where v.owner=u.username
	order by 1
	""" % database
			#(db,user) = ('MRR_BI','MRR_ETL_USER')
			Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.pos,gOwnersCache,q, (user,db,pwd), limit=None)
			self.worker.start()
			print self.worker.isAlive()


	def getTables(self,login, location, object_filter):
		(user,db,pwd) = login	
		ta={}
		cache='%s.%s_%s.%s' % (gTableCache,user,db,location[0])
		#print cache
		if use_cache and ifCacheExists(cache):
			
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""select objname, 'table' type,TO_CHAR( ROUND(sum(used_bytes)/1024/1024,1),'999,999,999,999.9') size, createdate 
	from _V_OBJ_RELATION_XDB 
	join _V_SYS_OBJECT_DSLICE_INFO on (objid = tblid) 
	where  owner='%s'
	group by objname, createdate
	order by 1
	""" % location
			Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.pos,cache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()

	def getTableColumns(self,login, location):
		(user,db,pwd) = login	
		ta={}
		cache='%s.%s_%s.%s_%s' % (gTableColumnsCache,user,db,location[0],location[1])
		if use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			ta=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:	
			q="""SELECT attname,format_type,attlen,'column',ATTNUM, createdate FROM _V_RELATION_COLUMN_XDB 
				  WHERE owner= '%s' and upper(NAME)=UPPER('%s') 
				  ORDER BY ATTNUM ASC;
	""" % location
			#(db,user) = ('MRR_BI','MRR_ETL_USER')
			Publisher().sendMessage( "start_db_progress_gauge", (self.pos) )
			#(status, err, rowcount,headers, out)=dbu.query(q, (user,db), limit=None)
			#print (out)
			#from collections import OrderedDict
			#ta=OrderedDict()	
			self.worker = DbThread(self.pos,cache,q, login, limit=None)
			self.worker.start()
			print self.worker.isAlive()
			if 0:
				(status, err, rowcount,headers, out)=dbu.query(q, login, limit=999)
				#print (out)
				#sys.exit(1)
				#from collections import OrderedDict
				#ta=OrderedDict()	
				i=0		
				for rec in out:
					ta[i]=rec
					i +=1
				#updateCache(cache,ta)
				#sys.exit(1)
				#print ta
		if 0: return ta
		
	def getEnvironments(self,configFile):
		print configFile
		cache= '%s.%s' % (gEnvironmentCache, os.path.basename(configFile).replace('.','_'))
		#print cache
		out ={}
		if  use_cache and ifCacheExists(cache):
			print 'cache exists',cache
			out=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:
			
			x = configFile
			doc = xml.dom.minidom.parse(x)
			
			for node in doc.getElementsByTagName("app_spec"):
			  #isbn = node.getAttribute("isbn")
			  #L = node.getElementsByTagName("title")
			  for node2 in node.childNodes:
				#title = ""
				
				if node2.nodeType != Node.TEXT_NODE:
					#print node2.nodeType, node2.nodeName	
					#if node2.nodeName=='process_spec':
						#print dir(node2.attributes.tems)
						#values=[]
						#for aName, aValue  in node2.attributes.items():
						#	values.append("%s=%s" % (aName, aValue))				
						#_tree.append((node2.nodeName,values))
					if node2.nodeName=='connector':
						#print dir(node2.attributes.tems)
						#values=[]
						i=0
						for node3  in node2.childNodes:
							if node3.nodeType != Node.TEXT_NODE and node3.nodeType != Node.COMMENT_NODE:
								env_type=node3.nodeName.upper()
								for node4  in node3.childNodes:
									if node4.nodeType != Node.TEXT_NODE and node4.nodeType != Node.COMMENT_NODE:
								
										out[i]= ('%s.%s' % (node3.nodeName,node4.nodeName), env_type,node4.attributes.getNamedItem('client_type').value, node4.attributes.getNamedItem('descr').value)
										i +=1
										print i
								#print node3.attributes.keys()
								#values.append("%s=%s@%s" % (node3.nodeName,node3.attributes.getNamedItem('schema').value, node3.attributes.getNamedItem('sid').value))
								#sys.exit(1)
						#_tree.append((node2.nodeName,values))
			#updateCache(cache,out)
		return out
		
	def getConnectList(self,configFile, environment):
		cache= '%s.%s.%s' % (gConnectListCache, os.path.basename(configFile).replace('.','_'),environment)
		#print cache
		out ={}
		if  use_cache and ifCacheExists(cache):
			
			out=readFromCache(cache)
			#print ta
			#sys.exit(1)
		else:
		
			x = configFile
			doc = xml.dom.minidom.parse(x)
			
			for node in doc.getElementsByTagName("app_spec"):
			  #isbn = node.getAttribute("isbn")
			  #L = node.getElementsByTagName("title")
			  for node2 in node.childNodes:
				#title = ""
				
				if node2.nodeType != Node.TEXT_NODE:
					#print node2.nodeType, node2.nodeName	
					#if node2.nodeName=='process_spec':
						#print dir(node2.attributes.tems)
						#values=[]
						#for aName, aValue  in node2.attributes.items():
						#	values.append("%s=%s" % (aName, aValue))				
						#_tree.append((node2.nodeName,values))
					if node2.nodeName=='connector':
						#print dir(node2.attributes.tems)
						i=0
						for node3  in node2.childNodes:
							if node3.nodeType != Node.TEXT_NODE and node3.nodeType != Node.COMMENT_NODE:
								print node3.nodeName								
								for node4  in node3.childNodes:
									
									if node4.nodeType != Node.TEXT_NODE and node4.nodeType != Node.COMMENT_NODE:
										if environment.upper()=='%s.%s' % (node3.nodeName.upper(),node4.nodeName.upper()):
											for node5  in node4.childNodes:
												if node5.nodeType != Node.TEXT_NODE and node5.nodeType != Node.COMMENT_NODE:										
													#print node4.nodeName
													#pprint (dir(node5.attributes))
													if node5.attributes.getNamedItem('schema'): #db login
														out[i]= (node5.nodeName, 'db_connect', '%s' % (node5.attributes.getNamedItem('schema').value), node5.attributes.getNamedItem('sid').value)
													else:
														if node5.attributes.getNamedItem('user'): #linux login
															print node5.attributes.keys()
															out[i]= (node5.nodeName, 'host_connect', '%s' % (node5.attributes.getNamedItem('user').value), node5.attributes.getNamedItem('host').value, node5.attributes.getNamedItem('home').value)
														else:
															assert 1==2, 'Undefined connect type %s' % node5.nodeName
													i+=1
													print i
								#print node3.attributes.keys()
								#values.append("%s=%s@%s" % (node3.nodeName,node3.attributes.getNamedItem('schema').value, node3.attributes.getNamedItem('sid').value))
								#sys.exit(1)
						#_tree.append((node2.nodeName,values))
			#updateCache(cache,out)
		return out