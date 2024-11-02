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
        'range': 1,
        'description': 'Shoots a powerful Fireball at the opponent, dealing 9 - 21 damage',
        'crit-chance': 10,
        'cooldown': 1
    },
    {
        'name': 'bolt',
        'visual': YELLOW + 'Bolt' + RESET,
        'type': DAMAGING,
        'dice': { 'base': 2, 'd8': 3 },
        'range': 1,
        'description': 'Shoots a bolt of lightning at the opponent, dealing 5 - 26 damage',
        'crit-chance': 20,
        'cooldown': 2
    },
    {
        'name': 'void',
        'visual': MAGENTA + 'Void' + RESET,
        'type': DAMAGING,
        'dice': { 'base': 8, 'd10': 2 },
        'range': 0,
        'description': 'Wraps the opponent in void tendrils, dealing 10 - 28 damage',
        'crit-chance': 0,
        'cooldown': 2
    },
    {
        'name': 'tsunami',
        'visual': BLUE + "Tsunami" + RESET,
        'type': DAMAGING,
        'dice': { 'base': 12, 'd6': 4 },
        'range': 2,
        'description': 'Hits the opponent with a massive wave of water dealing 16 - 36 damage',
        'crit-chance': 25,
        'cooldown': 4
    },
    {
        'name': 'tornado',
        'visual': "Tornado",
        'type': DAMAGING,
        'dice': { 'base': 15, 'd4': 3 },
        'range': 2,
        'description': 'Hits opponent',
        'crit-chance': 5,
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

potions = [
    {
        'name': 'health',
        'visual': RED + 'Health Potion' + RESET,
        'effect': HEALING,
        'dice': { 'base': 5, 'd6': 2 },
        'description': 'Heals 7 - 17 health',
        'length': 0
    },
    {
        'name': 'ghealth',
        'visual': RED + 'Greater Health Potion' + RESET,
        'effect': HEALING,
        'dice': { 'base': 10, 'd6': 3 },
        'description': 'Heals 13 - 28 health',
        'length': 0
    },
    # {
    #     'name': 'strength',
    #     'visual': MAGENTA + 'Strength Potion' + RESET,
    #     'effect': BUFF,
    #     'dice': { 'base': 5, 'd4': 3 },
    #     'description': 'Adds 8 - 17 additional damage to spells for 3 turns',
    #     'length': 3
    # }
]

def GetPotion():
    chosen = random.randint(0, len(potions) - 1)
    return copy.deepcopy(potions[chosen])
        


    