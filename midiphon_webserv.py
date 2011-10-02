#!/usr/bin/env python

import tornado.web
import tornado.ioloop


class MainHandler(tornado.web.RequestHandler):
	def get(self, *args, **kwargs):
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

class RecurseHandler(tornado.web.RequestHandler):
	def post(self, *args, **kwargs):
		self.write("We are recursing")
	
	def get(self):
		self.write("We don't care about your <em>stinking</em> GETs.")


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/recurse", RecurseHandler),
    (r"/)
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
