import json
from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from constant import BOLD, DARK, BLINK, SWAP

SERVER = WHITE + BOLD + '[SERVER]' + RESET
CONNECTION = YELLOW + '[CONNECTION]' + RESET
MATCHMAKING = CYAN + DARK + '[MATCHMAKING]' + RESET
BATTLE = CYAN + '[BATTLE]' + RESET
CHOICE = MAGENTA + '[CHOICE]' + RESET
QUEUE = BLUE + BOLD + '[QUEUE]' + RESET
TOKEN = YELLOW + DARK + '[TOKEN]' + RESET

DEBUG = RED + BLINK + '[DEBUG]' + RESET
ERROR = RED + BLINK + SWAP + '[ERROR]' + RESET

debug = True

def out(messageType: str, content: str) -> str:
    if messageType == DEBUG and not debug:
        return
    
    print(messageType + content)

# client messages

DISCONNECT_MESSAGE = '!DISCONNECT'
CLEAR_MESSAGE = '!CLEAR'
PING_MESSAGE = '!PING'
PONG_MESSAGE = '!PONG'

NAME_PROMPT = json.dumps({
    'messages': [
        GREEN + 'Successfully Connected!' + RESET,
        'What would you like to name your wizard?'
    ],
    'input': 'string'
})

QUEUE_MESSAGE = json.dumps({
    'messages': [
        CYAN + '      You have used all your tokens' + RESET,
        RED +  '        Entering the Battle Queue' + RESET,
               'You will be matched up with an opponent soon'
    ]
})

COMM_MESSAGE = json.dumps({
    'messages': [
        YELLOW + 'Communicating...' + RESET
    ]
})