#!/usr/bin/env python

import tornado.web
import tornado.ioloop
import json
from SessionManager import SessionManager
from twilio import twiml

class TwilioHandler(tornado.web.RequestHandler):
    def initialize(self, sessionManager):
        self.sessionManager = sessionManager
    
    @tornado.web.removeslash
    def post(self, *args, **kwargs):
        print('Got Twilio request')
        if self.request.path == '/twilio/enter':
            print('Performing /twilio/enter')
            phone_num = self.get_argument('From')
            r = twiml.Response()
            r.say("Welcome to midi-phone. Enter your jam session's shortcode.")
            r.gather(action='/twilio/recurse', numDigits=3)
            self.write(r.toxml())
            
        elif self.request.path == '/twilio/recurse':
            print('Performing /twilio/recurse')
            digits = self.get_argument('Digits')
            phone_num = self.get_argument('From')
            r = twiml.Response()
            print('Checking the dialed digits')
            if len(digits) == 3:
                print('3 digits dialed')
                if self.sessionManager.addCallerToSession(digits, phone_num):
                    r.say('Press a key to play a note')
                    r.gather(action='/twilio/recurse', numDigits=1)
                else:
                    r.say("This jam is full yo. Seventeen's a crowd")
                    r.hangup()
            elif len(digits) == 1:
                print('1 digit dialed')
                r.say('Okay')
            
            else:
                r.say("These aren't the droids you're looking for.")
                r.hangup()

            self.write(r.toxml())
        elif self.request.path == '/twilio/status':
            pass



class WebHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('Hello, world.')
    

class ClientHandler(tornado.web.RequestHandler):
    def initialize(self, sessionManager):
        self.sessionManager = sessionManager
    
    @tornado.web.asynchronous
    @tornado.web.removeslash
    def get(self, *args, **kwargs):
        if self.request.path == '/client/newsession':
            print('Client connected.')
            session_name = self.get_argument('session_name', default='MyJam')
            shortcode = self.sessionManager.addNewSession(session_name)
            self.write(json.dumps({
                        "success":True,
                        "shortcode":shortcode
                        }))
            self.finish()
            print('Added client with shortcode {0}'.format(shortcode))
        elif self.request.path == '/client/update':
            pass
        elif self.request.path == '/client/endsession':
            pass

    def respondToClient(self, response):
        self.write(json.dumps(response))
        self.finish()


if __name__ == "__main__":
    db_host = 'localhost'
    db_name = 'midiphon_webapp_db'
    db_user = 'midiphon_webapp'
    db_pass = 'grantophone'
    
    database = tornado.database.Connection(
            db_host,
            db_name,
            user=db_user,
            password=db_pass)

    sessionManager = SessionManager(database)
    
    application = tornado.web.Application([
        (r"/client/newsession/*", ClientHandler, dict(sessionManager=sessionManager)),
        (r"/client/update/*", ClientHandler, dict(sessionManager=sessionManager)),
        (r"/client/endsession/*", ClientHandler, dict(sessionManager=sessionManager)),
        (r"/twilio/enter/*", TwilioHandler, dict(sessionManager=sessionManager)),
        (r"/twilio/recurse/*", TwilioHandler, dict(sessionManager=sessionManager)),
        (r"/twilio/status/*", TwilioHandler, dict(sessionManager=sessionManager)),
    ])
    application.listen(80)
    print('Listening on port 80')
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print('User quit')
