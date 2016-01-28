import asyncio
import aiocoap.resource as resource
from aiocoap import *


class BlockResource(resource.Resource):
    def __init__(self):
        super(BlockResource,self).__init__()
    def render_put(self,req):
        print('received: %s' % req.payload)


root = resource.Site()
root.add_resource(('led',), BlockResource())
asyncio.async(Context.create_server_context(root))
asyncio.get_event_loop().run_forever()