import socket
import select
from threading import Thread

HEADER = 64
PORT = 5050
LOCAL_IP = socket.gethostbyname(socket.gethostname())
ADDR = (LOCAL_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

full = [server]
clients = {}

shutdown = False

def receive(client: socket.socket):
    header = client.recv(HEADER).decode(FORMAT).strip()
            
    if not header:
        return
        
    length = int(header)
    message = client.recv(length).decode(FORMAT).strip()
    
    if message == DISCONNECT_MESSAGE:
        disconnect(client)
    else:
        print(f"[{clients[client]['address']}] : {message}")

def send(client: socket.socket, message: str):
    try:
        encoded_message = message.encode(FORMAT)
        message_length = len(encoded_message)
        
        # convert the message length into bytes
        header_bytes = str(message_length).encode(FORMAT)
        # pad so it matches the header
        header_bytes += b' ' * (HEADER - len(header_bytes))
        
        # send the header
        client.send(header_bytes)
        # send the message
        client.send(encoded_message)
    except:
        print(f"[ERROR] Unable to send message to {clients[client]['address']}")

def disconnect(client):
    print(f"[{clients[client]['address']}] DISCONNECTED")
    full.remove(client)
    del clients[client]
    print(f'[ACTIVE CLIENTS] {len(clients)}')

def start():
    server.listen()
    print(f'[SERVER] Server started on {LOCAL_IP}')

def connectLoop():
    while not shutdown:
        try:
            read, write, err = select.select(full, [], [], 1)
            
            for s in read:
                if s is server:
                    connect()
                else:
                    receive(s)
        except:
            pass

def connect():
    conn, addr = server.accept()
    
    full.append(conn)
    clients[conn] = {
        'address': addr
    }
    
    print(f'[NEW CONNECTION] {addr} connected')
    print(f'[ACTIVE CLIENTS] {len(clients)}')

if __name__ == '__main__':
    start()
    
    connectThread = Thread(target = connectLoop, args = ())
    connectThread.start()
    
    while not shutdown:
        string = input()
        if string == 'stop':
            for client in clients:
                send(client, DISCONNECT_MESSAGE)
            
            shutdown = True
        
    connectThread.join()
    
    
    

