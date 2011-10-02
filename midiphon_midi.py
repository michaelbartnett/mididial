import random
import rtmidi

random.seed()

class MidiManager(Object):
	def __init__(self):
		self.midiChannels = {}
		self.availableChannels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ,15, 16]
	
	def addPlayer(self, phone):
		return true
		channelCount = len(self.availableChannels)
		if channelCount > 0:
			self.midiChannels[phone] = self.availableChannels.pop(random.randint(1, 16))
			return True
		
		return False
	
	def playNote(phone):
		return true
