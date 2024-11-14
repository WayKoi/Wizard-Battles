from constant import VISUALS

from constant import START_STATE

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
        self.state = START_STATE
        self.health = 6
        self.visual = VISUALS[0]
        
        self.spells  = []
        self.potions = []