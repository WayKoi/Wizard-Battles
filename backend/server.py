import socket
import select
import json
from threading import Thread
import items

BLACK = '\u001b[30m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
YELLOW = '\u001b[33m'
BLUE = '\u001b[34m'
MAGENTA = '\u001b[35m'
CYAN = '\u001b[36m'
WHITE = '\u001b[37m'
RESET = '\u001b[0m'

HEADER = 64
PORT = 5050
LOCAL_IP = socket.gethostbyname(socket.gethostname())
ADDR = (LOCAL_IP, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

GAME_INIT = 0
GAME_START = 1

GAME_TOKEN = 2
GAME_SPELL = 3
GAME_POTION = 4

GAME_QUEUE = 5
GAME_BATTLE = 6

TOKEN_SPELL = 1
TOKEN_ARMOUR = 2
TOKEN_POTION = 3

NAME_PROMPT = json.dumps({
    'messages': [
        GREEN + 'Successfully Connected!' + RESET,
        'What would you like to name your wizard?'
    ],
    'input': 'string'
})

QUEUE_MESSAGE = json.dumps({
    'messages': [
        CYAN + '      You have used all your tokens' + RESET,
        RED +  '        Entering the Battle Queue' + RESET,
               'You will be matched up with an opponent soon'
    ]
})

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

        state = clients[client]['game-state']

        if state == GAME_INIT:
            print(f'[ASKING FOR NAME] {clients[client]["address"]}')
            send(client, NAME_PROMPT)
            clients[client]['game-state'] = GAME_START

        elif state == GAME_START:
            clients[client]['name'] = message
            print(f'[GAVE CLIENT NAME] {clients[client]["address"]} -> {message}')
            send(client, tokenMessage(client))
            clients[client]['game-state'] = GAME_TOKEN

        elif state == GAME_TOKEN:
            # prompt for item or potion, or whatever they chose
            choice = int(message)

            if choice == TOKEN_SPELL:
                spells = items.GetSpells(2)
                clients[client]['choices'] = spells

                send(client, json.dumps({
                    'messages': [
                        'Please choose a spell from the below options',
                        '1. ' + spells[0]['visual'] + ' (' + spells[0]['description'] + ')',
                        '2. ' + spells[1]['visual'] + ' (' + spells[1]['description'] + ')'
                    ],
                    'input': 'choice',
                    'choices': [ '1', '2' ]
                }))

                clients[client]['game-state'] = GAME_SPELL
            elif choice == TOKEN_ARMOUR:
                pass
            elif choice == TOKEN_POTION:
                pass

            clients[client]['tokens'] -= 1
        elif state == GAME_SPELL:
            choice = int(message) - 1

            spell = clients[client]['choices'][choice]
            send(client, json.dumps({
                'messages': [
                    spell['visual'] + ' has been added to your spellbook'
                ]
            }))

            clients[client]['spells'].append(spell)

            if clients[client]['tokens'] > 0:
                send(client, tokenMessage(client))
                clients[client]['game-state'] = GAME_TOKEN
            else:
                print(f'[ADDED TO BATTLE QUEUE] {clients[client]["address"]}')
                send(client, QUEUE_MESSAGE)
                clients[client]['game-state'] = GAME_QUEUE

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
        'address': addr,
        'game-state': GAME_INIT,
        'spells': [],
        'tokens': 5,
        'rounds-won': 0,
        'health': 50,
        'choices': []
    }
    
    print(f'[NEW CONNECTION] {addr} connected')
    print(f'[ACTIVE CLIENTS] {len(clients)}')

# MESSAGES

def tokenMessage(client) -> str:
    state = clients[client]

    message = {
        'messages': [
            'You have ' + YELLOW + str(state["tokens"]) + RESET + ' tokens left',
            'You can spend a token to purchase one of the following',
            '\t1. A New Spell',
            '\t2. Armour',
            '\t3. A Potion',
            'Please select a number 1-3'
        ],
        'input': 'choice',
        'choices': [
            '1', '2', '3'
        ]
    }

    return json.dumps(message)

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
    
    
    

