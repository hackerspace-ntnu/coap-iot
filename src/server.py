import logging
import asyncio
import flask
import threading
import time
import aiocoap.resource as resource
import aiocoap

app = flask.Flask(__name__,static_folder="../static",static_url_path="/static",template_folder="../templates")
@app.route("/")


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
        finally:
            logging.debug('Released a lock')
            self.lock.release()

    def updatestatus(self, active):
        self.lock.acquire()
        try:
            self.active = active
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
for i in enumerate(range(1,20)):
    DEVICES[str(i).zfill(2)] = (Nordicnode(name=str(i).zfill(2)))

def hello():
    return flask.render_template("index.html", name="index")

class LedResource(resource.Resource):
    def __init__(self,kit):
        super(BlockResource, self).__init__()
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
        super(BlockResource, self).__init__()
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
        root.add_resource((str(kit).zfill(2),'i_am_alive'), BlockResource(str(kit).zfill(2)))

    websrv = threading.Thread(target=(lambda: app.run(debug=True, port=25565, use_reloader=False)), name="Flask-server")
    websrv.start()
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)



if __name__ == "__main__":
    main()
