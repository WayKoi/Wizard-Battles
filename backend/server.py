import socket
import select
import json
from threading import Thread
import items
import random
import time

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
CLEAR_MESSAGE = '!CLEAR'

GAME_INIT = 0
GAME_VISUAL = -1
GAME_START = 1

GAME_TOKEN = 2
GAME_SPELL = 3
GAME_POTION = 4

GAME_QUEUE = 5
GAME_BATTLE = 6

BATTLE_CHOOSE = 7
BATTLE_TARGET = 8
BATTLE_WAIT = 9

TOKEN_SPELL = 1
TOKEN_ARMOUR = 2
TOKEN_POTION = 3

LEFT = 0
MIDDLE = 1
RIGHT = 2

POS_NAMES = [
    'left',
    'middle',
    'right'
]

VISUALS = [
    '(O_O)',
    '(^_^)',
    '(+_+)',
    '(>.<)',
    '(^_-)',
    '(o-o)',
    '(OwO)',
    '(UwU)'
]

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

COMM_MESSAGE = json.dumps({
    'messages': [
        YELLOW + 'Communicating...' + RESET
    ]
})

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

full = [server]
clients = {}

battles = []

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
            clients[client]['game-state'] = GAME_VISUAL

        elif state == GAME_VISUAL:
            print(f'[GAVE CLIENT NAME] {clients[client]["address"]} -> {message}')
            clients[client]['name'] = message
            
            print(f'[ASKING FOR VISUAL] {clients[client]["address"]}')
            send(client, visualPrompt())

            clients[client]['game-state'] = GAME_START
            
        elif state == GAME_START:
            clients[client]['visual'] = VISUALS[int(message) - 1]
            print(f'[GAVE CLIENT VISUAL] {clients[client]["name"]} -> {clients[client]["visual"]}')

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

                matchmaking()
        elif state == GAME_BATTLE:
            got = getBattle(client)

            if got == None:
                return

            current = got['battle']
            player = got['player']

            if message.isdigit(): # cast a spell
                player['move'] = {
                    'spell': player['spells'][int(message) - 1], 
                    'target': 0
                }

                clients[client]['game-state'] = BATTLE_TARGET
                send(client, json.dumps({
                    'messages': [
                        'Where would you like to target?',
                        '  1. Left',
                        '  2. Middle',
                        '  3. Right',
                        ''
                    ],
                    'input': 'choice',
                    'choices': [ '1', '2', '3' ]
                }))
            else: # must be a movement
                player['move'] = message
                clients[client]['game-state'] = BATTLE_WAIT

                send(client, COMM_MESSAGE)

                if current['first'] == None:
                    current['first'] = player

                checkBattle(current)
        elif state == BATTLE_TARGET:
            got = getBattle(client)

            if got == None:
                return

            current = got['battle']
            player = got['player']

            target = int(message) - 1
            player['move']['target'] = target
            clients[client]['game-state'] = BATTLE_WAIT

            send(client, COMM_MESSAGE)

            checkBattle(current)
                
def getBattle(client):
    current = None
    player = None

    for battle in battles:
        if battle['a']['client'] == client:
            player = battle['a']
            current = battle
            break
        elif battle['b']['client'] == client:
            player = battle['b']
            current = battle
            break

    if current == None:
        return None
    
    return {
        'battle': battle,
        'player': player
    }

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
        'choices': [],
        'visual': VISUALS[0]
    }
    
    print(f'[NEW CONNECTION] {addr} connected')
    print(f'[ACTIVE CLIENTS] {len(clients)}')

def dealDamage(spell, target, opponent) -> str:
    damage = spell['dice']['base']

    if 'd4' in spell['dice']:
        for i in range(spell['dice']['d4']):
            damage += random.randint(1, 4)
    
    if 'd6' in spell['dice']:
        for i in range(spell['dice']['d6']):
            damage += random.randint(1, 6)
    
    if 'd8' in spell['dice']:
        for i in range(spell['dice']['d8']):
            damage += random.randint(1, 8)

    if 'd10' in spell['dice']:
        for i in range(spell['dice']['d10']):
            damage += random.randint(1, 10)
    
    distance = abs(target - opponent['position'])

    if distance <= spell['range']:
        damage = round(damage / (distance + 1))
        opponent['health'] -= damage
        message = opponent['name'] + ' took ' + RED + str(damage) + RESET + ' damage'
    else:
        message = spell['visual'] + ' Missed ' + opponent['name'] + '!'

    return message

def createBattle(clientA, clientB):
    return {
        'a': {
            'name': clients[clientA]['name'],
            'visual': clients[clientA]['visual'],
            'client': clientA,
            'health': clients[clientA]['health'],
            'spells': wrapSpells(clients[clientA]['spells']),
            'position': MIDDLE,
            'move': None
        },
        'b': {
            'name': clients[clientB]['name'],
            'visual': clients[clientB]['visual'],
            'client': clientB,
            'health': clients[clientB]['health'],
            'spells': wrapSpells(clients[clientB]['spells']),
            'position': MIDDLE,
            'move': None
        },
        'turn': 1,
        'first': None
    }

def wrapSpells(spells):
    wrapped = []

    for spell in spells:
        wrapped.append({
            'spell': spell,
            'cooldown': 0,
            'visual': spell['visual']
        })
    
    return wrapped

def checkBattle(battle):
    a = battle['a']
    b = battle['b']

    mess = {
        'messages': []
    }

    print(RED + '[CHECK BATTLE]' + RESET)

    if clients[a['client']]['game-state'] == BATTLE_WAIT and clients[b['client']]['game-state'] == BATTLE_WAIT:
        if battle['first'] == a:
            mess['messages'].extend(playTurn(a, b))
            mess['messages'].extend(playTurn(b, a))
        else:
            mess['messages'].extend(playTurn(b, a))
            mess['messages'].extend(playTurn(a, b))

        a['move'] = None
        b['move'] = None

        battle['turn'] += 1
        battle['first'] = None

        finished = True

        aFell = a['health'] <= 0
        bFell = b['health'] <= 0

        if aFell and bFell:
            mess['messages'].append('Both wizards are down, Game ends in a tie!')
        elif aFell:
            mess['messages'].append(RED + f'{a["name"]} falls!' + RESET)
            mess['messages'].append(GREEN + f'{b["name"]} is the Winner!' + RESET)
        elif bFell:
            mess['messages'].append(RED + f'{b["name"]} falls!' + RESET)
            mess['messages'].append(GREEN + f'{a["name"]} is the Winner!' + RESET)
        else:
            mess['messages'].append('The Battle Continues!')
            finished = False

        time.sleep(1)

        mess = json.dumps(mess)
        send(a['client'], mess)
        send(b['client'], mess)

        if not finished:
            clients[a['client']]['game-state'] = GAME_BATTLE
            clients[b['client']]['game-state'] = GAME_BATTLE

            time.sleep(5)

            send(a['client'], battleMessage(battle, a['client']))
            send(b['client'], battleMessage(battle, b['client']))

def playTurn (a, b):
    mess = []

    if a['move'] == 'left':
        a['position'] -= 1
        mess.append(f'{a["name"]} moves left!')
    elif a['move'] == 'right':
        a['position'] += 1
        mess.append(f'{a["name"]} moves right!')
    else:
        target = POS_NAMES[a['move']['target']]
        mess.append(f'{a["name"]} casts {a["move"]["spell"]["visual"]} in the {target}!')
        mess.append(dealDamage(a['move']['spell']['spell'], a['move']['target'], b))

    return mess

# MESSAGES

def tokenMessage(client) -> str:
    state = clients[client]

    message = {
        'messages': [
            'You have ' + YELLOW + str(state["tokens"]) + RESET + ' tokens left',
            'You can spend a token to purchase one of the following',
            '  1. A New Spell',
            '  2. Armour',
            '  3. A Potion',
            'Please select a number 1-3'
        ],
        'input': 'choice',
        'choices': [
            '1', '2', '3'
        ]
    }

    return json.dumps(message)

def battleMessage(battle, client):
    if battle['a']['client'] == client:
        player = battle['a']
        opponent = battle['b']
    else:
        player = battle['b']
        opponent = battle['a']
    
    message = {
        'messages': [
            CLEAR_MESSAGE,
            f'Turn {battle["turn"]}',
            printPosition(opponent),
            '',
            printPosition(player, True),
            '',
            GREEN + 'Options' + RESET,
        ],
        'input': 'choice',
        'choices': []
    }

    count = 1
    for spell in player['spells']:
        message['messages'].append(f'  {count}. {spell["visual"]}')
        message['choices'].append(str(count))
        count += 1

    move = 'you can also move '

    if player['position'] == MIDDLE:
        move += 'left or right'
        message['choices'].append('left')
        message['choices'].append('right')
    elif player['position'] == LEFT:
        move += 'right'
        message['choices'].append('right')
    else:
        move += 'left'
        message['choices'].append('left')

    message['messages'].append(move)
    message['messages'].append('What would you like to do?')

    return json.dumps(message)

def printPosition(battle, player = False):
    blank = '  •  '
    visual = battle['visual']

    line = [
        blank,
        blank,
        blank
    ]

    if not player:
        line[battle['position']] = RED + visual + RESET
    else:
        line[battle['position']] = GREEN + visual + RESET

    return line[0] + line[1] + line[2]

def visualPrompt():
    prompt = {
        'messages': [
            'What would you like your wizard to look like?'
        ],
        'input': 'choice',
        'choices': []
    }

    count = 1
    for visual in VISUALS:
        prompt['messages'].append(f'  {count}. {visual}')
        prompt['choices'].append(str(count))
        count += 1
    
    return json.dumps(prompt)


def matchmaking():
    ready = []

    for client in clients:
        if clients[client]['game-state'] == GAME_QUEUE:
            ready.append(client)
    
    print(f'[MATCHMAKING] {len(ready)} are waiting')

    if len(ready) >= 2:
        send(ready[0], json.dumps({
            'messages': [
                f'You have been matched with {clients[ready[1]]["name"]}'
            ]
        }))

        send(ready[1], json.dumps({
            'messages': [
                f'You have been matched with {clients[ready[0]]["name"]}'
            ]
        }))

        clients[ready[0]]['game-state'] = GAME_BATTLE
        clients[ready[1]]['game-state'] = GAME_BATTLE

        print(f'[MATCHMAKING] paired up {clients[ready[0]]["name"]} with {clients[ready[1]]["name"]}')

        battle = createBattle(ready[0], ready[1])
        battles.append(battle)

        send(ready[0], battleMessage(battle, ready[0]))
        send(ready[1], battleMessage(battle, ready[1]))

if __name__ == '__main__':
    start()

    print(VISUALS)
    
    connectThread = Thread(target = connectLoop, args = ())
    connectThread.start()
    
    while not shutdown:
        string = input()
        if string == 'stop':
            for client in clients:
                send(client, DISCONNECT_MESSAGE)
            
            shutdown = True
        
    connectThread.join()
    
    
    

