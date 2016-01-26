import logging
import asyncio
import flask
import threading
import time
import aiocoap.resource as resource
import aiocoap

from SECRET import SECRET_KEY

from flask_socketio import SocketIO, join_room, leave_room

app = flask.Flask(__name__,static_folder="../static",static_url_path="/static",template_folder="../templates")
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

class Nordicnode():
    def __init__(self, led="0,0,0,0", active=False, address=None, lastactive=0, name=None):
        self.lock = threading.Lock()
        self.led = led
        self.active = active
        self.address = address
        self.lastactive = lastactive
        self.name = name

    def updateled(self, led):
        self.lock.acquire()
        try:
            logging.debug('Acquired a lock')
            self.led = led
            socketio.send('newboard',{'data':led},room=self.name)
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
        out = None
        try:
            out = copy.deepcopy(self.led)
        finally:
            self.lock.release()
            return out

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
for i in enumerate(range(1,20)):
    DEVICES[str(i).zfill(2)] = (Nordicnode(name=str(i).zfill(2)))

@app.route("/")
def index():
    return flask.render_template("index.html", name="index")

@app.route("/<int:id>/<command>")
def parseCommand(id, command):
    # Start tentative nonlocked ip id map
    if flask.g.get("ipidmap",None) == None:
        flask.g.ipidmap = {flask.request.environ["REMOTE_ADDR"], id}
    else:
        flask.g.ipidmap[flask.request.environ["REMOTE_ADDR"]] = id
    
    print(flask.g.get("ipidmap",None))
    # End tentative map
    return "ID: %i, command: %s" % (id, command)

@socketio.on('join')
def on_join(data):
    id = data['id']
    join_room(id)
    send('newboard',{'data':DEVICES[id].getledstatus()},room=id)

@socketio.on('leave')
def on_leave(data):
    id = data['id']
    leave_room(id)

@socketio.on('toggleled')
def on_toggle(data):
    payload = data['leds']
    id = data['id']
    DEVICES[id].updateled(payload)

class LedResource(resource.Resource):
    def __init__(self,kit):
        super(LedResource, self).__init__()
        # self.content = ("test-content: yes please").encode("ascii")
        self.kit = kit
    @asyncio.coroutine
    def render_get(self, req):
        resp = aiocoap.Message(code=aiocoap.CONTENT,payload=self.content)
        return resp

    def render_put(self,req):
        print("Got payload: %s" % req.payload)
        self.content = req.payload
        DEVICES[self.kit].updateled(req.payload.decode('ascii'))
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)

class LastSeenResource(resource.Resource):
    def __init__(self,kit):
        super(LastSeenResource, self).__init__()
        # self.content = ("test-content: yes please").encode("ascii")
        self.kit = kit
    @asyncio.coroutine
    def render_get(self, req):
        resp = aiocoap.Message(code=aiocoap.CONTENT,payload=self.content)
        return resp

    def render_put(self,req):
        print("Got payload: %s" % req.payload)
        self.content = req.payload
        DEVICES[self.kit].updatelastactive(time.time())
        DEVICES[self.kit].updateaddress(req.remote[0])
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)


def main():

    root = resource.Site()
    for kit in enumerate(range(1,21)):
        root.add_resource((str(kit).zfill(2),'button'), LedResource(str(kit).zfill(2)))
        root.add_resource((str(kit).zfill(2),'i_am_alive'), LastSeenResource(str(kit).zfill(2)))

    websrv = threading.Thread(target=(lambda: socketio.run(app=app, debug=True, port=5000, use_reloader=False)), name="Flask-server")
    websrv.start()
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)



if __name__ == "__main__":
    main()
