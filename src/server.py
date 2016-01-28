import logging
import asyncio
import threading
import copy

from nordicnode import Nordicnode
from SECRET import SECRET_KEY

from flask_socketio import *

app = flask.Flask(__name__,static_folder="../static",static_url_path="/static",template_folder="../templates")
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app)


DEVICES = {}
for i in range(1,21):
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

@app.route("/<int:id>/<str:cmd>/handle_msg")
def parseSignal(id):
    """
    Håndter meldinger fra CoAP server om ledchange
    :param id:
    :return:
    """
    return

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
    emit('newboard',{'data':DEVICES[str(id).zfill(2)].getledstatus(),'id':id})


def main():
    socketio.run(app=app, debug=True, port=5000, use_reloader=False)

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

if __name__ == "__main__":
    main()
