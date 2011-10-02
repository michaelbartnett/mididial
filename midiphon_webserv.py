#!/usr/bin/env python

import tornado.web
import tornado.ioloop
from midiphon_midi import MidiManager
from twilio import *

myglob = 42

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
		r = twiml.Response()
		phoneNumber = self.request.arguments["From"]
		if MidiManager.addPlayer(phoneNumber) == False:
			r.say("All channels full.")
			r.hangup()
			self.write(r.toxml())
		else:
			r.say("Welcome to MIDIphon.")



class RecurseHandler(tornado.web.RequestHandler):
	def post(self):

	
	def get(self):
		global myglob
		myglob += 1
		self.write("We don't care about your <em>stinking</em> GETs.<br /> myglob is now {0}".format(myglob))





application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/recurse", RecurseHandler),
    (r"/path/to/whateveryouwant", TwilioHandler)
])

if __name__ == "__main__":
    application.listen(8081)
    tornado.ioloop.IOLoop.instance().start()
