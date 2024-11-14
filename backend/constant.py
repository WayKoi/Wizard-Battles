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

'''
Ask for name and visual
Ask for T1 spell
Ask for T2 spell
Ask for T3 spell or Ability
Ask for Potion or Armour
Ask for Potion or Armour
'''

START_STATE = -1
INIT_NAME = 0
BUILD_T1 = 1
BUILD_T2 = 2
BUILD_T3 = 3
BUILD_PA = 4 # potion or armour

BATTLE_QUEUE = 5
BATTLE_CHOOSE = 6
BATTLE_WAIT = 7


# positions

UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3

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