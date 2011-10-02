import random
import rtmidi
import threading

random.seed()

class PhoneMusician(object):
	def __init__(self, phoneNumber, midiChannel):
		self.midiChannel = midiChannel
		self.phoneNumber = phoneNumber
		self.octaveModifier = 0
		self.semitoneModifier = 0
		self.noteMap = {
			'1' : 60,
			'2' : 62,
			'3' : 64,
			'4' : 65,
			'5' : 67,
			'6' : 69,
			'7' : 71,
			'8' : 72,
			'9' : 74,
			'0' : 76,
			'*' : 77,
			'#' : 79,
		}
	
	def getMidiChannel():
		return self.midiChannel
	
	def getNoteOnMessage(self, digit):
		return rtmidi.MidiMessage.noteOn(1, self.noteMap[digit] + self.octaveModifier * 8 + self.semitoneModifier, 127)

	def getNoteOffMessage(self, digit):
		return rtmidi.MidiMessage.noteOff(1, self.noteMap[digit] + self.octaveModifier * 8 + self.semitoneModifier)

	def octaveUp(amount):
		self.octaveModifier += amount
	
	def octaveDown(amount):
		self.octaveModifier -= amount
	
	def semitoneUp(amount):
		self.semitoneModifier += amount

	def semitoneDown(amount):
		self.semitoneModifier -= amount
			

class MidiManager(object):
	MidiPortName = "MIDIPHON"
	def __init__(self):
		self.midiChannels = {}
		self.availableChannels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 ,15, 16]
		self.mout = rtmidi.RtMidiOut()
		self.min = rtmidi.RtMidiIn()
		self.min.openVirtualPort(MidiManager.MidiPortName)
		self.mout.openVirtualPort(MidiManager.MidiPortName)
		self.midiPort = -1
		for i in range(0, self.mout.getPortCount()):
			if self.mout.getPortName(i) == MidiManager.MidiPortName:
				self.midiPort = i
				return
		
		if self.midiPort == -1:
			raise Exception('Epic failure of finding midi channel I just opened.')
		


	def addPlayer(self, phone):
		if self.midiChannels.has_key(phone):
			return True
		
		
		channelCount = len(self.availableChannels)
		if channelCount > 0:
			self.midiChannels[phone] = PhoneMusician(phone, self.availableChannels.pop(random.randint(1, channelCount) - 1))
			return True
		
		return False
	
	def removePlayer(self, phone):
		if self.midiChannels.has_key(phone):
			player = self.midiChannels.pop(phone)
			channelNumber = player.midiChannel
			print "Removing player {0} with midi channel {1}".format(phone, channelNumber)
			self.availableChannels.append(channelNumber)

	
	def playNote(self, phone, digit):
		if self.midiChannels.has_key(phone):
			msg = self.midiChannels[phone].getNoteOnMessage(digit)
			print "Sending midi message: channel={0} note={1} vel={2}".format(msg.getChannel(), msg.getNoteNumber(), msg.getVelocity())
			self.mout.sendMessage(msg)
			t = threading.Timer(1.25, self.stopNote, [phone, digit])
			t.start()

			return True


	def stopNote(self, phone, digit):
		msg = self.midiChannels[phone].getNoteOffMessage(digit)
		print "Sending midi message: channel={0} note={1}".format(msg.getChannel(), msg.getNoteNumber())
		self.mout.sendMessage(msg)
