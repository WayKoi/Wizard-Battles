import socket, select, json, random, time
from threading import Thread

import os
clear = 'cls' if os.name == 'nt' else 'clear'

import items
from items import Spell

from player import Client, Player

from battle import Battle

import message as ms
from message import out
from message import CONNECTED, DISCONNECT_MESSAGE, PONG_MESSAGE, PING_MESSAGE, CLEAR_MESSAGE
from message import QUEUE_MESSAGE, COMM_MESSAGE, NAME_PROMPT, POTION_ARMOUR_MESSAGE

from constant import START_STATE, INIT_NAME, BUILD_T1, BUILD_T2, BUILD_T3, BUILD_PA, BATTLE_CHOOSE, BATTLE_QUEUE, BATTLE_WAIT, BATTLE_PROMPT

from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

from constant import VISUALS, MOVE_NAMES, UP, DOWN, LEFT, RIGHT

from constant import DAMAGING, HEALING, BUFF

from battle import A, B

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
    
    out(ms.DEBUG, f'Recieved : {message}')

    if message == DISCONNECT_MESSAGE:
        disconnect(socket)
    elif message == PONG_MESSAGE:
        out(ms.PING_PONG, f'{get_name(socket)} Ponged')
        pings.remove(socket)
    else:
        handle_message(players[clients[socket]], message)

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

    send(socket, DISCONNECT_MESSAGE)

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
    copy = sockets.copy()
    for sock in copy:
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
    # ping = Thread(target = ping_pong)

    while not shutdown:
        if not con.is_alive():
            con = Thread(target = connect_thread)
            con.start()
            out(ms.DEBUG, '<connect> started')

        if not rec.is_alive():
            rec = Thread(target = receive_thread)
            rec.start()
            out(ms.DEBUG, '<receive> started')
        
        # if not ping.is_alive():
        #     ping = Thread(target = ping_pong)
        #     ping.start()
        #     out(ms.DEBUG, '<ping-pong> started')

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

# ------------------------------
# Message handling 
# ------------------------------

def handle_message(player: Player, message: str):
    data = json.loads(message)
    extra = []

    # check players state and process message accordingly
    if player.state == START_STATE:
        player.state = INIT_NAME
        send(player.client.socket, CONNECTED)

    elif player.state == INIT_NAME:
        player.client.name = data['response'][0]
        
        index = min(int(data['response'][1]) - 1, len(VISUALS) - 1)
        index = max(index, 0)
        player.visual = VISUALS[index]
    
        player.state = BUILD_T1

        out(ms.CONNECTION, f"Renamed {player.client.address} -> '{player.client.name}' -> {player.visual}")
    elif player.state == BUILD_T1:
        player.state = BUILD_T2

        spell = items.get_spell(data['response'][0])
        if spell == None:
            player.state = BUILD_T1
        
        give_spell(player, spell)
    elif player.state == BUILD_T2:
        player.state = BUILD_T3

        spell = items.get_spell(data['response'][0])
        if spell == None:
            player.state = BUILD_T2
        
        give_spell(player, spell)
    elif player.state == BUILD_T3:
        player.state = BUILD_PA

        spell = items.get_spell(data['response'][0])
        if spell == None:
            player.state = BUILD_T3

        give_spell(player, spell)
    elif player.state == BUILD_PA:
        player.state = BATTLE_QUEUE

        choice = data['response'][0]

        if choice == 'potion':
            out(ms.CHOICE, f'{player.client.get_name()} obtained a potion')
            pass
        elif choice == 'armour':
            out(ms.CHOICE, f'{player.client.get_name()} obtained armour')
            pass

        out(ms.QUEUE, f'{player.client.get_name()} enters the queue')
    elif player.state == BATTLE_PROMPT:
        battle = get_battle(player.client.socket)

        if battle == None:
            out(ms.ERROR, f'Player {player.client.get_name()} is not part of any battle')
            return

        plan = battle.players[player.client.socket].plan
        res = data['response'][0]

        if res == 'up':
            plan.aim = UP
        elif res == 'down':
            plan.aim = DOWN
        elif res == 'left':
            plan.aim = LEFT
        elif res == 'right':
            plan.aim = RIGHT
        elif res.isdigit():
            plan.aim = int(res) - 1

        player.state = BATTLE_CHOOSE

    elif player.state == BATTLE_CHOOSE:
        battle = get_battle(player.client.socket)
        if battle == None:
            return
        
        prompt = battle.plan_turn(player.client.socket, data)

        if prompt != None:
            player.state = BATTLE_PROMPT

            send(player.client.socket, json.dumps({
                'prompts': [
                    prompt
                ]
            }))

        check_battle(battle)

    # send proper message

    handle_client(player)
    
def handle_client(player: Player):
    if player.state == INIT_NAME:
        send(player.client.socket, NAME_PROMPT)
    elif player.state == BUILD_T1:
        send(player.client.socket, items.create_message(1, 3))
    elif player.state == BUILD_T2:
        send(player.client.socket, items.create_message(2, 2))
    elif player.state == BUILD_T3:
        send(player.client.socket, items.create_message(3, 2))
    elif player.state == BUILD_PA:
        send(player.client.socket, POTION_ARMOUR_MESSAGE)
    elif player.state == BATTLE_QUEUE:
        send(player.client.socket, QUEUE_MESSAGE)
        check_queue()
    elif player.state == BATTLE_CHOOSE:
        send(player.client.socket, COMM_MESSAGE)

        player.state = BATTLE_WAIT
        battle = get_battle(player.client.socket)
        
        if battle == None:
            out(ms.ERROR, f'Player {player.client.get_name()} is not part of any battle')
            return
        
        check_battle(battle)

def get_battle(socket: socket.socket) -> Battle:
    for battle in battles:
        if battle.part_of(socket):
            return battle
    
    return None

def give_spell(player: Player, spell: Spell):
    player.spells.append(spell)
    
    send(player.client.socket, json.dumps({
        'messages': [
            f'{player.client.get_name()} got a {spell.display_name()} spell',
            '!FREEZE'
        ]
    }))

    out(ms.CHOICE, f'{player.client.get_name()} got {spell.display_name()}')

def check_queue():
    waiting = []
    for socket in sockets:
        player = players[clients[socket]]

        if player.state == BATTLE_QUEUE:
            waiting.append(player)
    
    out(ms.DEBUG, f'{len(waiting)} are waiting')
    while len(waiting) >= 2:
        a = waiting.pop(0)
        b = waiting.pop(0)

        a.state = BATTLE_CHOOSE
        b.state = BATTLE_CHOOSE

        battle = Battle(a, b)
        battles.append(battle)

        out(ms.QUEUE, f'Matched {a.client.get_name()} and {b.client.get_name()}')

        send(a.client.socket, json.dumps({
            'messages': [
                f'Matched with {b.client.get_name()}',
                '!FREEZE'
            ]
        }))

        send(b.client.socket, json.dumps({
            'messages': [
                f'Matched with {a.client.get_name()}',
                '!FREEZE'
            ]
        }))

        send_battle(battle)

def send_battle(battle: Battle):
    send(battle.a.player.client.socket, battle.get_message(A))
    send(battle.b.player.client.socket, battle.get_message(B))

def check_battle(battle: Battle):
    if battle.a.player.state != BATTLE_WAIT or battle.b.player.state != BATTLE_WAIT:
        return
    
    messages = battle.play_turns()
    mess = json.dumps({
        'messages': messages
    })

    send(battle.a.player.client.socket, mess)
    send(battle.b.player.client.socket, mess)

    if battle.finished:
        battles.remove(battle)

        handle_client(battle.a.player)
        handle_client(battle.b.player)
    else:
        send_battle(battle)

# -----------------------
# Main
# -----------------------

def start():
    server.listen()
    out(ms.SERVER, f'Server started on {LOCAL_IP}')

if __name__ == '__main__':
    os.system(clear)

    start()
    ms.enable_debug = False

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
    server.detach()

    out(ms.SERVER, 'Shut Down Successful')
    
    
    

