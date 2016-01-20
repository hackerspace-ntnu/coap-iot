import logging
import asyncio

import aiocoap.resource as resource
import aiocoap

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
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

main()
