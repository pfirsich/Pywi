import bisect

from pyglet.gl import *

from npshortcuts import *
from renderable import *
import image
import core
from transform import Transform

class BlendTypes:
	NONE, ADDITIVE, ADDITIVE_WEIGHED, MIX = range(4)

def applyBlendState(state):
	if applyBlendState.lastState != state:
		if applyBlendState.lastState == BlendTypes.NONE:
			glEnable( GL_BLEND )
			glDisable( GL_DEPTH_TEST )
			
		if state == BlendTypes.NONE:
			glDisable( GL_BLEND )
			glEnable( GL_DEPTH_TEST )
		elif state == BlendTypes.ADDITIVE:
			glBlendFunc( GL_ONE, GL_ONE )
		elif state == BlendTypes.ADDITIVE_WEIGHED:
			glBlendFunc( GL_SRC_ALPHA, GL_ONE )
		elif state == BlendTypes.MIX:
			glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
	
		applyBlendState.lastState = state
applyBlendState.lastState = BlendTypes.NONE
	
class Renderable(object):
	renderableList = []
	finishList = []
	renderedLastFrame = 0
	def __init__(self):
		self.enabled = True
		Renderable.finishList.append(self)
		
	def delete(self):
		for r in Renderable.renderableList:
			if r[1] == self:
				Renderable.renderableList.remove(r)
				break
	
	def finish(self):
		bisect.insort(Renderable.renderableList, self)
		
	def sortKey(self):
		raise NotImplementedError
		
	def __lt__(self, other):
		return self.sortKey() < other.sortKey()
	
	def render(self):
		raise NotImplementedError

class Sprite(Renderable):
	def __init__(self):
		self.image = None
		self.transform = Transform()
		self.color = vec4(1,1,1,1)
		self.blending = BlendTypes.NONE
		self.tags = ""
		self.depth = 0.0 # Range: [-1,1]. Otherwise: crazy things happen in draw call sorting (you don't want that)
		self.geometry = core.globs.quad
		super(Sprite, self).__init__()
		self.textureScale = vec2(1,1)
		
	def sortKey(self): #TODO: IMPLEMENT!!
		alphabit = (self.blending != BlendTypes.NONE)
		depth = (self.depth + 1.0) * 0.5 * 1024
		if alphabit == False:
			depth = 1024 - depth
		return 2048 * alphabit + depth
		
	def render(self):
		glPushMatrix( )
		glTranslatef( self.position[0], self.position[1], self.depth )
		#print self.tags, self.depth
		glRotatef( self.angle, 0.0, 0.0, 1.0 )
		glTranslatef( self.transform.absoluteOffset[0], self.transform.absoluteOffset[1], 0 )
		
		w, h = 1.0, 1.0
		if self.image != None:
			w, h = self.image.width, self.image.height
		glScalef( self.scale[0] * w, self.scale[1] * h, 1.0 )
		glTranslatef( self.offset[0], self.offset[1], 0.0 )
		glColor4f( self.color[0], self.color[1], self.color[2], self.color[3] )

		isRect = (self.image != None) and (self.image._texture.target != GL_TEXTURE_2D)
		texScale = self.textureScale
		if isRect:
			texScale = texScale * vec2(w,h)
			
		glMatrixMode(GL_TEXTURE)
		glPushMatrix()
		glScalef(texScale[0], texScale[1], 0.0)

		image.bindImage(self.image)
		applyBlendState(self.blending)
		glCallList(self.geometry)
		
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
		glPopMatrix()
	
	@property
	def position(self):
		return self.transform.position
		
	@position.setter
	def position(self, value):
		self.transform.position = value
		
	@property
	def offset(self):
		return self.transform.offset
		
	@offset.setter
	def offset(self, value):
		self.transform.offset = value
		
	@property
	def scale(self):
		return self.transform.scale
		
	@scale.setter
	def scale(self, value):
		self.transform.scale = value
		
	@property
	def angle(self):
		return self.transform.angle
		
	@angle.setter
	def angle(self, value):
		self.transform.angle = value