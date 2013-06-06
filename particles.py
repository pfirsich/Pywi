import numpy as np

from sprite import *
from core import UpdateObject

def velocityIntegrationDamping(dt, damping = 1.0):
	def updateFunction(particle):
		particle.velocity -= damping * particle.velocity * dt
		particle.position += particle.velocity * dt
	return updateFunction

def velocityIntegration(dt):
	def updateFunction(particle):
		particle.position += particle.velocity * dt
	return updateFunction
	
class Particle(object):
	def __init__(self):
		self.position = vec2(0,0)
		self.velocity = vec2(0,0)
		self.scale = vec2(0,0)
		self.angle = 0
		self.color = vec4(1,1,1,1)
		self.age = 0
		
	def kill(self):
		self.parent.particles.remove(self)
	
class ParticleGroup(Sprite, UpdateObject):
	def __init__(self, updateFunction, engine):
		Sprite.__init__(self)
		UpdateObject.__init__(self, engine)
		self.updateFunction = updateFunction
		self.particles = []
		self.lastActive = 0
		
	def spawn(self, number):
		for i in xrange(number):
			new = Particle()
			self.particles.append(new)
			new.parent = self
			yield new
		
	def render(self):
		image.bindImage(self.image)
		applyBlendState(self.blending)

		self.lastActive = 0
		for particle in self.particles:
			self.lastActive += 1

			glPushMatrix()
			glTranslatef(particle.position[0], particle.position[1], self.depth)
			glRotatef(particle.angle, 0.0, 0.0, 1.0)
			
			w, h = 1.0, 1.0
			if self.image != None:
				w, h = self.image.width, self.image.height
			glScalef(particle.scale[0] * w, particle.scale[1] * h, 1.0)
			glTranslatef(-0.5, -0.5, 0.0)

			glColor4f(particle.color[0],particle.color[1],particle.color[2],particle.color[3])

			glCallList(core.globs.quad)

			glPopMatrix()
		
	def update(self):
		for particle in self.particles:
			self.updateFunction(particle)
			particle.age += 1