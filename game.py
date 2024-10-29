from client import Client

class Game(Client):
    def process(message):
        print(message)
    
game = Game()
game.connect()