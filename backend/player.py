from constant import GAME_INIT, GAME_BATTLE, GAME_POTION, GAME_QUEUE, GAME_SPELL, GAME_START, GAME_TOKEN, GAME_VISUAL
from constant import BATTLE_CHOOSE, BATTLE_TARGET, BATTLE_WAIT

from constant import VISUALS

class Client:
    def __init__(self, socket, address) -> None:
        self.socket = socket
        self.address = address
        self.name = None
    
    def rename(self, name: str):
        self.name = name
    
    def get_name(self):
        if self.name != None:
            return self.name

        return str(self.address)

class Player:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.state = GAME_INIT
        self.health = 6
        self.visual = VISUALS[0]
        
        self.spells  = []
        self.potions = []