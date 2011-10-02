#!/usr/bin/env python

import tornado.web
import tornado.ioloop


class MainHandler(tornado.web.RequestHandler):
	def get(self, *args, **kwargs):
		self.write('OMG MIDIPHON')


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(7777)
    tornado.ioloop.IOLoop.instance().start()
