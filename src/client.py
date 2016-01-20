import asyncio

from aiocoap import *

@asyncio.coroutine
def main():
	protocol = yield from  Context.create_client_context();
	request = Message(code=PUT,payload=("Hello, server").encode("ascii"));
	request.set_request_uri("coap://localhost/block");
	try:
		response = yield from protocol.request(request).response;
	except Exception as e:
		print(e)
	else:
		print("lol",response.code,response.payload)

asyncio.get_event_loop().run_until_complete(main())
