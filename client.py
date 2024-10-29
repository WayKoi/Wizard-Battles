import socket
from threading import Thread

HEADER = 64
PORT = 5050
SERVER = '192.168.2.200'
FORMAT = 'utf-8'

LOCAL_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

DISCONNECT_MESSAGE = '!DISCONNECT'

class Client:
    def __init__(self):
        self.connected = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def send(self, message: str):
        if not self.connected:
            return
        
        try:
            encoded_message = message.encode(FORMAT)
            message_length = len(encoded_message)
            
            # convert the message length into bytes
            header_bytes = str(message_length).encode(FORMAT)
            # pad so it matches the header
            header_bytes += b' ' * (HEADER - len(header_bytes))
            
            # send the header
            self.client.send(header_bytes)
            # send the message
            self.client.send(encoded_message)
        except:
            print('Could not send message')
    
    def disconnect(self):
        if not self.connected:
            return
        
        self.send(DISCONNECT_MESSAGE)
        self.client.detach()
        
        self.connected = False
        print('Client Disconnected')

    def receive(self):
        if not self.connected:
            return
        
        try:
            header = self.client.recv(HEADER).decode(FORMAT).strip()
            if not header:
                return
            
            message_length = int(header)
            message = self.client.recv(message_length).decode(FORMAT).strip()
            
            if message == DISCONNECT_MESSAGE:
                self.disconnect()
                return

            self.process(message)
        except:
            pass
    
    def process(message: str):
        pass
    
    def __recieveLoop(self):
        while self.connected:
            self.receive()
    
    def connect(self):
        self.client.connect(ADDR)
        self.connected = True
        
        recvWait = Thread(target = self.__recieveLoop, args = ())
        recvWait.start()

if __name__ == '__main__':
    client = Client()
    client.connect()
    
    client.send('Hello, World!')
    client.disconnect()
