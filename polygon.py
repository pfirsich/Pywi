import numpy as np
import pyglet.gl as gl
from pywi.transform import Transform, rotate
from trianglecollision import circleHitCircle
from pywi.timer import *

class _WrappingArray(np.ndarray):
	def getWrapped(self, index):
		return np.ndarray.__getitem__(self, index % len(self))
	def setWrapped(self, index, value):
		return np.ndarray.__setitem__(self, index % len(self), value)

def pointInTriangle(triangle, point):
	b0 = np.cross(triangle[1]-triangle[0], triangle[2]-triangle[0])
	if b0 != 0:
		b1 = np.cross(triangle[1]-point, triangle[2]-point) / b0
		b2 = np.cross(triangle[2]-point, triangle[0]-point) / b0
		b3 = 1.0 - b1 - b2
		return (b1>0) and (b2>0) and (b3>0)
	else:
		return False
		
def projectOnAxis(axis, point):
	return np.dot(axis, point)
		
def inInterval(int, v):
	return int[0] <= v <= int[1]
	
def lenInterval(int):
	return int[1] - int[0]

# Interval intA ist left from intB
def overlapInterval(intA, intB):
	d = intA[1] - intB[0]
	if d > 0:
		return d
		
	return None
			
def orthoVector(vec):
	return np.array([vec[1], -vec[0]], dtype = float)

#def pointInTriangleS( triPoints, point ):
#	rpoint = point - triPoints[0]
#	a = triPoints[1] - triPoints[0]
#	b = triPoints[2] - triPoints[0]
#	coeff = np.linalg.solve(np.array([a,b]).T, point - triPoints[0])
#	return coeff.sum() < 1.0 and (coeff > 0.0).all()

class Polygon(object):
	def __init__(self, list, name='unnamed', calcGeometricProperties = True):
		self._data = np.array(list, dtype=float)
		self.name = name
		if calcGeometricProperties:
			self.centroid()
			self.radius()
			self.getEdgeDirections()
			self.boundingBox()

	def __getitem__(self, index):
		return self._data[index]

	def __str__(self):
		return str(self._data)

	def __repr__(self):
		return repr(self._data)

	def __len__(self):
		return len(self._data)

	def triangulate(self):
		triangles = []
		list = self._data.copy().view(_WrappingArray)
		i = 0
		failedTries = -1
		while len(list) > 3:
			failedTries += 1
			if (failedTries > len(list)*50):
				print "List:",list
				raise RuntimeError("could not triangulate polygon '%s'" % self.name)
			p1 = list.getWrapped(i-1)
			p = list.getWrapped(i)
			p2 = list.getWrapped(i+1)
			l = np.cross(p1-p, p2-p)
			if l < 0:
				triangle = Triangle(np.array([p1,p,p2]))
				triangle.name = self.name
				for point in list:
					if (point==p1).all() or (point==p).all() or (point==p2).all():
						continue
					if triangle.contains(point):
						break
				else: # nobreak ==> no other point is in triangle
					triangles.append(triangle)
					list = np.delete(list, i, 0)
					failedTries = 0
			i = (i+1) % len(list)
		else:
			points = []
			for i in xrange(3):
				points.append(list.getWrapped(i))
			triangles.append(Triangle(points))
		return triangles

	def isClockWise(self):
		sum = 0
		for i in xrange(0,len(self._data)-1):
			sum += (self._data[i+1][0]-self._data[i][0]) * (self._data[i+1][1]+self._data[i][1])
		return sum > 0

	def isCounterClockWise(self):
		return not self.isClockWise()

	def reverse(self):
		self._data = self._data[::-1]

	def removeDuplicates(self):
		uniqueL = []
		for p in map( tuple, self._data ):
			if not p in uniqueL:
				uniqueL.append(p)
		self._data = np.array(uniqueL, dtype=float)

	def normalize(self):
		self.removeDuplicates()
		if self.isClockWise():
			self.reverse()
			
	#def isConvex(self): Cross product with all the edges. If they all have the same sign -> YesYoah.

	def compileDisplayList(self, triangulate=True):
		quad = gl.glGenLists(1)
		gl.glNewList(quad, gl.GL_COMPILE)
		if triangulate:
			gl.glBegin(gl.GL_TRIANGLES)
			triangles = self.triangulate()
			for triangle in triangles:
				for node in triangle:
					gl.glTexCoord2f(node[0], node[1])
					gl.glVertex2f(node[0], node[1])
			gl.glEnd()
		else:
			gl.glBegin(gl.GL_LINE_STRIP)
			for node in self:
				gl.glVertex2f(node[0], node[1])
			gl.glEnd()
		gl.glEndList()
		return quad
		
	def centroid(self):
		center = np.sum(self._data, axis = 0) / len(self._data)
		self._centroid = center
		return center
		
	def radius(self):
		maxRadius = 0
		center = self.centroid()
		for point in self._data:
			r = np.linalg.norm(center - point)
			if r > maxRadius:
				maxRadius = r
		self._radius = maxRadius
		return maxRadius
		
	def boundingBox(self):
		transposed = self._data.T
		x = transposed[0]
		y = transposed[1]
		self._boundingBox = np.array([[min(x),max(x)],[min(y),max(y)]], dtype=float)
		return self._boundingBox
		
	def getEdgeDirections(self):
		edges = []
		for i in xrange(len(self)):
			ni = (i + 1) % len(self)
			r = self[ni] - self[i]
			n = np.linalg.norm(r)
			if n > 0:
				edges.append(r/n)
		self._edgeDirections = edges
		return edges
	
	
	def checkSATAxis(self, other, axis):
		t = projectOnAxis(axis, self[0])
		A = [t, t]
		for point in self._data:
			p = projectOnAxis(axis, point)
			if p < A[0]:
				A[0] = p
			elif p > A[1]:
				A[1] = p
			
		t = projectOnAxis(axis, other[0])
		B = [t, t]
		for point in other._data:
			p = projectOnAxis(axis, point)
			if p < B[0]:
				B[0] = p
			elif p > B[1]:
				B[1] = p
				
		if B[0] < A[0]:
			A, B = B, A
		
		return overlapInterval(A,B)
		
	def transformed(self, transf):
	
		pol = Polygon( map( transf.apply, self._data ), False )
		pol._radius = self._radius * max(transf.scale)
		pol._centroid = transf.apply(self._centroid)
		pol._edgeDirections = map(lambda e : rotate(transf.angle, e), self._edgeDirections)
		return pol
		
	
	def collidesPolygon_convex(self, other):
		edges = self._edgeDirections
		edges.extend(other._edgeDirections)
		axes = map( orthoVector, edges ) # alternative: process entire list at once
		MTV = None
		minimalOverlap = 1e12
		for axis in axes:
			overlap = self.checkSATAxis(other, axis)
			
			if overlap == None:
				return None
			
			aoverlap = abs(overlap)
			if aoverlap < abs(minimalOverlap):
				MTV = axis * overlap
				minimalOverlap = aoverlap
				
		if np.dot(MTV, other._centroid - self._centroid) > 0.0:
			MTV *= -1.0
				
		return MTV

def dumpPolygons(file, polygons):
	for polygon in polygons:
		file.write('## %s\n' % polygon.name)
		triangles = polygon.triangulate()
		for triangle in triangles:
			file.write('%s\n' % ' '.join('%.9g,%.9g' % (point[0], point[1]) for point in triangle))
		file.write('\n')

def loadPolygons(file):
	polygons = []
	currentName = None

	for line in file:
		line = line.strip()
		if len(line) == 0:
		   continue
		elif line.startswith('##'):
			currentName = line.partition(' ')[2]
		else:
			points = line.split()
			triangle = []
			for point in points:
				x,y = point.split(',')
				x = float(x)
				y = float(y)
				triangle.append((x,y))
			triangle = Triangle(triangle)
			triangle.name = currentName
			polygons.append(triangle)
	return polygons
		

class Triangle(Polygon):
	def __init__(self, list):
		super(Triangle, self).__init__(list)
		if len(self._data) != 3:
			raise RuntimeError("no triangle (%d nodes)" % len(self._data))

	def contains(self, point):
		b0 = np.cross(self._data[1]-self._data[0], self._data[2]-self._data[0])
		if b0 != 0:
			b1 = np.cross(self._data[1]-point, self._data[2]-point) / b0
			b2 = np.cross(self._data[2]-point, self._data[0]-point) / b0
			b3 = 1.0 - b1 - b2
			return (b1>0) and (b2>0) and (b3>0)
		else:
			return False
	
	def containsTolerance(self, point, delta=0.01):
		rpoint = point - self._data[0]
		a = self._data[1] - self._data[0]
		b = self._data[2] - self._data[0]
		try:
			coeff = np.linalg.solve(np.array([a,b]).T, rpoint)
		except np.linalg.linalg.LinAlgError:
			#print "Exception:",e
			#print "Triangle:",self
			#print "Point:",point
			#print "Matrix:",np.array([a,b]).T
			#print "Relative Point:",rpoint
			#print "A:",a
			#print "B:",b
			return False
	
		return coeff.sum() < 1.0 + delta and (coeff > -delta).all()

	def triangulate(self):
		return [self]

