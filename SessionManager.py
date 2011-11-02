#!/usr/bin/env python

import tornado.database
import json

# JSON resopnse format for clientrequest:
# {
#   "participant_id": participant_id,
#   "digit":digit
# }
# participant_id is the id that client will associate with midi channel
# digit is 0-9, *, or H for hung up, or N for new participant
# Now that's what I call versatility.

class SessionManager(object):
    def __init__(self, db_host, db_name, db_user, db_pass):
        self.db = tornado.database.Connection(
            db_host,
            db_name,
            user=db_user,
            password=db_pass)
        
        self.sessions = {} # key = shortcode
        self.participants = {} # key = phone_num
        self.activeShortcodes = []
        self.activeRequests = []
        self.clientResponseBuffer = {}
	
        
    def addNewSession(self, sessnion_name):
        '''Creates new session and adds it to the database and collection'''
        session_id = self.db.execute_lastrowid(
            'insert into sessions set name={0}'.format(session_name))
        session = Session(id, self.getNewShortcode())
        self.sessions[session.shortcode] = session
        return session.shortcode
        
	
    def endSession(self, shortcode):
        '''Ends a session, uploads midi file, writes final info to database.'''
        pass


    def addCallerToSession(self, shortcode, phone_num):
        if shortcode in self.sessions and not phone_num in self.participants:
            # send message to client
            session = self.sessions[shortcode]
            if session.isFull():
                return False
            session.addPlayer()
            participant_id = self.db.execute_lastrowid(
                'insert into participants set FK_session_id={0}'.format(session.id))
            participant = Participant(participant_id, phone_num, session)
            self.participants[phone_num] = participant
            
            return True
        elif phone_num in self.participants:
            # print('Participant {0} already active in {1}'.format(
            #         phone_num, session.name))
            return True
        elif shortcode not in self.sessions:
            raise Exception('Invalid shortcode')


    def newClientRequest(self, shortcode, request_handler):
        self.activeRequests[shortcode] = ClientRequest(shortcode, request_handler)
        # todo: add logic for response

    def handleDigitDialed(self, phone_num, digit):
        participant = self.participants[phone_num]
        response = {
            'participant_id':participant.id,
            'digit':digit
            }
        
        
        
        if shortcode in self.activeRequests:
            request = self.activeRequests[shortcode]
            request.handler.respondToClient(request)
            self.activeRequests.pop(shortcode)
            # todo: add logic for response queue
        else:
            pass
        

    def handleHangup(self, phone_num):
        participant = self.participants[phone_num]
        response = {
            'participant_id':participant.id,
            'digit':'H'
            }
        
        if shortcode in self.activeRequests:
            request = self.activeRequests[shortcode]
            request.handler.respondToClient(request)
            self.activeRequests.pop(shortcode)
            # todo: add logic for response queue
        else:
            pass


    def addClientResponse(self, shortcode, response):
        if shortcode not in self.clientResponseBuffer:
            self.clientResponseBuffer[shortcode] = {'messages':[]}

        self.clientResopnseBuffer[shortcode]['messages'].append(response)


    def flushClientResponseBuffer(self, shortcode):
        if shortcode in activeRequests and shortcode in self.clientResponseBffer:
            request = self.activeRequests[shortcode]
            request.respondToClient(self.clientResponseBuffer[shortcode])
            self.clientResponseBuffer[shortcode]['messages'].clear()
            
            

    
    def getNewShortcode(self):
        '''Generates a new 3-digit shortcode.'''
        shortcode = 1
        if not self.activeShortCodes:
            self.activeShortcodes.append(shortcode)
        else:
            shortcode = max(self.activeShortCodes) + 1
            if shortcode > 999:
                raise Exception('Ran out of shortcodes')
            self.activeShortcodes.append(shortcode)
        return format(shortcode, '03d')



class Session(object):
    def __init__(self, session_id, shortcode):
        self.id = session_id
        self.name = ''
        self.midifile_url = ''
        self.shortcode = shortcode
        self.player_count = 0


    def addPlayer(self):
        self.player_count += 1

    def isFull(self):
        return self.player_count >= 16



class Participant(object):
    def __init__(self, participant_id, phone_num, session):
        self.id = participant_id
        self.phone_num = phone_num
        self.midi_channel = 0
        self.session = session


class ClientRequest(object):
    def __init__(self, shortcode, request_handler):
        self.shortcode = shortcode
        self.handler = request_handler
