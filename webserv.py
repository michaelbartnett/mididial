#!/usr/bin/env python

import tornado.web
import tornado.ioloop

class TwilioHandler(tornado.web.RequestHandler):
    @tornado.web.removeslash
    def post(self, *args, **kwargs):
        if self.request.path == '/twilio/entry':
            r = twiml.Response()
            r.say("Welcome to midi-phone.")
            phoneNumber = self.request.arguments["From"][0]
            if midiManager.addPlayer(phoneNumber) == False:
                r.say("All channels full.")
                r.hangup()
            else:
                r.say('Press a key to play a note')
                r.gather(action='/twilio/recurse', numDigits=1)

            self.write(r.toxml())
            
        elif self.request.path == '/twilio/recurse':
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


class WebHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        pass
    

class ClientHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.web.removeslash
    def get(self, *args, **kwargs):
        if self.request.path == '/client/newsession':
            pass
        elif self.request.path == '/client/update':
            pass
        elif self.request.path == '/client/endsession':
            pass

    def respondToClient(self, response):
        self.write(json.dumps(response))
        self.finish()


if __name__ == "__main__":
    application = tornado.web.Application([
            (r"/client/newsession/*", ClientHandler),
            (r"/client/update/*", ClientHandler),
            (r"/client/endsession/*", ClientHandler),
            (r"/twilio/enter/*", TwilioHandler),
            (r"/twilio/recurse/*", TwilioHandler),
            (r"/twilio/status/*", TwilioHandler),
    ])
