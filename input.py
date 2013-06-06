import core

class ButtonInput(core.UpdateObject):
	def __init__(self, engine):
		super(ButtonInput, self).__init__(engine)

	def pressed(self):
		raise NotImplementedError
	
	def triggered(self):
		raise NotImplementedError
		
	def released(self):
		raise NotImplementedError
	
class MouseKeyboard(ButtonInput):
	def __init__(self, key, engine):
		super(MouseKeyboard, self).__init__(engine)
		self._key = key
		self._pressed = False
		self._lastPressed = False
	
	def update(self):
		self._lastPressed = self._pressed
		self._pressed = self.engine.keyMap[self._key]
		
	def pressed(self):
		return self._pressed
		
	def triggered(self):
		return self._pressed and not self._lastPressed
		
	def released(self):
		return not self._pressed and self._lastPressed
		
#class JoypadButton