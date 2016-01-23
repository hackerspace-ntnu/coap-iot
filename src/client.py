import asyncio
import sys

null = None

from aiocoap import *

STAYALIVE = "i_am_alive"
BUTTNPRSS = "button"

server_ip = "localhost"
server_path = "block"

dev_id = "01"
dev_ip = "localhost"

def gen_message(ip,devid,opcode,data):
    fmt = ("%s/\"%s\"/%s = \"%s\"" % (ip,devid,opcode,data)).encode("ascii")
    return Message(code=PUT,payload=fmt)

@asyncio.coroutine
def main():
    protocol = yield from  Context.create_client_context();
    request = gen_message(dev_ip,dev_id,STAYALIVE,0)
    request.set_request_uri("coap://%s/%s" % (server_ip,server_path));
    try:
        response = yield from protocol.request(request).response;
    except Exception as e:
        print(e)
    else:
        print("Code=%s, message=%s" % (response.code,response.payload))

if(len(sys.argv)>=2):
    dev_id = sys.argv[1]

if(dev_id == null):
    exit(1)

asyncio.get_event_loop().run_until_complete(main())
