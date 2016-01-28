import asyncio

import aiocoap.resource as resource
from aiocoap import *


@asyncio.coroutine
def send_msg(host, path, payload):
    protocol = yield from Context.create_client_context()
    request = Message(code=PUT, payload=payload.encode("ascii"))
    request.set_request_uri("coap://" + host + "/" + path)
    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print(e)
    else:
        print("lol", response.code, response.payload)

asyncio.get_event_loop().run_until_complete(send_msg('localhost', '03/i_am_alive', '0'))
asyncio.get_event_loop().run_until_complete(send_msg('localhost', '03/button', '1000'))
asyncio.get_event_loop().run_until_complete(send_msg('localhost', '03/button', '0001'))

#root = resource.Site()
#root.add_resource(('led',), BlockResource())
#asyncio.async(Context.create_server_context(root))
#asyncio.get_event_loop().run_forever()