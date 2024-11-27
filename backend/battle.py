from player import Player
import socket, json, time

from items import Spell, Potion

from constant import RED, GREEN, RESET, BOLD, BLACK, YELLOW, UNDERLINE
from constant import UP, LEFT, DOWN, RIGHT, MOVE_NAMES

from constant import BATTLE_CHOOSE, START_STATE, BATTLE_QUEUE, BATTLE_PROMPT, INIT_NAME

from items import RELATIVE, ROW, COLUMN, RELATIVE_SYMMETRIC, STATIC

import message as ms

A = 1
B = 2

PASS = -1
MOVEMENT = 0
POTION = 1
ATTACK = 2

class Plan:
    def __init__(self, current) -> None:
        self.spell: SWrap = None
        self.potion: PoWrap = None
        self.aim: int = UP
        self.move: int = None
        self.type = PASS
        self.time = current

class PoWrap:
    def __init__(self, potion: Potion):
        self.potion = potion
        self.used = False

def wrap_potions(potions: list[Potion]):
    wrapped = []
    
    for potion in potions:
        wrapped.append(PoWrap(potion))
        
    return wrapped

class SWrap:
    def __init__(self, spell: Spell) -> None:
        self.spell = spell
        self.cooldown = 0
        if spell.cooldown > 6:
            self.cooldown = spell.cooldown - 6

def wrap_spells(spells: list[Spell]):
    wrapped = []

    for spell in spells:
        wrapped.append(SWrap(spell))
    
    return wrapped

class PWrap:
    def __init__(self, player: Player, name: str):
        self.player = player
        self.name = name
        self.visual = player.visual
        
        self.health = player.health
        
        self.spells: list[SWrap] = wrap_spells(player.spells)
        self.potions: list[PoWrap] = wrap_potions(player.potions)
        self.status  = []

        self.plan: Plan = None
        
        self.position = (0, 0)
    
    def display_health(self):
        build = RED if self.health > 0 else BOLD + BLACK
        
        amt = max(self.player.health, self.health)
        for i in range(amt):
            if self.health == i:
                build += BOLD + BLACK
            
            if i >= self.player.health:
                build += YELLOW
            
            build += '♥'
        
        return build + RESET

    def get_spell(self, name: str):
        name = name.lower()

        for spell in self.spells:
            if spell.spell.name.lower() == name:
                return spell
            
        return None
    
    def get_potion(self, name: str):
        name = name.lower()

        for potion in self.potions:
            if potion.potion.name.lower() == name:
                return potion
            
        return None

class Battle:
    def __init__(self, a: Player, b: Player):
        self.sockets = {
            a.client.socket : a,
            b.client.socket : b
        }
        
        self.a = PWrap(a, a.client.get_name())
        self.a.position = (4, 0)
        
        self.b = PWrap(b, b.client.get_name())
        self.b.position = (0, 4)
        
        self.players = {
            a.client.socket : self.a,
            b.client.socket : self.b
        }

        self.finished = False
    
    # just checks if that socket is part of this battle
    def part_of(self, socket: socket.socket) -> bool:
        if socket in self.sockets:
            return True
    
        return False
    
    def get(self, socket: socket.socket):
        return self.players[socket]
    
    def display_board(self, perspective):
        build = BOLD + BLACK + '    1    2    3    4    5  \n' +  RESET
        empty = '  •  '
        
        for y in range(5):
            build += f'{BOLD + BLACK}{y + 1}{RESET} '

            for x in range(5):
                if self.a.position == (x, y):
                    if perspective == A:
                        build += GREEN
                    else:
                        build += RED
                        
                    build += self.a.visual + RESET
                elif self.b.position == (x, y):
                    if perspective == B:
                        build += GREEN
                    else:
                        build += RED
                        
                    build += self.b.visual + RESET
                else:
                    build += empty
            
            build += '\n'
        
        return build
    
    def display_battle(self, perspective):
        build = ''
        
        if perspective == A:
            build += RED + self.b.name + ' ' + self.b.visual + RESET + '\n'
            build += self.b.display_health() + '\n'
        else:
            build += RED + self.a.name + ' ' + self.a.visual + RESET + '\n'
            build += self.a.display_health() + '\n'
        
        build += f'\n{self.display_board(perspective)}\n'
        
        if perspective == A:
            build += self.a.display_health() + '\n'
            build += GREEN + self.a.name + ' ' + self.a.visual + RESET + '\n'
        else:
            build += self.b.display_health() + '\n'
            build += GREEN + self.b.name + ' ' + self.b.visual + RESET + '\n'
            
        return build

    def play_turns(self):
        for spell in self.a.spells:
            if spell.cooldown > 0:
                spell.cooldown -= 1
        
        for spell in self.b.spells:
            if spell.cooldown > 0:
                spell.cooldown -= 1
    
        afirst = True

        messages = []
        if self.a.plan.type == self.b.plan.type:
            if self.a.plan.time > self.b.plan.time:
                afirst = False
        elif self.a.plan.type > self.b.plan.type:
            afirst = False
        
        if afirst:
            messages.extend(self.__play_turn(self.a))
            messages.append('')

            messages.extend(self.__play_turn(self.b))
            messages.append('')
        else:
            messages.extend(self.__play_turn(self.b))
            messages.append('')
            
            messages.extend(self.__play_turn(self.a))
            messages.append('')

        self.finished = True
        if self.a.health <= 0 and self.b.health <= 0:
            self.a.player.state = INIT_NAME
            self.b.player.state = INIT_NAME

            self.a.player.spells.clear()
            self.a.player.potions.clear()
            
            self.b.player.spells.clear()
            self.b.player.potions.clear()

            messages.append(f'{RED}{self.a.name} {self.a.visual} has fallen!{RESET}')
            messages.append(f'{RED}{self.b.name} {self.b.visual} has fallen!{RESET}')

        elif self.a.health <= 0:
            self.a.player.state = INIT_NAME
            self.b.player.state = BATTLE_QUEUE

            self.a.player.spells.clear()
            self.a.player.potions.clear()

            messages.append(f'{RED}{self.a.name} {self.a.visual} has fallen!{RESET}')
            messages.append(f'{GREEN + BOLD + UNDERLINE}{self.b.name} {self.b.visual} is the victor!{RESET}')

        elif self.b.health <= 0:
            self.a.player.state = BATTLE_QUEUE
            self.b.player.state = INIT_NAME

            self.b.player.spells.clear()
            self.b.player.potions.clear()

            messages.append(f'{RED}{self.b.name} {self.b.visual} has fallen!{RESET}')  
            messages.append(f'{GREEN + BOLD + UNDERLINE}{self.a.name} {self.a.visual} is the victor!{RESET}')  

        else:
            self.a.plan = None
            self.b.plan = None
            self.a.player.state = BATTLE_CHOOSE
            self.b.player.state = BATTLE_CHOOSE

            messages.append(f'{YELLOW}The battle continues{RESET}')
            self.finished = False
        
        messages.append('!FREEZE')
        return messages
        
    def __play_turn(self, player: PWrap):
        plan = player.plan

        messages = []

        if plan.spell != None:
            messages.extend(self.__play_spell(player, plan.spell))
            ms.out(ms.BATTLE, f'{player.name} casts {plan.spell.spell.display_name()}')
            messages.extend(self.board_spell(player, plan.spell, plan.aim))
            
        elif plan.potion != None:
            messages.extend(self.__play_potion(player, plan.potion))
            ms.out(ms.BATTLE, f'{player.name} drinks {plan.potion.potion.display_name()}')
            
        elif plan.move != None:
            messages.extend(self.__move(player, plan.move))
            ms.out(ms.BATTLE, f'{player.name} moves {MOVE_NAMES[plan.move]}')
            messages.extend(self.display_board(A if player == self.a else B).split('\n'))
        
        else:
            messages.append(f'{player.name} passes their turn')
            ms.out(ms.BATTLE, f'{player.name} passes')
        
        return messages
    
    def board_spell(self, player: PWrap, spell: SWrap, direction: int) -> list[str]:
        board = self.display_board(A if player is self.a else B).split('\n')
        
        at = spell.spell.attack_type
        pos = player.position if at == RELATIVE or at == RELATIVE_SYMMETRIC else (player.plan.aim, player.plan.aim)
        spell_display = spell.spell.display_spell(pos, direction).split('\n')
        
        for i in range(len(spell_display)):
            board[i] += '\t' + spell_display[i]
        
        return board
        
    
    def __play_spell(self, player: PWrap, spell: SWrap):
        messages = [spell.spell.get_cast_print(player.name)]
        at = player.plan.spell.spell.attack_type
        pos = player.position if at == RELATIVE or at == RELATIVE_SYMMETRIC else (player.plan.aim, player.plan.aim)
        aim = player.plan.aim if player.plan.aim != None else UP

        spots = spell.spell.get_spots(pos, aim)

        hit = False
        if self.a.position in spots:
            messages.append(f'{self.a.name} is hit!')
            hitprint = f'{self.a.display_health()} -> '
            
            self.a.health -= spell.spell.damage
            hitprint += self.a.display_health()

            messages.append(hitprint)
            
            ms.out(ms.BATTLE, f'{self.a.name} {hitprint}')

            hit = True
        
        if self.b.position in spots:
            messages.append(f'{self.b.name} is hit!')
            hitprint = f'{self.b.display_health()} -> '
            
            self.b.health -= spell.spell.damage
            hitprint += self.b.display_health()

            messages.append(hitprint)

            ms.out(ms.BATTLE, f'{self.b.name} {hitprint}')

            hit = True
        
        if not hit:
            messages.append(f'{spell.spell.display_name()} missed everyone')
        
        spell.cooldown = spell.spell.cooldown

        return messages
    
    def __play_potion(self, player: PWrap, potion: PoWrap):
        heal = player.display_health() + ' -> '
        player.health += potion.potion.heal
        heal += player.display_health()
        
        potion.used = True
        
        messages = [
            f'{player.name} drinks a {potion.potion.display_name()}',
            heal
        ]
        
        return messages
    
    def __move(self, player: PWrap, move: int):
        new = (player.position[0], player.position[1])

        opp = self.a
        if self.a == player:
            opp = self.b

        if move == UP:
            new = (new[0], new[1] - 1)
        elif move == DOWN:
            new = (new[0], new[1] + 1)
        elif move == LEFT:
            new = (new[0] - 1, new[1])
        elif move == RIGHT:
            new = (new[0] + 1, new[1])
        
        if new == opp.position:
            ms.out(ms.BATTLE, f'{player.name} can\'t move')
            return [f'{player.name} attempted to move {MOVE_NAMES[move]}, but was blocked by {opp.name}']
        
        player.position = new

        return [f'{player.name} moves {MOVE_NAMES[move]}']

    def plan_turn(self, socket: socket.socket, data):
        # possible plans

        '''
        {
            'response': [
                'spell / potion / pass / up / left / down / right'
            ]
        }
        '''

        prompt = None

        start = data['response'][0]

        player = self.players[socket]
        spell = player.get_spell(start)
        potion = player.get_potion(start)

        player.plan = Plan(time.time())

        if spell != None:
            direction = UP

            player.plan.type = ATTACK 
            player.plan.spell = spell
            player.plan.aim = direction

            if spell.spell.attack_type == RELATIVE:
                prompt = {
                    'text': ['Which direction would you like to cast the spell in?'],
                    'input': 'choice',
                    'choices': ['up', 'down', 'left', 'right']
                }
            elif spell.spell.attack_type == ROW:
                prompt = {
                    'text': ['Which row would you like to attack?'],
                    'input': 'choice',
                    'choices': ['1', '2', '3', '4', '5']
                }
            elif spell.spell.attack_type == COLUMN:
                prompt = {
                    'text': ['Which column would you like to attack?'],
                    'input': 'choice',
                    'choices': ['1', '2', '3', '4', '5']
                }
        elif potion != None:
            player.plan.potion = potion
            player.plan.type = POTION
            
        elif start == 'up':
            player.plan.move = UP
            player.plan.type = MOVEMENT

        elif start == 'left':
            player.plan.move = LEFT
            player.plan.type = MOVEMENT

        elif start == 'down':
            player.plan.move = DOWN
            player.plan.type = MOVEMENT

        elif start == 'right':
            player.plan.move = RIGHT
            player.plan.type = MOVEMENT
        
        return prompt

    def get_perspective(self, socket : socket.socket):
        if self.players[socket] == self.a:
            return A
        
        return B

    def get_message(self, perspective):
        if perspective is socket.socket:
            if perspective == self.a.player.client.socket:
                perspective = A
            else:
                perspective = B

        board = self.display_battle(perspective)

        messages = ['!CLEAR']
        messages.extend(board.split('\n'))

        messages.append('\n')

        choices = [
            'pass'
        ]

        options = {}

        player = self.a
        if perspective == B:
            player = self.b

        messages.append('Your options are :')
        # add spell options
        for spell in player.spells:
            message = '  '

            options['help ' + spell.spell.name.lower()] = spell.spell.display_spell().split('\n')

            if spell.cooldown == 0:
                choices.append(spell.spell.name.lower())
                message += spell.spell.display_name()
            else:
                message += f'{BOLD}{BLACK}{spell.spell.name} ({spell.cooldown} Turns){RESET}'
            
            messages.append(message)
        
        for potion in player.potions:
            message = '  '
            
            if potion.used:
                message += f'{BOLD + BLACK}{potion.potion.name} (Used){RESET}'
            else:
                choices.append(potion.potion.name.lower())
                message += f'{potion.potion.display_name()}'
            
            messages.append(message)
        
        
        mess = ''

        if player.position[0] != 0:
            choices.append('left')
            mess += 'left'

        if player.position[0] != 4:
            choices.append('right')
            if len(mess) > 0:
                mess += ', '
            mess += 'right'

        if player.position[1] != 0:
            choices.append('up')
            if len(mess) > 0:
                mess += ', '
            mess += 'up'
        
        if player.position[1] != 4:
            choices.append('down')
            if len(mess) > 0:
                mess += ', '
            mess += 'down'

        messages.append(mess + ', or pass')

        return json.dumps({
            'messages': messages,
            'prompts': [
                {
                    'input': 'choice',
                    'choices': choices,
                    'options': options
                }
            ]
        })
        
        
        
        
        