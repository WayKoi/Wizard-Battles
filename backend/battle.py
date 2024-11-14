from player import Player
import socket, json

from items import Spell

from constant import RED, GREEN, RESET, BOLD, BLACK
from constant import UP, LEFT, DOWN, RIGHT

A = 1
B = 2

class Plan:
    def __init__(self) -> None:
        self.spell = None
        self.potion = None
        self.aim = None
        self.move = None

class SWrap:
    def __init__(self, spell: Spell) -> None:
        self.spell = spell
        self.cooldown = 0

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
        self.potions = []
        self.status  = []

        self.plan: Plan = None
        
        self.position = (0, 0)
    
    def display_health(self):
        build = RED
        
        for i in range(self.player.health):
            if self.health == i:
                build += BOLD + BLACK
            
            build += '♥'
        
        return build + RESET

    def get_spell(self, name: str):
        name = name.lower()

        for spell in self.spells:
            if spell.name.lower() == name:
                return spell
            
        return None
    
    def get_potion(self, name: str):
        name = name.lower()

        for potion in self.potions:
            if potion.name.lower() == name:
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
    
    # just checks if that socket is part of this battle
    def part_of(self, socket: socket.socket) -> bool:
        if socket in self.sockets:
            return True
    
        return False
    
    def get(self, socket: socket.socket):
        return self.players[socket]
    
    def display_board(self, perspective):
        build = ''
        empty = '  •  '
        
        for y in range(5):
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

    def plan_turn(self, socket: socket.socket, data):
        # possible plans

        '''
        {
            'response': [
                'spell / potion / pass / up / left / down / right',
                'direction'
            ]
        }
        '''

        start = data['response'][0]

        player = self.players[socket]
        spell = player.get_spell(start)
        potion = player.get_potion(start)

        player.plan = Plan()

        if spell != None:
            direction = UP
            if len(data['response']) > 1:
                point = data['response'][1]
                
                if point == 'down':
                    direction = DOWN
                elif point == 'right':
                    direction = RIGHT
                elif point == 'left':
                    direction = LEFT

            player.plan.spell = spell
            player.plan.aim = direction

        elif potion != None:
            pass
        elif start == 'up':
            player.plan.move = UP

        elif start == 'left':
            player.plan.move = LEFT

        elif start == 'down':
            player.plan.move = DOWN

        elif start == 'right':
            player.plan.move = RIGHT

    def get_message(self, perspective):
        board = self.display_battle(perspective)

        messages = ['!CLEAR']
        messages.extend(board.split('\n'))

        messages.append('\n')

        choices = [
            'pass'
        ]

        player = self.a
        if perspective == B:
            player = self.b

        messages.append('Your options are :')
        # add spell options
        for spell in player.spells:
            message = '  '
            if spell.cooldown == 0:
                choices.append(spell.spell.name.lower())
                message += spell.spell.display_name()
            else:
                message += f'{BOLD}{BLACK}{spell.spell.name} ({spell.cooldown} Turns){RESET}'
            
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
                    'choices': choices
                }
            ]
        })
        
        
        
        
        