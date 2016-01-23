import logging
import asyncio
import time

import aiocoap.resource as resource
import aiocoap

class NordicMessage:
    address = None
    device_id = None
    opcode = None
    data = None
    def __init__(self,asciidata):
        values = asciidata
        self.address = values[0]
        self.device_id = int(values[1].replace('"',''))
        info = values[2].split('=')
        for i in range(len(info)):
            info[i] = info[i].strip().replace('"','')
        
        self.opcode = info[0]
        self.data = info[1]

class NordicResponse:
    address = None
    opcode = None
    data = None
    def __init__(self,address,opcode,lights):
        self.address = address
        self.opcode = opcode
        self.data = lights

def gen_response(response):
    payload = ("%s/\"%s\"" % (response.address,response.opcode,response.data)).encode("ascii")
    return aiocap.Message(code=aiocap.CONTENT,payload=payload)

def message_handler(msg):
    """
    msg: A NordicMessage 
    """
    # Process opcode
    if msg.opcode == STAYALIVE:
        last_seen[msg.device_id] = time.time()
        devices[msg.device_id] = msg.address
        print("Bleep bloop, device %s says it's still alive" % (msg.device_id))
    elif msg.opcode == BUTTNPRSS:
        print("Bleep bloop, button %s was pressed" % (msg.data))
    # Print message for debug purposes
    print("IP=%s, ID=%s, Info=%s:%s" % (msg.address,msg.device_id,msg.opcode,msg.data))

STAYALIVE = "i_am_alive"
BUTTNPRSS = "button"

# Will contain device mapping from 01..20 range to IP
devices   = {}
last_seen = {}

class BlockResource(resource.Resource):
    """
    We will test some of aiocoap here.
    Enjoy.
    """
    
    def __init__(self,handler):
        super(BlockResource, self).__init__()
        self.mhandler = handler
    
    def render_put(self,req):
        values = (req.payload.decode("utf-8")).split("/")
        """
        Validate the message contents
        """
        if(len(values)!=3):
            print("Received ill-formed message: %s" % req.payload)
            return aiocoap.Message(code=aiocoap.BAD_REQUEST,payload="")
        """
        Parse the message contents
        """
        msg = NordicMessage(values)
        
        """
        Call up the message handler
        """
        self.mhandler(msg)
        
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload="")

def main():
    root = resource.Site()
    root.add_resource(('block',),BlockResource(message_handler))
    
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.INFO)

main()
