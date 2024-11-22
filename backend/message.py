import json
from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from constant import BOLD, DARK, BLINK, SWAP

from constant import VISUALS

SERVER = WHITE + BOLD + '[SERVER]' + RESET
CONNECTION = YELLOW + '[CONNECTION]' + RESET
MATCHMAKING = CYAN + DARK + '[MATCHMAKING]' + RESET
BATTLE = CYAN + '[BATTLE]' + RESET
CHOICE = MAGENTA + '[CHOICE]' + RESET
QUEUE = BLUE + BOLD + '[QUEUE]' + RESET
TOKEN = YELLOW + DARK + '[TOKEN]' + RESET

PING_PONG = DARK + GREEN + '[PING-PONG]' + RESET

DEBUG = RED + BLINK + '[DEBUG]' + RESET
ERROR = RED + BLINK + SWAP + '[ERROR]' + RESET

enable_debug = True

def out(messageType: str, content: str) -> str:
    if (messageType == DEBUG or messageType == PING_PONG) and not enable_debug:
        return
    
    print(messageType, content)

# client messages

VISUAL_PROMPT = []
VISUAL_CHOICES = []

count = 1
for visual in VISUALS:
    VISUAL_PROMPT.append(f'  {count}. {visual}')
    VISUAL_CHOICES.append(str(count))
    count += 1

VISUAL_PROMPT.insert(0, 'What would you like your wizard to look like?')
VISUAL_PROMPT.insert(0, '!CLEAR')

DISCONNECT_MESSAGE = '!DISCONNECT'
CLEAR_MESSAGE = '!CLEAR'
PING_MESSAGE = '!PING'
PONG_MESSAGE = '!PONG'

CONNECTED = json.dumps({
    'messages': [
        GREEN + 'Successfully Connected!' + RESET,
    ]
})

NAME_PROMPT = json.dumps({
    'prompts' : [
        {
            'text': [ 'What would you like to name your wizard?' ],
            'input': 'string'
        },
        {
            'text': VISUAL_PROMPT,
            'input': 'choice',
            'choices': VISUAL_CHOICES
        }
    ]
})

POTION_ARMOUR_MESSAGE = json.dumps({
    'messages': [ '!CLEAR' ],
    'prompts': [
        {
            'text': [
                'Would you like a potion or armour?'
            ],
            'input': 'choice',
            'choices': [ 'potion', 'armour' ]
        }
    ]
})

QUEUE_MESSAGE = json.dumps({
    'messages': [
        '!CLEAR',
        RED +          '        Entering the Battle Queue' + RESET,
        BLACK + BOLD + 'You will be matched up with an opponent soon' + RESET,
                CYAN + '                Waiting...' + RESET
    ]
})

COMM_MESSAGE = json.dumps({
    'messages': [
        '!CLEAR',
        YELLOW + 'Communicating...' + RESET
    ]
})