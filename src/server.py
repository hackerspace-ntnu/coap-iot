import logging
import asyncio
import flask
import threading
import time
import aiocoap.resource as resource
import aiocoap
import copy

from SECRET import SECRET_KEY

from flask_socketio import *

app = flask.Flask(__name__,static_folder="../static",static_url_path="/static",template_folder="../templates")
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)


@asyncio.coroutine
def send_coap_message(host,path,payload):
    print(host,path,payload)
    bluesea = yield from aiocoap.Context.create_client_context()
    request = aiocoap.Message(code=aiocoap.PUT, payload=payload.encode("ascii"))
    request.set_request_uri("coap://"+host+"/"+path)
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

    def updateled(self, red):
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            for i in range(4):
                if int(red[i]) == 1:
                    self.led[i] = (self.led[i]+1)%2
            print("Thread ID:",threading.current_thread())
            socketio.emit('newboard',{'data':self.led,'id':self.name},broadcast=True)
            strdata = ""
            for element in self.led:
                strdata += str(element)
            print("Code",strdata)
            if self.address == None:
                return
            send_coap_message(self.address,'led',strdata)
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
            self.address = address
        finally:
            self.lock.release()

    def updatelastactive(self, lastactive):
        self.lock.acquire()
        try:
            self.lastactive = lastactive
        finally:
            self.lock.release()

DEVICES = {}
for i in range(1,21):
    DEVICES[str(i).zfill(2)] = (Nordicnode(name=str(i).zfill(2)))


@app.route("/")
def index():
    return flask.render_template("index.html", name="index")


@app.route("/<int:id>")
def parseCommand(id):
    # Start tentative nonlocked ip id map
    if flask.g.get("ipidmap",None) == None:
        flask.g.ipidmap = {flask.request.environ["REMOTE_ADDR"], id}
    else:
        flask.g.ipidmap[flask.request.environ["REMOTE_ADDR"]] = id
    
    print("yolo ",flask.g.get("ipidmap",None))
    # End tentative map
    return flask.render_template("led.html", name="led")


@socketio.on('connect')
def on_connect():
    emit('connection', {'data': 'Connected'})


@socketio.on('disconnect')
def on_disco():
    print("The birds flew south")


@socketio.on('toggleled')
def on_toggle(data):
    print('HELLO')
    payload = data['leds']
    id = data['id']
    print(id)
    DEVICES[str(id).zfill(2)].updateled(payload)


@socketio.on('requeststate')
def on_request_state(data):
    id = data['id']
    print('WHAT YEAR IS IT',id)
    print('Request received',id,DEVICES[str(id).zfill(2)].getledstatus())
    emit('newboard',{'data':DEVICES[str(id).zfill(2)].getledstatus(),'id':id})


class LedResource(resource.Resource):
    def __init__(self,kit):
        super(LedResource, self).__init__()
        self.kit = kit

    def render_put(self,req):
        print("Got payload: %s" % req.payload)
        DEVICES[self.kit].updateled(req.payload.decode('ascii'))
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)


class LastSeenResource(resource.Resource):
    def __init__(self,kit):
        super(LastSeenResource, self).__init__()
        self.kit = kit

    def render_put(self,req):
        print("Keepalive: %s" % req.payload)
        DEVICES[self.kit].updatelastactive(time.time())
        DEVICES[self.kit].updateaddress(req.remote[0])
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)


def main():

    root = resource.Site()
    for kit in range(1,21):
        root.add_resource((str(kit).zfill(2), 'button'), LedResource(str(kit).zfill(2)))
        root.add_resource((str(kit).zfill(2), 'i_am_alive'), LastSeenResource(str(kit).zfill(2)))

    websrv = threading.Thread(target=(lambda: socketio.run(app=app, debug=True, port=5000, use_reloader=False)), name="Flask-server")
    websrv.start()
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

if __name__ == "__main__":
    main()
