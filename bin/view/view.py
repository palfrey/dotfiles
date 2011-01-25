#!/usr/bin/python

import pygame,os
from pygame.locals import *
from directory import Directory
from os.path import dirname,join,realpath
from sys import argv

class Viewer:
	def __init__(self,dir):
		self.dir = dir
		pygame.init()
		modes = pygame.display.list_modes()
		self.screen = pygame.display.set_mode(modes[0],pygame.FULLSCREEN)
		self.loc = Directory(dir)
		self.myfont = pygame.font.Font(join(dirname(realpath(__file__)),"verdana.ttf"),32)
		self.index = 0
		self.list = [".."]+self.loc.listdir()
		self.collen = int((self.screen.get_size()[1]*1.0)/self.myfont.size(self.list[1])[1])
		print "collen",self.collen,self.myfont.size(self.list[1])[1],self.screen.get_size()[1]
		self.draw_list()
		clock = pygame.time.Clock()
		while 1:
			clock.tick(5)
			for event in pygame.event.get():
				if event.type is QUIT:
					return
				elif event.type is KEYDOWN:
					oldindex = self.index
					olddir = self.loc.path
					if event.key == K_ESCAPE:
						return
					elif event.key == K_DOWN or event.key == K_UP or event.key == K_LEFT or event.key == K_RIGHT:
						if event.key == K_DOWN or event.key == K_RIGHT:
							if event.key == K_DOWN:
								self.index +=1
							else: # K_RIGHT
								self.index += self.collen
								if self.index>=len(self.list):
									while self.index>=self.collen:
										self.index -= self.collen
							if self.index>=len(self.list):
								self.index -= len(self.list)
						else: # K_UP or K_LEFT
							if event.key == K_UP:
								self.index = self.index - 1
							else:
								self.index = self.index - self.collen
							if self.index<0:
								self.index = len(self.list)+self.index

					elif event.key == K_RETURN or event.key == K_BACKSPACE:
						if event.key == K_BACKSPACE:
							self.index = 0
							
						if self.loc.isfile(self.list[self.index]):
							if self.list[self.index][-4:]=='.cbz' or self.list[self.index][-4:]=='.zip' or self.list[self.index][-4:]=='.cbr' or self.list[self.index][-4:] == ".rar":
								if self.list[self.index]!="..":
									self.loc.chdir(self.list[self.index])
									self.list = [".."]+self.loc.listdir()
									self.index = 0
								else:
									place = self.loc.path[-1]
									self.loc.chdir("..")
									self.list = [".."]+self.loc.listdir()
									self.index=0

									for l in range(len(self.list)):
										if self.list[l]==place:
											self.index = l
											break
							else:
								self.index -=1
								self.browser()
								self.index +=1
								self.draw_list()
						else:
							if self.list[self.index]!="..":
								self.loc.chdir(self.list[self.index])
								self.list = [".."]+self.loc.listdir()
								self.index = 0
							else:
								place = [x for x in self.loc.path.split(os.sep) if x!=""][-1]
								print "dir",self.loc.path#,Directory.sep.findall(self.loc.path)
								self.loc.chdir("..")
								self.list = [".."]+self.loc.listdir()
								self.index=0
								print "looking for",place
								for l in range(len(self.list)):
									print self.list[l]
									if self.list[l]==place:
										self.index = l
										break
					elif event.key == K_END:
						self.index = len(self.list)-1
					elif event.key == K_HOME:
						self.index = 0
					elif event.key == K_DELETE:
						self.loc.delete(self.list[self.index])
						self.loc.clear_dir()
						self.list = [".."]+self.loc.listdir()
						if self.index == len(self.list):
							self.index -=1
						self.draw_list()
					else:
						print "No binding for "+str(pygame.key.name(event.key))
					if oldindex!=self.index or self.loc.path!=olddir:
						self.draw_list()
					

	def draw_list(self):
		self.screen.fill((0,0,0))
		try:
			height = self.myfont.size(self.list[1])[1]
		except IndexError:
			height=20
		except:
			print "list",self.list
			raise
		y = 0
		min_x = 20
		x = min_x
		max_x = 0
		for f in self.list:
			if self.myfont.size(f)[0]>max_x:
				max_x = self.myfont.size(f)[0]
				
		firstdraw = 0
		while self.index-firstdraw>self.collen*int(self.screen.get_size()[0]/(max_x*1.0)):
			if firstdraw+self.collen>self.index:
				break
			firstdraw += self.collen

		for i in range(firstdraw, len(self.list)):
			f = self.list[i]
			if not self.loc.isfile(f):
				f = "["+f+"]"
			if y == self.collen:
				y = 0
				x += max_x+min_x
			if self.index == i:
				self.screen.blit(self.myfont.render(f,True,(255,255,255),(255,0,0)),(x,y*height))
			else:
				self.screen.blit(self.myfont.render(f,True,(255,255,255)),(x,y*height))

			y += 1
		pygame.display.flip()		

	def browser(self):
		image = self.get_image(self.loc.listdir()[self.index])
		pygame.display.flip()
		while 1:
			for event in pygame.event.get():
				if event.type is QUIT:
					return
				elif event.type is KEYDOWN:
					if event.key == K_ESCAPE or event.key == K_BACKSPACE:
						return
					elif event.key in [K_PAGEDOWN, K_RIGHT, K_DOWN, K_PAGEUP, K_LEFT, K_UP]:
						if event.key in [K_PAGEDOWN, K_RIGHT, K_DOWN]:
							self.index = self.index + 1
							if self.index>len(self.loc.listdir())-1:
								self.index = len(self.loc.listdir())-1							
						else:
							self.index = self.index - 1
							if self.index<0:
								self.index = 0
						
						image = self.get_image(self.loc.listdir()[self.index])
						pygame.display.flip()
					else:
						print "No binding for "+str(pygame.key.name(event.key))

	def get_image(self,filename):
		try:
			print filename
			f = self.loc.open(filename)
			print f
			image = pygame.image.load(f,filename).convert()
			r=[0,0]
			for i in range(2):
				r[i] = self.screen.get_size()[i]/(image.get_size()[i]*1.0)
			if r[0]>r[1]:
				ratio = r[1]
			else:
				ratio = r[0]
			scr = (self.screen.get_size()[0]/(self.screen.get_size()[1]*1.0))
			imr = (image.get_size()[0]/(image.get_size()[1]*1.0))
			print "imr",scr,imr
			if imr<1.0:
				print "small ratio",ratio
				image = pygame.transform.rotate(image,90)
				for i in range(2):
					r[i] = self.screen.get_size()[i]/(image.get_size()[i]*1.0)
				if r[0]>r[1]:
					ratio = r[1]
				else:
					ratio = r[0]

			print ratio,scr,image.get_size(),(image.get_size()[0]*ratio,image.get_size()[1]*ratio),self.screen.get_size()
			image = pygame.transform.smoothscale(image,(image.get_size()[0]*ratio,image.get_size()[1]*ratio))
			self.screen.fill((0,0,0))
			self.screen.blit(image, ((self.screen.get_size()[0]-image.get_size()[0])/2, (self.screen.get_size()[1]-image.get_size()[1])/2))
			return image
		except pygame.error, message:
			if str(message) == "Unsupported image format":
				return None
			else:
				print "\""+str(message)+"\""
				raise

try:
	if len(argv) == 1:
		Viewer(os.getcwd())
	else:
		Viewer(realpath(argv[1]))
except:
	print "err"
	raise
