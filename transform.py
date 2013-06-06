import math

import numpy as np

import npshortcuts as nps

def rotate(angle, vec):
	rad = angle / 180.0 * math.pi
	s = math.sin(rad)
	c = math.cos(rad)
	rot = np.array([[c,-s],[s,c]], dtype = float)
	return np.dot( rot, vec )

class Transform(object):
	def __init__(self):
		self.position = nps.vec2(0,0)
		self.offset = nps.vec2(0,0)
		self.absoluteOffset = nps.vec2(0,0)
		self._scale = nps.vec2(1,1)
		self.angle = 0
		
	@property
	def scale(self):
		return self._scale
		
	@scale.setter
	def scale(self, value):
		if not hasattr(value, "__getitem__"):
			self._scale = nps.vec2(value,value)
		else:
			self._scale = value
		
	def apply(self, point):
		return self.position + rotate(self.angle, (point + self.offset) * self._scale + self.absoluteOffset)