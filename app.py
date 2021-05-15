from flask import Flask
from flask_cors import CORS, cross_origin
import pexpect
from pexpect.popen_spawn import PopenSpawn
from time import sleep
import threading
from utils.getter import get_clients_status, get_server_status, uptime
from utils.errors import ERR_CANNOT_CONNECT

FILEPATH = 'read/startup/fl_admin.sh'
USERNAME = 'read@gmail.com'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


RET = {}


def init():
    child = pexpect.spawn(FILEPATH)
    child.expect('User Name:')
    child.sendline(USERNAME)
    child.expect('\r\n> ')
    return child


def poll():
    global RET
    child = None
    while(True):
        try:
            while child == None:
                child = init()
                RET = {
                    'error': ERR_CANNOT_CONNECT
                }
            RET = {
                'uptime': uptime(),
                'clients': get_clients_status(child),
                'server': get_server_status(child),
            }
        except Exception as e:
            RET = {
                'error': str(e)
            }           
        sleep(20)
            

@app.route('/')
@cross_origin()
def get():
    global RET
    return RET


if __name__ == '__main__':
    threading.Thread(target=poll).start()
    app.run(host='0.0.0.0', port=8080)
