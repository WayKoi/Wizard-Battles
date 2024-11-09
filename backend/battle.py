from player import Player
import socket

from constant import RED, GREEN, RESET, BOLD, BLACK

A = 1
B = 2

class PWrap:
    def __init__(self, player: Player, name: str):
        self.player = player
        self.name = name
        self.visual = player.visual
        
        self.health = player.health
        
        self.spells  = []
        self.potions = []
        self.status  = []
        
        self.position = (0, 0)
    
    def display_health(self):
        build = RED
        
        for i in range(self.player.health):
            if self.health == i:
                build += BOLD + BLACK
            
            build += '♥'
        
        return build + RESET

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
        
        
        
        