import random
import rtmidi
import threading
from midiutil.MidiFile import MIDIFile
import time
import uuid
import ftplib
from bitly_api import Connection
from twilio.rest import TwilioRestClient

random.seed()


class MidiPhonConfig(object):
    """Configuration object class for midiphon"""

    TwilioTokenString = "TWILIO_API_TOKEN"
    TwilioSidString   = "TWILIO_APP_SID"
    BitlyTokenString  = "BITLY_API_TOKEN"

    def __init__(self):
        super(MidiPhonConfig, self).__init__()
        self.TwilioApiToken  = ''
        self.TwilioAppSid    = ''
        self.BitlyApiToken   = ''
        self.NumMidiChannels = 16
        


class PhoneMusician(object):

    NoteMap = {
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

    def __init__(self, phoneNumber, midiChannel):
        super(PhoneMusician, self).__init__()
        self.midiChannel = midiChannel
        self.phoneNumber = phoneNumber
        self.octaveModifier = 0
        self.semitoneModifier = 0
    
    def getMidiChannel(self):
        return self.midiChannel
    
    def getNoteOnMessage(self, digit):
        if digit == '*':
            self.octaveDown(1)
            return None
        elif digit == '#':
            self.octaveUp(1)
            return None
        return rtmidi.MidiMessage.noteOn(self.midiChannel, PhoneMusician.NoteMap[digit] + self.octaveModifier * 12 + self.semitoneModifier, 127)
    
    def getPhoneNumber():
        return self.phoneNumber

    def getNoteOffMessage(self, digit):
        if digit == '*' or digit == '#':
            return None
        return rtmidi.MidiMessage.noteOff(self.midiChannel, PhoneMusician.NoteMap[digit] + self.octaveModifier * 12 + self.semitoneModifier)

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

    def __init__(self, midiPhonConfig):
        super(MidiManager, self).__init__()

        self.midiPhonConfig = midiPhonConfig
        self.midiChannels = {}
        self.oldPlayers = {}
        self.availableChannels = range(1, self.midiPhonConfig.NumMidiChannels + 1)
        self.mout = rtmidi.RtMidiOut()
        # self.min = rtmidi.RtMidiIn()
        # self.min.openVirtualPort(MidiManager.MidiPortName)
        self.mout.openVirtualPort(MidiManager.MidiPortName)
        self.startedPlaying = False
        self.initialTime = time.clock()
        # for i in range(0, self.mout.getPortCount()):
        #     if self.mout.getPortName(i) == MidiManager.MidiPortName:
        #         self.midiPort = i
        #         break
        
        # if self.midiPort == -1:
        #     raise Exception('Epic failure of finding midi channel I just opened.')

        self.twilio_client = TwilioRestClient(
            account=self.midiPhonConfig.TwilioAppSid,
            token=self.midiPhonConfig.TwilioApiToken
        )

    def releaseMidi(self):
        self.mout.closePort()


    def uploadMidiFile(self, filename):
        print "Uploading midi file"
        ftp = ftplib.FTP('midiphon.bartnett.com', 'midiphon_uploader', 'grantophone')
        mf = open(filename)
        ftp.storbinary('STOR midiphon.bartnett.com/' + filename, mf)
        mf.close()
        print "Done storing midi file"
        
        if self.midiPhonConfig.BitlyApiToken:
            link = self.getBitlyLink('http://midiphon.bartnett.com/' + str(filename))
            print 'GOT LINK: ' + link
            self.sendBitlyLink(link)
            print "SMS Sent!"
        else:
            print 'Not Bit.ly api token specified, not sending out the link to midi file.'

    def getBitlyLink(self, url):
        print "Opening bitly connection"
        connect = Connection("midiphon", self.midiPhonConfig.BitlyApiToken)
        print "Shortening URL"
        short = connect.shorten(url)
        print "Done shortening URL"
        return short['url']

    def sendBitlyLink(self, link):
        for p in self.oldPlayers:
            self.twilio_client.sms.messages.create(to=p, from_="13866434928", body=("Listen to your performance at " + link))

        self.oldPlayers.clear()
        self.startedPlaying = False

    
    def setNumMidiChannels(numChannels):
        if not self.startedPlaying:
            if numChannels <= 16:
                self.availableChannels = range(1, numChannels + 1)
            else:
                print 'Error: limit is 16 channels'
                return False
        else:
            print "Error, can't change number of midi channels in the middle of a session."


    def addPlayer(self, phone):
        if not self.startedPlaying:
            self.startedPlaying = True
            self.midiFile = MIDIFile(self.midiPhonConfig.NumMidiChannels)
            for i in range(0, self.midiPhonConfig.NumMidiChannels):
                self.midiFile.addTrackName(i, 0, str(i))
                self.midiFile.addTempo(i, 0, 60)

        if self.midiChannels.has_key(phone):
            return True
        
        
        channelCount = len(self.availableChannels)
        if channelCount > 0:
            self.midiChannels[phone] = PhoneMusician(phone, self.availableChannels.pop(random.randint(1, channelCount) - 1))
            print "Adding player#" + phone
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
                fn = str(uuid.uuid1()) + '.mid'
                f = open(fn, 'wb')
                self.midiFile.writeFile(f)
                f.close()
                self.midiFile.close()
                self.uploadMidiFile(fn)
                
    
    def playNote(self, phone, digit):
        if self.midiChannels.has_key(phone):
            player = self.midiChannels[phone]
            msg = player.getNoteOnMessage(digit)
            if msg:
                noteLength = 1.5
                elapsedTime = (time.clock() - self.initialTime) * 60.0
                try:
                    self.midiFile.addNote(player.getMidiChannel() - 1, player.getMidiChannel() - 1, msg.getNoteNumber(), elapsedTime, noteLength, 127)
                    print "Sending midi message: channel={0} note={1} vel={2}".format(msg.getChannel(), msg.getNoteNumber(), msg.getVelocity())
                    self.mout.sendMessage(msg)
                    t = threading.Timer(noteLength, self.stopNote, [phone, digit])
                    t.start()
                except IndexError:
                    print 'Error adding midi note'
                    print 'PlayerInfo: MidiChannel: {0} MidiNote: {1}'.format(player.getMidiChannel(), msg.getNoteNumber())
                    return False

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
