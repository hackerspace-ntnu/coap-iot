import aiocoap.resource as resource
import aiocoap
import time
import asyncio

addresses = {}
aliveness = {}


class LedResource(resource.Resource):
    def __init__(self,kit):
        super(LedResource, self).__init__()
        self.kit = kit

    def render_put(self,req):
        print("Got payload: %s" % req.payload)
        #DEVICES[self.kit].updateled(req.payload.decode('ascii'))
        """
        Echo back messages
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)


class LastSeenResource(resource.Resource):
    def __init__(self,kit):
        super(LastSeenResource, self).__init__()
        self.kit = kit

    def render_put(self,req):
        print("Keepalive: %s" % req.payload)
        aliveness[self.kit] = time.time()
        addresses[self.kit] = req.remote[0]
        """
        http put to flask server <int>/<str>/ledpushed
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload=req.payload)


def main():
    root = resource.Site()
    for kit in range(1,21):
        root.add_resource((str(kit).zfill(2), 'button'), LedResource(str(kit).zfill(2)))
        root.add_resource((str(kit).zfill(2), 'i_am_alive'), LastSeenResource(str(kit).zfill(2)))

    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()