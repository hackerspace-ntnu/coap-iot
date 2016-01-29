import threading
import copy
import logging
import asyncio
from flask_socketio import *
import aiocoap


@asyncio.coroutine
def send_coap_message(host,path,payload):
    print(host,path,payload)
    bluesea = yield from aiocoap.Context.create_client_context()
    request = aiocoap.Message(code=aiocoap.PUT, payload=payload.encode("ascii"))
    request.set_request_uri("coap://"+'localhost'+"/"+path)
    try:
        response = yield from bluesea.request(request).response
    except Exception as e:
        print(e)
    else:
        print("Message response:",response.code,response.payload)


class Nordicnode():
    def __init__(self, led=None, active=False, address=None, lastactive=0, name=None):
        self.lock = threading.Lock()
        self.led = [0,0,0,0]
        self.active = active
        self.address = address
        self.lastactive = lastactive
        self.name = name

    def updateled(self, socketio, red):
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            for i in range(4):
                if int(red[i]) == 1:
                    self.led[i] = (self.led[i]+1)%2
            print("Thread ID:",threading.current_thread())
            print('Emitting socket broadcast')
            socketio.emit('newboard',{'data':self.led,'id':self.name},broadcast=True)
            print('Broadcast complete')
            """
            Send CoAP meldinger til kit herifra
            """
        finally:
            logging.debug('Released a lock')
            self.lock.release()

    def updatestatus(self, active):
        self.lock.acquire()
        try:
            self.active = active
        finally:
            self.lock.release()

    def getledstatus(self):
        self.lock.acquire()
        try:
            return copy.deepcopy(self.led)
        finally:
            self.lock.release()

    def updateaddress(self, address):
        self.lock.acquire()
        try:
            print('Refreshing address: %s' % address)
            self.address = address
        finally:
            self.lock.release()

    def updatelastactive(self, lastactive):
        self.lock.acquire()
        try:
            self.lastactive = lastactive
        finally:
            self.lock.release()