#!/usr/bin/env python

import tornado.web
import tornado.ioloop
from midiphon_midi import MidiManager

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
		self.write(twilio_handler.setup(self.request))


class RecurseHandler(tornado.web.RequestHandler):
	def post(self, *args, **kwargs):
		self.request
		self.write("We are recursing")
	
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
