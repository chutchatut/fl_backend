from utils.parser import parse_log
import re
from utils.errors import ERR_CANNOT_CONNECT


def run(cmd, child):
    child.sendline(cmd)
    child.expect('\r\n> ')
    ret_msg = child.before.decode("utf-8").strip()
    if ret_msg.find('Error: not authenticated') != -1 or ret_msg.find('Error: Failed to communicate') != -1:
        raise Exception(ERR_CANNOT_CONNECT)
    return ret_msg


def get_clients_status(child):
    clients = run('check_status client', child).split('\r\n')
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
    servers = run('check_status server', child).split('\r\n')
    CAPTURE = re.compile(r'\|[A-Za-z0-9 \-_]*\|[A-Za-z0-9 \-]*\|[A-Za-z0-9 \-]*\|')
    servers = [line for line in servers if CAPTURE.match(line)]
    for line in servers[1:]:
        key = line.split('|')[1].strip()
        for key2, value in zip(['client name', 'token', 'submitted model'], line.split('|')[1:4]):
            clients_dict[key][key2.strip()] = value.strip()  
    for instance in clients_dict:
        clients_dict[instance]['train_info'] = get_train_info(instance, child)       
    return list(clients_dict.values())


def get_server_status(child):
    servers = run('check_status server', child).split('\r\n')
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


def get_train_info(instance, child):
    log = run(f'cat {instance} log.txt', child)
    return parse_log(log)