from collections import defaultdict

import pyglet
#pyglet.options['debug_gl'] = False

from pyglet.gl import *

from renderable import *
from sprite import *
from timer import Timer
from transform import Transform

import time

class globs:
	quad = 0
	
class UpdateObject(object):
	def __init__(self, engine):
		engine.updateObjects.append(self)
		self.engine = engine
		
	def update(self):
		raise NotImplementedError
	
class Engine:
	def __init__(self, xres, yres, title, fullscreen = False, vsync = False, samples = 0):
		self._closeIssued = False
		self._window = None
		self.gameTime = 0

		self.keyMap = defaultdict(lambda: False)
		self.mousePosition = vec2(0,0)
		self.mouseDelta = vec2(0,0)
		self.mouseWheelPosition = 0

		self.cameraTransform = Transform()
		
		self.resolution = vec2(0,0)
		self.updateObjects = []
		
		self._init(xres, yres, title, fullscreen, vsync, samples)
		
		self.makeRenderStats = False
		self.renderStats = {}
	
	def prepareFrame(self):
		pass

	# Pywi is using a fixed timestep game loop and calls the stepCallback-function as long as the dt estimated for one call does
	# not correspond to the "dt" in the real world
	def run(self, dt): 
		"""Initialized Pywi and enters the mainloop.
			
		stepCallback - This callback is called until the gameTime is bigger or equal to the real time.
		dt - The time gameTime is incremented by in very simulation step
		title - The window title
		xres - The width of the window in pixels
		yres - The height of the window in piyels
		fullscreen - If the window created should be fullscreen (boolean)
		vsync - If vsync should be enabled (boolean)
		"""
		
		mainLoopTimer = Timer()
		fpsTimer = Timer()
		
		#bench = Timer()
		#stepcount = 0
		#stepcum = 0
	
		#framecount = 0
		#framecum = 0
		
		fpsRendered = 0
		while not self._closeIssued:
			while not self._closeIssued and self.gameTime < mainLoopTimer.total():
				#bench.reset()
				#print mainLoopTimer.total(),"-",self.gameTime,"=",mainLoopTimer.total()-self.gameTime
				self._window.dispatch_events()
				for obj in self.updateObjects:
					obj.update()
				
				self.step()
				self.gameTime += dt
				#d = bench.delta()
				#stepcount += 1
				#stepcum += d
				#print "STEP current:", d
				#print "STEP Avrg time:", float(stepcum)/stepcount
			
			fpsRendered += 1
			#bench.reset()
			self.prepareFrame()
			self._updateFrame()
			#d = bench.delta()
			#framecount += 1
			#framecum += d
			#print "FRAME current:", d
			#print "FRAME Avrg time:", float(framecum)/framecount
			
			if fpsTimer.total() > 1.0:
				self._window.set_caption( self._title + " - FPS: " + str(fpsRendered) )
				fpsRendered = 0
				fpsTimer.reset()
			
			
		#print "STEP COUNT: %d" % stepcount
		#print "FRAME COUNT: %d" % framecount
		
		self._terminate()
		self.terminate() # Should be overload

	def step(self):
		pass

	def issueClose(self):
		"""Call this function to issue a close request to Pywi"""
		self._closeIssued = True
		pass
		
	def _init(self, xres, yres, title, fullscreen, vsync, multisamples):
		config = Config()
		config.buffer_size = 32
		config.depth_size = 24
		config.double_buffer = True
		if multisamples > 0:
			config.sample_buffers = 1
			config.samples = multisamples
			
		if fullscreen:
			self._window = pyglet.window.Window(config = config, caption = title, resizable = False, fullscreen = True, vsync = vsync) # xres, yres may not be specified with fullscreen
		else:
			self._window = pyglet.window.Window(config = config, width = xres, height = yres, caption = title, resizable = False, fullscreen = False, vsync = vsync)
			
		self.resolution = vec2(xres, yres)
		self._title = title
		@self._window.event
		def on_close():
			self._closeIssued = True
		
		@self._window.event
		def on_key_press( symbol, modifier ):
			self.keyMap[symbol] = True
			return True
		
		@self._window.event	
		def on_key_release( symbol, modifier ):
			self.keyMap[symbol] = False
		
		@self._window.event
		def on_mouse_motion( x, y, dx, dy ):
			self.mousePosition = vec2(x,y)
			self.mouseDelta = vec2(dx,dy)
		
		@self._window.event
		def on_mouse_press( x, y, button, modifiers ):
			self.keyMap[button] = True
		
		@self._window.event
		def on_mouse_release( x, y, button, modifiers ):
			self.keyMap[button] = False
			
		@self._window.event
		def on_mouse_scroll(x, y, x_scroll, y_scroll):
			self.mouseWheelPosition += y_scroll
		
		glViewport( 0, 0, xres, yres )
		glMatrixMode( GL_PROJECTION )
		glLoadIdentity( )
		glOrtho( 0.0, xres, 0.0, yres, -1.0, 1.0 )
		
		glMatrixMode( GL_TEXTURE )
		glLoadIdentity()
		
		glMatrixMode( GL_MODELVIEW )
		glLoadIdentity( )
		

		glAlphaFunc( GL_GREATER, 0.01 )
		glEnable( GL_ALPHA_TEST )

		glEnable( GL_DEPTH_TEST )

		glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )

		globs.quad = glGenLists( 1 )
		glNewList( globs.quad, GL_COMPILE )
		glBegin( GL_TRIANGLE_STRIP )
		glTexCoord2i( 0, 1 )
		glVertex2i( 0, 1 )
		glTexCoord2i( 0, 0 )
		glVertex2i( 0, 0 )
		glTexCoord2i( 1, 1 )
		glVertex2i( 1, 1 )
		glTexCoord2i( 1, 0 )
		glVertex2i( 1, 0 )
		glEnd( )
		glEndList( )

	def _terminate(self):
		self._window.close()
		
	def terminate(self):
		pass

	def _updateFrame(self):		
		self._window.clear()
		
		#last = ("",-1)
		for r in Renderable.finishList:
			r.finish()
			#ident = (r.tags, r.sortKey())
			#if ident != last:
			#	last = ident
			#	print ident
			#	print r.depth
		Renderable.finishList = []

		glPushMatrix()
		glTranslatef( self.cameraTransform.absoluteOffset[0], self.cameraTransform.absoluteOffset[1], 0 )
		glRotatef( -self.cameraTransform.angle, 0.0, 0.0, 1.0 )
		glScalef( self.cameraTransform.scale[0], self.cameraTransform.scale[1], 1.0 )
		glTranslatef( -self.cameraTransform.position[0], -self.cameraTransform.position[1], 0 )

		for r in Renderable.renderableList:
			if r.enabled:
				r.render()
		glPopMatrix()
		
		self._window.flip()
		pass

def clearColor(col):
	glClearColor(col[0], col[1], col[2], col[3])
	
		