import logging
import asyncio
import flask
import threading

import aiocoap.resource as resource
import aiocoap

app = flask.Flask(__name__,static_folder="../static",static_url_path="/static",template_folder="../templates")
@app.route("/")
def index():
    return flask.render_template("index.html", name="index")

@app.route("/<int:id>/<command>")
def parseCommand(id, command):
    pass

class BlockResource(resource.Resource):
    """
    We will test some of aiocoap here.
    Enjoy.
    """
    
    def __init__(self):
        super(BlockResource, self).__init__()
        self.content = ("test-content: yes please").encode("ascii")
        
    
    @asyncio.coroutine
    def render_get(self, req):
        resp = aiocoap.Message(code=aiocoap.CONTENT,payload=self.content)
        return resp
        
    def render_put(self,req):
        print("Got payload: %s" % req.payload)
        self.content = req.payload
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)

def main():
    root = resource.Site()
    root.add_resource(('block',),BlockResource())
    
    websrv = threading.Thread(target=(lambda: app.run(debug=True, port=25565, use_reloader=False)), name="Flask-server")
    websrv.start()
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

if __name__ == "__main__":
    main()
