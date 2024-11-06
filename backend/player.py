from constant import GAME_INIT, GAME_BATTLE, GAME_POTION, GAME_QUEUE, GAME_SPELL, GAME_START, GAME_TOKEN, GAME_VISUAL
from constant import BATTLE_CHOOSE, BATTLE_TARGET, BATTLE_WAIT

from constant import VISUALS

class Client:
    def __init__(self, socket, address) -> None:
        self.socket = socket
        self.address = address
        self.state = GAME_INIT
        
        self.spells = []
        self.potions = []

        self.won = 0
        self.tokens = 4
        self.health = 50
        
        self.choices = []

        self.name = 'Wizard'
        self.visual = VISUALS[0]
    