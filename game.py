from client import Client, CLEAR_MESSAGE, clear_console
import json, time

BLACK   = '\u001b[30m'
RED     = '\u001b[31m'
GREEN   = '\u001b[32m'
YELLOW  = '\u001b[33m'
BLUE    = '\u001b[34m'
MAGENTA = '\u001b[35m'
CYAN    = '\u001b[36m'
WHITE   = '\u001b[37m'

BOLD        = '\033[1m'
DARK        = '\033[2m'
ITALIC      = '\033[3m'
UNDERLINE   = '\033[4m'
BLINK       = '\033[5m'
SWAP        = '\033[7m'
STRIKE      = '\033[9m'

RESET = '\u001b[0m'

class Game(Client):
    def __init__(self):
        super().__init__()
        self.frozen = False

    def process(self, message):
        data = json.loads(message)

        while self.frozen:
            time.sleep(0.5)
        
        print()
        if 'messages' in data:
            for message in data['messages']:
                self.interpret(message)

        if 'prompts' in data:
            response = []
            for prompt in data['prompts']:
                response.append(self.prompt(prompt))
            
            self.send(
                json.dumps({
                    'response': response
                })
            )
    
    def prompt(self, prompt):
        if not ('input' in prompt):
            return ''

        if 'text' in prompt:
            for text in prompt['text']:
                self.interpret(text)

        choice = ''
        if prompt['input'] == 'string':
            choice = input('> ')
            while choice == '':
                choice = input('> ')

        elif prompt['input'] == 'choice':
            choices = prompt['choices']
            for i in range(len(choices)):
                choices[i] = choices[i].lower()
            
            options = {} 
            if 'options' in prompt:
                options = prompt['options']

            choice = input('> ')
            while not(choice.lower() in choices):
                if choice.lower() in options:
                    for line in options[choice.lower()]:
                        self.interpret(line)

                else:
                    print('Choices are ', end = '')

                    for option in prompt['choices']:
                        print(f'"{option}" ', end = '')

                    for option in options:
                        print(f'"{option}" ', end='')

                    print()
                    
                choice = input('> ')
        
        return choice
    
    def interpret(self, message):
        if message == CLEAR_MESSAGE:
            clear_console()
        elif message == '!FREEZE':
            self.frozen = True
            input(BOLD + BLACK + 'press enter to continue' + RESET)
            self.frozen = False
        else:
            print(message)

game = Game()
clear_console()
game.connect()
game.send('{"response": ["here"]}')