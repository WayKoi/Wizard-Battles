from client import Client
import json
import os

clear = 'cls' if os.name == 'nt' else 'clear'

class Game(Client):
    def process(self, message):
        data = json.loads(message)

        '''
        {
            'messages': [
                'this is a message',
                'this is another'
            ],
            'input': <'string' or 'choice'>,
            'choices': [ '1', '2', '3' ]
        }
        '''
        
        print()
        for message in data['messages']:
            if message == '!CLEAR':
                os.system(clear)
            else:
                print(message)

        if not ('input' in data):
            return

        if data['input'] == 'string':
            string = ''
            
            while string == '':
                string = input('> ')
            
            self.send(string)
        elif data['input'] == 'choice':
            valid = False

            while not valid:
                string = input('> ')
                
                for choice in data['choices']:
                    if choice == string:
                        self.send(string)
                        valid = True
                
                if not valid:
                    print('That is not a valid option')

game = Game()
game.connect()
game.send('ready')