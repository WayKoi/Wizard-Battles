import random
import copy

BLACK = '\u001b[30m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
YELLOW = '\u001b[33m'
BLUE = '\u001b[34m'
MAGENTA = '\u001b[35m'
CYAN = '\u001b[36m'
WHITE = '\u001b[37m'
RESET = '\u001b[0m'

DAMAGING = 1
HEALING = 2
BUFF = 3

spells = [
    {
        'name': 'fireball',
        'visual': RED + 'Fireball' + RESET,
        'type': DAMAGING,
        'dice': { 'base': 5, 'd4': 4 },
        'description': 'Shoots a powerful Fireball at the opponent, dealing 9 - 21 damage',
        'crit-chance': 10,
        'cooldown': 1
    },
    {
        'name': 'bolt',
        'visual': YELLOW + 'Bolt' + RESET,
        'type': DAMAGING,
        'dice': { 'base': 2, 'd8': 3 },
        'description': 'Shoots a bolt of lightning at the opponent, dealing 5 - 26 damage',
        'crit-chance': 20,
        'cooldown': 2
    },
    {
        'name': 'void',
        'visual': MAGENTA + 'Void' + RESET,
        'type': DAMAGING,
        'dice': { 'base': 8, 'delay': { 'd10': 2 } },
        'description': 'Wraps the opponent in void tendrils, dealing 8 damage up front and 2 - 20 damage the following turn',
        'crit-chance': 0,
        'cooldown': 2
    },
    {
        'name': 'tsunami',
        'visual': BLUE + "Tsunami" + RESET,
        'type': DAMAGING,
        'dice': { 'base': 12, 'd6': 4 },
        'description': 'Hits the opponent with a massive wave of water dealing 16 - 36 damage',
        'crit-chance': 25,
        'cooldown': 4
    }
]

def GetSpells(amount):
    amount = min(amount, len(spells))
    chosen = []

    for i in range(amount):
        found = True
        while found:
            found = False

            choice = random.randint(0, len(spells) - 1)
            for spell in chosen:
                if spell['name'] == spells[choice]['name']:
                    found = True
                    break
            
            if not found:
                chosen.append(copy.deepcopy(spells[choice]))
    
    return chosen
        


    