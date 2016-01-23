import logging
import asyncio
import time

import aiocoap.resource as resource
import aiocoap

STAYALIVE = "i_am_alive"
BUTTNPRSS = "button"

# Will contain device mapping from 01..20 range to IP
devices = {}
last_seen = {}

class BlockResource(resource.Resource):
    """
    We will test some of aiocoap here.
    Enjoy.
    """
    
    def __init__(self):
        super(BlockResource, self).__init__()
    
    @asyncio.coroutine
    def render_get(self, req):
        led_status = "\"0000\""
        ip = "localhost"
        opcode = "led = %s" % led_status
        content = ("%s/%s" % (ip,opcode)).encode("ascii")
        resp = aiocoap.Message(code=aiocoap.CONTENT,payload=content)
        return resp
        
    def render_put(self,req):
        values = (req.payload.decode("utf-8")).split("/")
        # Evaluate message validity
        if(len(values)!=3):
            print("Received ill-formed message: %s" % req.payload)
            return aiocoap.Message(code=aiocoap.BAD_REQUEST,payload="")
        # Extract data
        ip = values[0]
        identifier = values[1].replace('"','')
        information = values[2].split('=')
        for i in range(len(information)):
            information[i] = information[i].strip()
        # Process opcode
        if information[0] == STAYALIVE:
            last_seen[identifier] = time.time()
            print("Bleep bloop, device %s says it's still alive" % (identifier))
        elif information[1] == BUTTNPRSS:
            print("Bleep bloop, button %s was pressed" % (information[1]))
        # Print message for debug purposes
        print("IP: %s, ID: %s, Info: %s" % (ip,identifier,information))
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload="")

def main():
    root = resource.Site()
    root.add_resource(('block',),BlockResource())
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)

main()
