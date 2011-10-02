import random
import rtmidi
import threading
from midiutil.MidiFile import MIDIFile
import time
import uuid
import ftplib

random.seed()

def uploadMidiFile(filename):
	ftp = ftplib.FTP('midiphon.bartnett.com', 'midiphon_uploader', 'grantophone')
	with mf = open(filename):
		ftp.storbinary('STOR ' + filename, mf)
	
	link = getBitlyLink()
	sendBitlyLink(link)

def getBitlyLink(url):
	pass

def sendBitlyLink(link):
	pass

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
			# '*' : 77,
			# '#' : 79,
		}
	
	def getMidiChannel():
		return self.midiChannel
	
	def getNoteOnMessage(self, digit):
		if digit == '*':
			self.octaveDown(1)
			return None
		elif digit == '#':
			self.octaveUp(1)
			return None
		return rtmidi.MidiMessage.noteOn(self.midiChannel, self.noteMap[digit] + self.octaveModifier * 12 + self.semitoneModifier, 127)

	def getNoteOffMessage(self, digit):
		if digit == '*' or digit == '#':
			return None
		return rtmidi.MidiMessage.noteOff(self.midiChannel, self.noteMap[digit] + self.octaveModifier * 12 + self.semitoneModifier)

	def octaveUp(self, amount):
		self.octaveModifier += amount
	
	def octaveDown(self, amount):
		self.octaveModifier -= amount
	
	def semitoneUp(self, amount):
		self.semitoneModifier += amount

	def semitoneDown(self, amount):
		self.semitoneModifier -= amount
			

class MidiManager(object):
	MidiPortName = "MIDIPHON"
	def __init__(self):
		self.midiChannels = {}
		self.oldPlayers = {}
		self.availableChannels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]#, 11, 12, 13, 14 ,15, 16]
		self.mout = rtmidi.RtMidiOut()
		self.min = rtmidi.RtMidiIn()
		self.min.openVirtualPort(MidiManager.MidiPortName)
		self.mout.openVirtualPort(MidiManager.MidiPortName)
		self.midiPort = -1
		self.startedPlaying = False
		self.initialTime = time.clock()
		for i in range(0, self.mout.getPortCount()):
			if self.mout.getPortName(i) == MidiManager.MidiPortName:
				self.midiPort = i
				return
		
		if self.midiPort == -1:
			raise Exception('Epic failure of finding midi channel I just opened.')
		


	def addPlayer(self, phone):
		if not self.startedPlaying:
			self.startedPlaying = True
			self.midiFile = MIDIFile(10)
			self.midiFile.addTempo(0, 0, 60)

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
			self.oldPlayers[phone] = player
			if len(self.midiChannels) < 1:
				fn = str(uuid.uuid1())
				with f = open(fn, 'wb'):
					self.midiFile.writeFile(f)
				
	
	def playNote(self, phone, digit):
		if self.midiChannels.has_key(phone):
			player = self.midiChannels[phone]
			msg = player.getNoteOnMessage(digit)
			if msg:
				noteLength = 1.5
				elapsedTime = time.clock() - self.initialTime
				self.midiFile.addNote(player.getMidiChannel(), player.getMidiChannel(), msg.getNoteNumber(), elapsedTime, noteLength, 127)
				print "Sending midi message: channel={0} note={1} vel={2}".format(msg.getChannel(), msg.getNoteNumber(), msg.getVelocity())
				self.mout.sendMessage(msg)
				t = threading.Timer(noteLength, self.stopNote, [phone, digit])
				t.start()

			return True


	def stopNote(self, phone, digit):
		if self.midiChannels.has_key(phone):
			player = self.midiChannels[phone]
		elif self.oldPlayers.has_key(phone):
			player = self.oldPlayers[phone]
		else:
			player = None
		
		if player:
			msg = player.getNoteOffMessage(digit)
			if msg:
				print "Sending midi message: channel={0} note={1}".format(msg.getChannel(), msg.getNoteNumber())
				self.mout.sendMessage(msg)
