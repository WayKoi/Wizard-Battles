import socket, select, json, random, time
from threading import Thread

import os
clear = 'cls' if os.name == 'nt' else 'clear'

import items

import message
from message import DISCONNECT_MESSAGE, PONG_MESSAGE, PING_MESSAGE, CLEAR_MESSAGE
from message import QUEUE_MESSAGE, COMM_MESSAGE, NAME_PROMPT

from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

from constant import GAME_INIT, GAME_BATTLE, GAME_POTION, GAME_QUEUE, GAME_SPELL, GAME_START, GAME_TOKEN, GAME_VISUAL
from constant import BATTLE_CHOOSE, BATTLE_TARGET, BATTLE_WAIT
from constant import TOKEN_ARMOUR, TOKEN_POTION, TOKEN_SPELL
from constant import LEFT, RIGHT, MIDDLE
from constant import VISUALS, POS_NAMES

from constant import DAMAGING, HEALING, BUFF

HEADER = 64
PORT = 5050
LOCAL_IP = socket.gethostbyname(socket.gethostname())
ADDR = (LOCAL_IP, PORT)
FORMAT = 'utf-8'

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

            clients[client]['tokens'] -= 1

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
                gain = random.randint(10, 25)
                clients[client]['health'] += gain
                
                print(f'[GAIN HEALTH] {clients[client]["name"]} gained {gain} health')

                send(client, json.dumps({
                    'messages': [
                        f'{clients[client]["name"]} gained {GREEN}{gain}{RESET} Health!',
                        f'{clients[client]["name"]} now has {GREEN}{clients[client]["health"]}{RESET} health'
                    ]
                }))

                if clients[client]['tokens'] > 0:
                    send(client, tokenMessage(client))
                else:
                    print(f'[ADDED TO BATTLE QUEUE] {clients[client]["address"]}')
                    send(client, QUEUE_MESSAGE)
                    clients[client]['game-state'] = GAME_QUEUE

                    matchmaking()
            elif choice == TOKEN_POTION:
                gain = items.GetPotion()
                clients[client]['potions'].append(gain)
                
                print(f'[GET POTION] {clients[client]["name"]} got {gain["visual"]}')

                send(client, json.dumps({
                    'messages': [
                        f'{clients[client]["name"]} got a {gain["visual"]}',
                        f'{gain["description"]}'
                    ]
                }))

                if clients[client]['tokens'] > 0:
                    send(client, tokenMessage(client))
                else:
                    print(f'[ADDED TO BATTLE QUEUE] {clients[client]["address"]}')
                    send(client, QUEUE_MESSAGE)
                    clients[client]['game-state'] = GAME_QUEUE

                    matchmaking()
            
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
                choice = int(message) - 1

                if choice < len(player['spells']):
                    player['move'] = {
                        'spell': player['spells'][choice], 
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
                else: # potion
                    choice -= len(player['spells'])
                    player['move'] = player['potions'][choice]

                    clients[client]['game-state'] = BATTLE_WAIT
                    send(client, COMM_MESSAGE)

                    if current['first'] == None:
                        current['first'] = player

                    checkBattle(current)

            elif message == 'pass':
                player['move'] = None
                clients[client]['game-state'] = BATTLE_WAIT
                send(client, COMM_MESSAGE)

                checkBattle(current)

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
                
def visual(client):
    return clients[client]['name']

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
        'potions': [],
        'tokens': 4,
        'rounds-won': 0,
        'health': 50,
        'choices': [],
        'visual': VISUALS[0]
    }
    
    print(f'[NEW CONNECTION] {addr} connected')
    print(f'[ACTIVE CLIENTS] {len(clients)}')

def rollDice(rollable):
    amount = rollable['dice']['base']

    if 'd4' in rollable['dice']:
        for i in range(rollable['dice']['d4']):
            amount += random.randint(1, 4)
    
    if 'd6' in rollable['dice']:
        for i in range(rollable['dice']['d6']):
            amount += random.randint(1, 6)
    
    if 'd8' in rollable['dice']:
        for i in range(rollable['dice']['d8']):
            amount += random.randint(1, 8)

    if 'd10' in rollable['dice']:
        for i in range(rollable['dice']['d10']):
            amount += random.randint(1, 10)
    
    return amount

def dealDamage(spell, target, opponent) -> str:
    damage = rollDice(spell)
    
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
            'potions': wrapPotions(clients[clientA]['potions']),
            'buffs': [],
            'position': MIDDLE,
            'move': None
        },
        'b': {
            'name': clients[clientB]['name'],
            'visual': clients[clientB]['visual'],
            'client': clientB,
            'health': clients[clientB]['health'],
            'spells': wrapSpells(clients[clientB]['spells']),
            'potions': wrapPotions(clients[clientB]['potions']),
            'buffs': [],
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

def wrapPotions(potions):
    wrapped = []

    for potion in potions:
        wrapped.append({
            'potion': potion,
            'used': False,
            'visual': potion['visual']
        })

    return wrapped

def checkBattle(battle):
    a = battle['a']
    b = battle['b']

    mess = {
        'messages': []
    }

    # print(RED + '[CHECK BATTLE]' + RESET)

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
            mess['messages'].append('The Battle Will Continue!')
            finished = False

        time.sleep(1)

        mess = json.dumps(mess)
        send(a['client'], mess)
        send(b['client'], mess)

        if not finished:
            clients[a['client']]['game-state'] = GAME_BATTLE
            clients[b['client']]['game-state'] = GAME_BATTLE

            time.sleep(3)

            for spell in a['spells']:
                if spell['cooldown'] > 0:
                    spell['cooldown'] -= 1
            
            for spell in b['spells']:
                if spell['cooldown'] > 0:
                    spell['cooldown'] -= 1

            send(a['client'], battleMessage(battle, a['client']))
            send(b['client'], battleMessage(battle, b['client']))
        else:
            battles.remove(battle)

            battle_end(a)
            battle_end(b)

def battle_end(wiz):
    if wiz['health'] <= 0:
        send(wiz['client'], json.dumps({
            'messages': [
                RED + wiz['name'] + ' was slain' + RESET,
                YELLOW + 'Your Journey Ends Here' + RESET,
                ''
            ]
        }))

        send(wiz['client'], DISCONNECT_MESSAGE)
    else:
        client = wiz['client']

        print(f'[ADDED TO BATTLE QUEUE] {clients[client]["address"]}')
        send(client, json.dumps({
            'messages': [
                YELLOW + 'Your Journey Continues' + RESET,
                ''
            ]
        }))
        
        send(client, QUEUE_MESSAGE)
        clients[client]['game-state'] = GAME_QUEUE

        matchmaking()

def playTurn (a, b):
    mess = []

    if a['move'] == None:
        print(f'{CYAN}[BATTLE]{RESET} {a["name"]} passes')
        mess.append(f'{a["name"]} passes their turn')
        return mess

    if a['move'] == 'left':
        print(f'{CYAN}[BATTLE]{RESET} {a["name"]} moves left')
        a['position'] -= 1
        mess.append(f'{a["name"]} moves left!')
    elif a['move'] == 'right':
        print(f'{CYAN}[BATTLE]{RESET} {a["name"]} moves right')
        a['position'] += 1
        mess.append(f'{a["name"]} moves right!')
    elif 'spell' in a['move']:
        a['move']['spell']['cooldown'] = a['move']['spell']['spell']['cooldown'] + 1
        target = POS_NAMES[a['move']['target']]
        
        print(f'{CYAN}[BATTLE]{RESET} {a["name"]} casts {a["move"]["spell"]["visual"]} in the {target}')
        
        mess.append(f'{a["name"]} casts {a["move"]["spell"]["visual"]} in the {target}!')
        mess.append(dealDamage(a['move']['spell']['spell'], a['move']['target'], b))
    else: # potion
        potion = a['move']
        print(f'{CYAN}[BATTLE]{RESET} {a["name"]} drinks a {potion["visual"]}')

        mess.append(f'{a["name"]} drinks a {potion["visual"]}')
        mess.extend(playPotion(a, potion))
    return mess

def playPotion (player, potion):
    mess = []
    base = potion['potion']

    if base['effect'] == HEALING:
        amount = rollDice(base)
        maxheal = clients[player["client"]]['health'] - player['health']
        amount = min(amount, maxheal)

        player['health'] += amount

        mess.append(f'{player["name"]} heals {GREEN}{amount}{RESET} health')
    elif base['effect'] == BUFF:
        pass

    potion['used'] = True

    return mess

# MESSAGES

def tokenMessage(client) -> str:
    state = clients[client]

    message = {
        'messages': [
            f'\n{YELLOW}You have {str(state["tokens"])} tokens left{RESET}',
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
        if spell['cooldown'] <= 0:
            message['messages'].append(f'  {count}. {spell["visual"]}')
            message['choices'].append(str(count))
        else:
            message['messages'].append(f'     {spell["visual"]} ({spell["cooldown"]} turns)')
        
        count += 1
    
    for potion in player['potions']:
        if not potion['used']:
            message['messages'].append(f'  {count}. {potion["visual"]}')
            message['choices'].append(str(count))
        else: 
            message['messages'].append(f'     {potion["visual"]} (used)')
        
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
    
    move += ' or pass'
    message['choices'].append('pass')

    message['messages'].append(move)
    message['messages'].append('What would you like to do?')

    return json.dumps(message)

def printPosition(player, isplayer = False):
    blank = '  •  '
    visual = player['visual']

    line = [
        blank,
        blank,
        blank
    ]

    if not isplayer:
        line[player['position']] = RED + visual + RESET
    else:
        line[player['position']] = GREEN + visual + RESET

    namecard = f'{player["name"]} ({player["health"]} / {clients[player["client"]]["health"]})'

    if isplayer:
        return line[0] + line[1] + line[2] + '\n' + namecard
    
    return namecard + '\n' + line[0] + line[1] + line[2]

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

# thread for making sure threads stay running
# thread for connecting
# thread for recieving
# thread for pinging clients
# main thread takes input to shutdown

if __name__ == '__main__':
    start()

    # print(VISUALS)
    
    connectThread = Thread(target = connectLoop, args = ())
    connectThread.start()
    
    while not shutdown:
        string = input()
        if string == 'stop':
            for client in clients:
                send(client, DISCONNECT_MESSAGE)
        elif string == 'clear':
            os.system(clear)
            
            shutdown = True
        
    connectThread.join()
    
    
    

