import socket, select, json, random, time
from threading import Thread

import os
clear = 'cls' if os.name == 'nt' else 'clear'

import items

from player import Client, Player

from battle import Battle

import message as ms
from message import out
from message import DISCONNECT_MESSAGE, PONG_MESSAGE, PING_MESSAGE, CLEAR_MESSAGE
from message import QUEUE_MESSAGE, COMM_MESSAGE, NAME_PROMPT

from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

from constant import VISUALS, POS_NAMES

from constant import DAMAGING, HEALING, BUFF

HEADER = 64
PORT = 5050
LOCAL_IP = socket.gethostbyname(socket.gethostname())
ADDR = (LOCAL_IP, PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

sockets = []
clients = {}

pings = []

battles = []

players = {}
battles = []

shutdown = False

# --------------------------------------
# Send / Recieve
# --------------------------------------

def receive(socket: socket.socket):
    header = socket.recv(HEADER).decode(FORMAT).strip()
            
    if not header:
        return
        
    length = int(header)
    message = socket.recv(length).decode(FORMAT).strip()
    
    if message == DISCONNECT_MESSAGE:
        disconnect(socket)
    elif message == PONG_MESSAGE:
        out(ms.PING_PONG, f'{get_name(socket)} Ponged')
        pings.remove(socket)
    else:
        pass # TODO handle message

def send(socket: socket.socket, message: str) -> bool:
    try:
        encoded_message = message.encode(FORMAT)
        message_length = len(encoded_message)
        
        # convert the message length into bytes
        header_bytes = str(message_length).encode(FORMAT)
        # pad so it matches the header
        header_bytes += b' ' * (HEADER - len(header_bytes))
        
        # send the header
        socket.send(header_bytes)
        # send the message
        socket.send(encoded_message)

        return True
    except:
        out(ms.CONNECTION, f'Unable to send message to {get_name(socket)}')
        disconnect(socket)
        return False

# --------------------------------------
# Connection
# --------------------------------------

def disconnect(socket: socket.socket):
    name = get_name(socket)

    socket.detach()
    del players[clients[socket]]
    del clients[socket]
    sockets.remove(socket)

    out(ms.CONNECTION, f"{name} Disconnected")
    active_clients()

def connect():
    conn, addr = server.accept()
    
    sockets.append(conn)
    client = Client(conn, addr)
    clients[conn] = client
    players[client] = Player(client)
    
    print(ms.CONNECTION, f'{addr} connected')
    active_clients()

def active_clients():
    print(ms.CONNECTION, f'{len(sockets)} active clients')

def disconnect_all():
    for sock in sockets:
        disconnect(sock)

# -------------------------------------------
# Clients
# -------------------------------------------

def get_name(socket: socket.socket):
    return clients[socket].get_name()

# ----------------------------------------
# Threads
# ----------------------------------------

def thread_handler():
    con = Thread(target = connect_thread)
    rec = Thread(target = receive_thread)
    ping = Thread(target = ping_pong)

    while not shutdown:
        if not con.is_alive():
            con = Thread(target = connect_thread)
            con.start()
            out(ms.DEBUG, '<connect> started')

        if not rec.is_alive():
            rec = Thread(target = receive_thread)
            rec.start()
            out(ms.DEBUG, '<receive> started')
        
        if not ping.is_alive():
            ping = Thread(target = ping_pong)
            ping.start()
            out(ms.DEBUG, '<ping-pong> started')

        time.sleep(2)

def connect_thread():
    while not shutdown:
        try:
            read, write, err = select.select([server], [], [], 1)
            
            if len(read) > 0:
                connect()
        except:
            pass

def receive_thread():
    while not shutdown:
        try:
            read, write, err = select.select(sockets, [], [], 1)
            
            for client in read:
                receive(client)
        except:
            pass

def ping_pong():
    counter = 0
    timer = 30

    while not shutdown:
        time.sleep(1)
        counter += 1

        if counter >= timer:
            counter = 0
            for sock in pings:
                disconnect(sock)

            pings.clear()

            for sock in sockets:
                out(ms.PING_PONG, f'{get_name(sock)} Pinged')
                success = send(sock, PING_MESSAGE)
                if success:
                    pings.append(sock)

# -----------------------
# Main
# -----------------------

def start():
    server.listen()
    out(ms.SERVER, f'Server started on {LOCAL_IP}')

if __name__ == '__main__':
    start()

    handler = Thread(target = thread_handler)
    handler.start()
    
    while not shutdown:
        string = input()
        if string == 'stop':
            shutdown = True
            out(ms.SERVER, 'Shutting Down')
            disconnect_all()
        elif string == 'clear' or string == 'cls':
            os.system(clear)
            out(ms.SERVER, f'Server running on {LOCAL_IP}')
        
    handler.join()

    out(ms.SERVER, 'Shut Down Successful')
    
    
    

