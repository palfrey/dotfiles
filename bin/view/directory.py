from zipfile import ZipFile
from rarfile import RarFile
import os,re
from types import *
from StringIO import StringIO
from shutil import rmtree

class TreeRar(RarFile):
	def rar_dirs(self,item):
		if not hasattr(item,"filename"):
			print "no filename",item
			return
		fname = item.filename
		print "item",fname
		if not hasattr(self,"_tree"):
			self._tree = {}
		bits = fname.split("\\")
		where = self._tree
		for b in bits[:-1]:
			if b not in where:
				where[b] = {}
			where = where[b]
		where[bits[-1]] = fname
		#print "tree",self._tree

	def __init__(self,fname):
		#RarFile.__init__(self,fname,info_callback=self.rar_dirs)
		RarFile.__init__(self,fname)

class ZipDir:
	splitter = re.compile(r"[/\\]")
	def __init__(self,parent,fname):
		self.parent = parent
		self.file = fname
		if fname.find("cbr")!=-1 or fname.find("rar")!=-1:
			self.zipfile = TreeRar(self.file)
			print "doing rar",self.file
			self.israr = True
		else:
			self.zipfile = ZipFile(self.file)
			self.israr = False
		list = self.zipfile.infolist()
		self.dir = {}
		for f in list:
			path = ZipDir.splitter.split(f.filename)
			print "f.file",f.filename,path
			root = self.dir
			while len(path)>1:
				if not root.has_key(path[0]) or root[path[0]] == "":
					root[path[0]] = {}
				root = root[path[0]]
				path = path[1:]
			if path[0]!="" and (path[0] not in root or root[path[0]]=={}):
				try:
					root[path[0]] = ""
				except TypeError:
					print "dir",self.dir
					print "root",root,path
					raise
		
		self.path = []
		self.curdir = self.dir
		print "self.curdir",self.curdir

	def listdir(self):
		k = self.curdir.keys()
		k.sort()
		return k

	def chdir(self,path):
		ret = self._chdir(path,self.path,self.curdir)
		if len(ret)==0:
			return False
		(self.path,self.curdir) = ret
		#assert type(self.curdir) == DictType,(self.path,self.curdir)
		return True
	
	def _chdir(self,path,oldpath,oldcurdir):
		segments = filter(lambda x:x!='',ZipDir.splitter.split(path))
		#print "segments",segments,path,self.path
		for s in segments:
			if s=="..":
				if len(oldpath)==0:
					return []
				else:
					oldpath = oldpath[:-1]
					oldcurdir = self.dir
					for p in oldpath:
						oldcurdir = oldcurdir[p]
					print "ocd,op",oldcurdir,oldpath
					if len(oldcurdir)==1 and len(oldpath)==0:
						print "blank root!"
						self.parent.chdir("..")
						return []
					
			else:
				if not oldcurdir.has_key(s):
					return []
				else:
					oldpath += [s]
					oldcurdir = oldcurdir[s]
		return [oldpath,oldcurdir]
	
	def isfile(self,filename):
		ret = self._chdir(os.path.dirname(filename),self.path,self.curdir)
		#print "Zip: change dir",os.path.dirname(filename),os.path.basename(filename),ret,self.path
		if len(ret)==0:
			return False
		(newpath,newcurdir) = ret
		if newcurdir.has_key(os.path.basename(filename)):
			ret = type(newcurdir[os.path.basename(filename)])
			print "typing",filename,ret
			return ret!= DictType
		else:
			return False
	
	def open(self,filename):
		f = "/".join(self.path+[filename])
		return StringIO(self.zipfile.read(f))
		
class Directory:
	#sep = re.compile(r"((?:[A-Za-z]:)|(?:[A-Za-z0-9\-_ ,\.()\[\]]+)|#)|[/\\]")
	sep = re.compile(r"((?:[A-Za-z]:)|(?:[&#A-Za-z0-9\-_ ,!\'\.~()\[\]]+))|[/\\]")

	def __init__(self,path):
		self.path = path
		self.dir = None
		self.subdir = None
		self.chdir(path)

	def clear_dir(self):
		self.dir = None
	
	def listdir(self):
		if self.subdir!=None:
			return self.subdir.listdir()
		
		self.dir = os.listdir(self.path)
		self.dir.sort()
		return self.dir
	
	def isfile(self,filename):
		if self.subdir!=None:
			return self.subdir.isfile(filename)
		else:
			return os.path.isfile(os.path.join(self.path,filename))
	
	compfiles = {"cbz":ZipDir,"zip":ZipDir,"cbr":ZipDir, "rar":ZipDir}
	
	def chdir(self,path):
		print "chdir path",path
		if (os.path.splitdrive(self.path)[0]=='' and path[0]==os.sep) or (path[0].lower()>='a' and path[0].lower()<='z' and len(path)>1 and path[1] == ':'):
			self.path = ""
		
		sections = filter(lambda x:x!='',Directory.sep.findall(self.path)+Directory.sep.findall(path))
		print "sections",sections,self.path,path,Directory.sep.findall(path)
		for x in range(1,len(sections)):
			if len(sections)-1<x:
				break
			if sections[x] == '..':
				if len(sections)>2 or (len(sections)>1 and os.path.splitdrive(self.path)[0]==''):
					del sections[x-1]
					del sections[x-1]
				else:
					del sections[x]
			
		print "join",sections,os.sep.join(sections)
		self.subdir = None
		for s in range(len(sections)):
			for c in Directory.compfiles.keys():
				if sections[s][-(len(c)+1):] == '.'+c and self.isfile(os.sep+os.sep.join(sections[:s+1])):
					self.subdir = Directory.compfiles[c](self,os.sep+os.sep.join(sections[:s+1]))
					if not self.subdir.chdir(os.sep.join(sections[s+1:])):
						return
					print "ZipDir",os.sep.join(sections[:s+1]),os.sep.join(sections[s+1:])
					#sections = sections[:s+1]
					break

		self.path = os.sep+os.sep.join(sections)+os.sep
		self.dir = None
	
	def open(self,filename):
		if self.subdir!=None:
			return self.subdir.open(filename)
		
		return file(os.path.join(self.path,filename),'rb')
		
	def delete(self,filename):
		fullpath = os.path.join(self.path,filename)
		print "delete",fullpath
		if os.path.isdir(fullpath):
			rmtree(fullpath)
		else:
			os.remove(fullpath)

