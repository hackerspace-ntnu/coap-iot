import aiocoap.resource as resource
import aiocoap
import asyncio
import http.client

COMMAND_ALIVE = 'alive'
COMMAND_BUTTON = 'button'

GLOBAL_HOST = 'localhost'
GLOBAL_PORT = '5000'


def send_http_request(host, pport, kit, cmd, payload):
    print('Building request:', host, pport, kit, cmd, payload)
    conn = http.client.HTTPConnection(host,port=pport)
    conn.request('GET', '/%s/%s/handle_msg/%s' % (kit, cmd, payload))
    #conn.getresponse()
    conn.close()
    print('Request finished')


class LedResource(resource.Resource):
    def __init__(self,kit):
        super(LedResource, self).__init__()
        self.kit = kit

    def render_put(self, req):
        print("Got payload: %s" % req.payload)
        send_http_request(GLOBAL_HOST, GLOBAL_PORT, self.kit, COMMAND_BUTTON, req.payload.decode('ascii'))
        return aiocoap.Message(code=aiocoap.CHANGED,payload='')


class LastSeenResource(resource.Resource):
    def __init__(self,kit):
        super(LastSeenResource, self).__init__()
        self.kit = kit

    def render_put(self,req):
        print("Keepalive: %s" % req.payload)
        send_http_request(GLOBAL_HOST, GLOBAL_PORT, self.kit, COMMAND_ALIVE, 'dldld')
        """
        http put to flask server <int>/<str>/ledpushed
        """
        return aiocoap.Message(code=aiocoap.CHANGED,payload='')

class BlockResource(resource.Resource):
    def __init__(self):
        super(BlockResource,self).__init__()

    def render(self, request):
        print('We got it:',request.payload)
        return aiocoap.Message(code=aiocoap.CHANGED,payload='')

def main():
    root = resource.Site()
    for kit in range(1,21):
        root.add_resource((str(kit).zfill(2), 'button'), LedResource(str(kit).zfill(2)))
        root.add_resource((str(kit).zfill(2), 'i_am_alive'), LastSeenResource(str(kit).zfill(2)))

    root.add_resource(('led',), BlockResource())

    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()