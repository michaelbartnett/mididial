#!/usr/bin/env python

import tornado.web
import tornado.ioloop
from midiphon_midi import MidiManager, MidiPhonConfig
from twilio import twiml
import os

midiManager = None

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

def setup(filename):
    params = readConfig(filename)

    if not params:
        lines = []
        params = {
            'twilio_sid'   : raw_input("enter twilio app SID: "),
            'twilio_token' : raw_input("enter twilio authentication token: "), 
            'bitly_token'  : raw_input("enter bitly authentication token (OPTIONAL - press enter to skip): "),
            'num_channels' : raw_input("enter the number of midi channels to use (OPTIONAL - press enter to skip): "),
        }
        if not params['num_channels']: params['num_channels'] = '16'

        # stores each pair on a new line as key:value
        config_file = open(filename, 'wb')
        print("saving configuration...")
        for i in params: lines.append(i + ":" + params[i] + "\n")
        # remove linebreak at end of last line
        lines[-1] = lines[-1].rstrip('\n')
        for i in lines: config_file.write(i)
        # done bitches
        config_file.close()
        print("saved to " + filename)

    config_object = MidiPhonConfig()
    config_object.TwilioAppSid = params['twilio_sid']
    config_object.TwilioApiToken = params['twilio_token']
    config_object.BitlyApiToken = params['bitly_token']
    config_object.NumMidiChannels = int(params['num_channels'])

    return config_object



def readConfig(filename):
    params = {}
    try:
        config_file = open(filename, 'rb')
    except IOError:
        return None

    for line in config_file:
        pair = line.rstrip('\n').split(':')
        params[pair[0]] = pair[1]
    
    return params




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



class RootHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('<h1>Hello!</h1>')
        self.write('<p>You have made a request to {0}</p>'.format(self.request.path))
        self.write('<p>Here are the *args:</p>')
        self.write('<ul>')
        for a in args:
            self.write('<li>{0}</li>'.format(a))
        self.write('</ul>')
        self.write('<p>Here are the **kwargs:</p>')
        self.write('<ul>')
        for k in kwargs:
            self.write('<li>{0}</li>'.format(k))
        self.write('</ul>')



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
        print
        sys.exit(1)

    conf = setup('midiphon.conf')
    # conf = MidiPhonConfig()
    # conf.TwilioApiToken = os.environ[MidiPhonConfig.TwilioTokenString]
    # conf.TwilioAppSid   = os.environ[MidiPhonConfig.TwilioSidString]
    # conf.BitlyApiToken  = os.environ[MidiPhonConfig.BitlyTokenString]
    # conf.numChannels    = options.numChannels
    midiManager = MidiManager(conf)

    application = tornado.web.Application([
        (r"/entry", MainHandler),
        (r"/recurse", RecurseHandler),
        (r"/status", StatusHandler),
        (r"/(.*)", RootHandler),
    ])

    application.listen(options.port)
    print 'Listening on port {0}'.format(options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print
        print 'User quit.'
        tornado.ioloop.IOLoop.instance().stop()
    
    midiManager.releaseMidi()
    sys.exit(0)
