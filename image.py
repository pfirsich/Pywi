import pyglet
from pyglet.gl import *
from collections import defaultdict

def getImage(name, file=None):
	if getImage.imageMap[name] == None:
		getImage.imageMap[name] = Image(name, file=file)
	return getImage.imageMap[name]
getImage.imageMap = defaultdict(lambda: None)

def clearImageCache():
	getImage.imageMap = defaultdict(lambda: None)
	
def bindImage(img):
	if img == None:
		currentTarget = None
	else:
		currentTarget = img._texture.target
	
	if Image.lastBoundTarget != currentTarget:
		if Image.lastBoundTarget != None:
			glDisable(Image.lastBoundTarget)
			
		if currentTarget != None:
			glEnable(currentTarget)

		Image.lastBoundTarget = currentTarget

	if Image.lastBound != img and img != None:
		img.bind()
		Image.lastBound = img

class Image(object):
	lastBound = None
	lastBoundTarget = None
	
	def __init__(self, path = None, file=None):
		self._pimage = None
		self._textureId = None
		self.width = 0
		self.height = 0
	
		if path != None:
			self.loadFile(path, file=file)
			
	def loadFile(self, path, file=None):
		self._pimage = pyglet.image.load(path, file=file)
		self._texture = self._pimage.get_texture(rectangle=True)
		
		if self._texture.target == GL_TEXTURE_2D:
			glBindTexture(self._texture.target, self._texture.id)
			glTexParameteri(self._texture.target, GL_TEXTURE_WRAP_S, GL_REPEAT)
			glTexParameteri(self._texture.target, GL_TEXTURE_WRAP_T, GL_REPEAT)
		
		self.width = self._pimage.width
		self.height = self._pimage.height
		
	def textureId(self):
		return self._texture.id
		
	def bind(self):
		glBindTexture( self._texture.target , self._texture.id )