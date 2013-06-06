"""This module provides time functions."""

import time
from collections import defaultdict 

class Timer(object):
	"""A unified wrapper for Python's time methods."""
	def __init__(self):
		self.reset()

	def reset(self):
		"""Sets the start (offset) of the timer."""
		self._reference = time.clock()
		self._lastTick = self._reference

	def total(self):
		"""Returns the total time ellapsed since last reset or creation of the timer."""
		return time.clock() - self._reference

	def delta(self):
		"""Returns the time delta since last invocation of this method."""
		now = time.clock()
		delta = now - self._lastTick
		self._lastTick = now
		return delta

class BenchmarkTimer(object):
	values = defaultdict(list)
	def __init__(self, name=None):
		self.name = name
		self._start = None
		
	def __enter__(self):
		self._start = time.clock()
		
	def __exit__(self, exc_type, exc_value, traceback):
		ende = time.clock()
		duration = ende - self._start
		BenchmarkTimer.values[self.name].append(duration)
		
	@staticmethod
	def request(name):
		import numpy as np
		durations = np.array(BenchmarkTimer.values[name])
		if len(durations) == 0:
			print "Benchmark Timer '%s' was not called." % (name)
		else:
			mean = np.mean(durations)
			std = np.std(durations) / np.sqrt(len(durations))
		print "Benchmark Timer '%s' (called %d times): (%.5f +- %.5f) ms" % (name, len(durations), 1000.0*mean, 1000.0*std)
		