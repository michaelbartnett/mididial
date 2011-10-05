#!/usr/bin/env python

import tornado.web
import tornado.ioloop
from midiphon_midi import MidiManager
from twilio import twiml

midiManager = MidiManager(16)

def printget(handler):
    '''Just prints out request info, easier to check if localtunnel's working.'''
    print "Got a get in a " + handler.__class__.__name__
    handler.write("""
    Got request!<br /><br />
    Path = '{0}'<br /><br />
    Query = '{1}'<br /><br />
    Headers = '{2}'<br /><br />
    Arguments = '{3}'<br /><br />
    Body = '{4}'<br /><br />
    """.format(handler.request.path, handler.request.query, handler.request.headers, handler.request.arguments, handler.request.body))

    print "Done with RecurseHandler" + handler.__class__.__name__


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        printget(self)
    
    def post(self):
        global midiManager
        r = twiml.Response()
        r.say("Welcome to mideefawn.")
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
        printget(self)


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

if __name__ == "__main__":
    import sys
    import optparse

    parser = optparse.OptionParser(
        description='The server software for running your own MidiPHON instance.',
        epilog='''
        Check out the README for basic instructions, or visit
        midiphon.bartnett.com for detailed setup instructions.
        '''
    )

    parser.add_option('-n', '--num-midi-channels', type='int', dest='numChannels')
    parser.add_option('-p', '--port', type='int', default=8080)

    (options, args) = parser.parse_args()

    if len(args) > 0:
        sys.stdout.write('Error, unrecognized arguments: ')
        for a in args:
            sys.stdout.write(a + ' ')
        print ''
        sys.exit(1)

    if (options.numChannels):
        midiManager.setNumChannels(options)
    

    application = tornado.web.Application([
        (r"/entry", MainHandler),
        (r"/recurse", RecurseHandler),
        (r"/status", StatusHandler),
    ])

    application.listen(options.port)
    print 'Listening on port {0}'.format(options.port)
    tornado.ioloop.IOLoop.instance().start()
