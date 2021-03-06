import logging
import time
import copy

from nordicnode import Nordicnode
from SECRET import SECRET_KEY
from SERVCONFIG import SERVER_HOST,SERVER_PORT

from flask_socketio import *

app = flask.Flask(__name__,static_folder="../static",static_url_path="/static",template_folder="../templates")
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)

MAX_DEVICES = 20

GLOBAL_HOST = SERVER_HOST
GLOBAL_PORT = SERVER_PORT

DEVICES = {}
for i in range(1,MAX_DEVICES+1):
    DEVICES[str(i).zfill(2)] = (Nordicnode(name=str(i).zfill(2)))


@app.route("/")
def index():
    return flask.render_template("index.html", name="index")


@app.route("/<int:id>")
def parseCommand(id):
    # Start tentative nonlocked ip id map
    if flask.g.get("ipidmap",None) == None:
        flask.g.ipidmap = {flask.request.environ["REMOTE_ADDR"], id}
    else:
        flask.g.ipidmap[flask.request.environ["REMOTE_ADDR"]] = id
    
    print("yolo ",flask.g.get("ipidmap",None))
    # End tentative map
    return flask.render_template("led.html", name="led")


@app.route("/<int:id>/<string:cmd>/handle_msg/<string:payloadd>", methods=['PUT', 'GET'])
def parseSignal(id, cmd, payloadd):
    """
    Håndter meldinger fra CoAP server om ledchange
    :param id:
    :return:
    """
    if id > MAX_DEVICES or id < 1:
        return 'Nope'

    kit = str(id).zfill(2)
    payload = str(flask.request.data.decode('ascii'))
    
    print('Payload type',type(payload))

    if cmd == 'alive' and flask.request.method == 'PUT':
        print('Updating address and keepalive', payload)
        DEVICES[kit].updatelastactive(time.time())
        DEVICES[kit].updateaddress(payload)
    elif cmd == 'button':
        print('Button toggle from kit:', payload)
        if len(payload) == 4 and DEVICES[kit].lastactive-time.time() < 25:
            DEVICES[kit].updateled(socketio, payload)
        else:
            print('Failed to toggle buttons')
            return 'Nope'
    else:
        return 'Nope'

    print('CoAP signal:', kit, cmd, payload)
    return 'Good job!'


@socketio.on('connect')
def on_connect():
    emit('connection', {'data': 'Connected'})


@socketio.on('disconnect')
def on_disco():
    print("The birds flew south")


@socketio.on('toggleled')
def on_toggle(data):
    print('HELLO')
    payload = data['leds']
    id = data['id']
    print(id)
    DEVICES[str(id).zfill(2)].updateled(socketio, payload)


@socketio.on('requeststate')
def on_request_state(data):
    id = data['id']
    print('WHAT YEAR IS IT',id)
    print('Request received',id,DEVICES[str(id).zfill(2)].getledstatus())
    emit('newboard', {'data':DEVICES[str(id).zfill(2)].getledstatus(),'id':id})


def main():
    socketio.run(app=app, host=GLOBAL_HOST, debug=True, port=GLOBAL_PORT, use_reloader=False)

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

if __name__ == "__main__":
    main()
