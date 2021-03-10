from flask import Flask
from flask_cors import CORS, cross_origin
import pexpect
from pexpect.popen_spawn import PopenSpawn
import datetime
import re
from time import sleep
import threading

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

FILEPATH = '/home/ubuntu/claratraindevday-latest/FL_COVID/covid_classification/read/startup/fl_admin.sh'
USERNAME = 'read@gmail.com'

child = pexpect.spawn(FILEPATH)
child.expect('User Name:')
child.sendline(USERNAME)
child.expect('\r\n>')

def run(cmd):
    child.sendline(cmd)
    child.expect('\r\n>')
    return child.before.decode("utf-8") 

def uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_sec = float(f.readline().split()[0]) // 1
        dt = datetime.timedelta(seconds=uptime_sec)
        return str(dt)

def get_clients_status():
    clients = run('check_status client').split('\r\n')
    clients = filter(lambda x: 'instance' in x, clients)
    clients_dict = {}
    for line in clients:
        client_data = re.split(':|\t', line)
        key = client_data[1].strip()
        if 'No replies' in client_data[-1]:
            clients_dict[key] = {'status': 'disconnected'}
        else:
            clients_dict[key] = {}
            for i in range(len(client_data)//2):
                clients_dict[key][client_data[2*i].strip()] = client_data[2*i+1].strip()
    servers = run('check_status server').split('\r\n')
    CAPTURE = re.compile(r'\|[A-Za-z0-9 \-_]*\|[A-Za-z0-9 \-]*\|[A-Za-z0-9 \-]*\|')
    servers = [line for line in servers if CAPTURE.match(line)]
    for line in servers[1:]:
        key = line.split('|')[1].strip()
        for key2, value in zip(['client name', 'token', 'submitted model'], line.split('|')[1:4]):
            clients_dict[key][key2.strip()] = value.strip()
            
    return list(clients_dict.values())

def get_server_status():
    servers = run('check_status server').split('\r\n')
    server_status = {}
    if servers[1].find(':') != -1:
        server_status['run number'] = servers[1].split(':')[1].strip()
    server_status['status'] = servers[2].split(':')[1].strip()
    for line in servers[3:-1]:
        if ':' in line:
            for pair in line.split('\t'):
                key, value = pair.split(':')
                server_status[key.strip()] = value.strip()
    return server_status

ret = {}

def poll():
    global ret
    while(True):
        sleep(4)
        ret = {
            'uptime': uptime(),
            'clients': get_clients_status(),
            'server': get_server_status(),
            }

@app.route('/')
@cross_origin()
def get():
    global ret
    return ret

if __name__ == '__main__':
    threading.Thread(target=poll).start()
    app.run(host='0.0.0.0', port=8080)
