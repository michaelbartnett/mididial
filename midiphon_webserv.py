#!/usr/bin/env python

import tornado.web
import tornado.ioloop
from midiphon_midi import MidiManager
from twilio import twiml

myglob = 42

midiManager = MidiManager()

def printget(handler):
	print "Got a get in RecurseHandler!"
	handler.write("""
	Got request!<br /><br />
	Path = '{0}'<br /><br />
	Query = '{1}'<br /><br />
	Headers = '{2}'<br /><br />
	Arguments = '{3}'<br /><br />
	Body = '{4}'<br /><br />
	""".format(handler.request.path, handler.request.query, handler.request.headers, handler.request.arguments, handler.request.body))

	print "Done with RecurseHandler."


class MainHandler(tornado.web.RequestHandler):

	def get(self):
		print "Got a get in MainHandler!"
		self.write("""
		Got request!<br /><br />
		Path = '{0}'<br /><br />
		Query = '{1}'<br /><br />
		Headers = '{2}'<br /><br />
		Arguments = '{3}'<br /><br />
		Body = '{4}'<br /><br />
		""".format(self.request.path, self.request.query, self.request.headers, self.request.arguments, self.request.body))

		print "Done with MainHandler."
	
	def post(self):
		global midiManager
		r = twiml.Response()
		r.say("Welcome to MIDIphon.")
		phoneNumber = self.request.arguments["From"][0]
		if midiManager.addPlayer(phoneNumber) == False:
			r.say("All channels full.")
			r.hangup()
		else:
			r.say('Press a key to play a note')
			r.gather(action='/recurse', numDigits=1)

		self.write(r.toxml())



class RecurseHandler(tornado.web.RequestHandler):
	def post(self):
		global midiManager
		r = twiml.Response()
		phoneNumber = self.request.arguments['From'][0]
		digit = self.request.arguments['Digits'][0]
		if midiManager.playNote(phoneNumber, digit) == False:
			r.say("You are not a valid person.")
			r.hangup()
		else:
			r.say('Okay')
			r.gather(action='/recurse', numDigits=1)

		self.write(r.toxml())

	
	def get(self):
		print "Got a get in RecurseHandler!"
		self.write("""
		Got request!<br /><br />
		Path = '{0}'<br /><br />
		Query = '{1}'<br /><br />
		Headers = '{2}'<br /><br />
		Arguments = '{3}'<br /><br />
		Body = '{4}'<br /><br />
		""".format(self.request.path, self.request.query, self.request.headers, self.request.arguments, self.request.body))

		print "Done with RecurseHandler."


class StatusHandler(tornado.web.RequestHandler):
	def post(self):
		global midiManager
		callstatus = self.request.arguments['CallStatus'][0]
		print "Got call status callback!"
		if callstatus == 'completed':
			print "Got end call callback!"
			phoneNumber = self.request.arguments['From'][0]
			midiManager.removePlayer(phoneNumber)
		else:
			print 'Got call status: ' + callstatus
	
	def get(self):
		printget(self)





application = tornado.web.Application([
    (r"/entry", MainHandler),
    (r"/recurse", RecurseHandler),
    (r"/status", StatusHandler),
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
