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

# Game states

GAME_INIT = 0
GAME_VISUAL = -1
GAME_START = 1

GAME_TOKEN = 2
GAME_SPELL = 3
GAME_POTION = 4

GAME_QUEUE = 5
GAME_BATTLE = 6

BATTLE_CHOOSE = 7
BATTLE_TARGET = 8
BATTLE_WAIT = 9

TOKEN_SPELL = 1
TOKEN_ARMOUR = 2
TOKEN_POTION = 3

# positions

LEFT = 0
MIDDLE = 1
RIGHT = 2

POS_NAMES = [
    'left',
    'middle',
    'right'
]

# spell / potion types

DAMAGING = 1
HEALING = 2
BUFF = 3

# Visuals

VISUALS = [
    '(O_O)',
    '(^_^)',
    '(+_+)',
    '(>.<)',
    '(^_-)',
    '(o-o)',
    '(OwO)',
    '(UwU)'
]