import random
import copy

from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from constant import DARK, BOLD
from constant import DAMAGING, HEALING, BUFF

class Dice:
    def __init__(self, base, d4 = 0, d6 = 0, d8 = 0, d10 = 0) -> None:
        self.base = base
        self.d4 = d4
        self.d6 = d6
        self.d8 = d8
        self.d10 = d10
    
    def roll(self) -> int:
        amount = self.base

        for i in range(self.d4):
            amount += random.randint(1, 4)
        
        for i in range(self.d6):
            amount += random.randint(1, 6)
        
        for i in range(self.d8):
            amount += random.randint(1, 8)
        
        for i in range(self.d10):
            amount += random.randint(1, 10)
        
        return amount

class Spell:
    def __init__(self, name, visual, type, dice: Dice, range, desc, crit, cooldown) -> None:
        self.name: str   = name
        self.visual: str = visual
        self.type: int   = type
        self.dice: Dice  = dice,
        self.range: int  = range
        self.desc: str   = desc
        self.crit: int   = crit
        self.cooldown: int = cooldown

    def roll(self) -> int:
        return self.dice.roll()

class Potion:
    pass

spells = [
    Spell(
        'fireball',
        RED + 'Fireball' + RESET,
        DAMAGING,
        Dice(5, d4 = 4),
        1,
        'Shoots a powerful Fireball at the opponent, dealing 9 - 21 damage',
        10,
        1
    ),
    Spell(
        'bolt',
        YELLOW + 'Bolt' + RESET,
        DAMAGING,
        Dice(2, d8 = 3),
        1,
        'Shoots a bolt of lightning at the opponent, dealing 5 - 26 damage',
        20,
        2
    ),
    Spell(
        'void',
        MAGENTA + DARK + 'Void' + RESET,
        DAMAGING,
        Dice(8, d10 = 2),
        0,
        'Wraps the opponent in void tendrils, dealing 10 - 28 damage',
        0,
        2
    ),
    Spell(
        'tsunami',
        BLUE + 'Tsunami' + RESET,
        DAMAGING,
        Dice(12, d6 = 3),
        2,
        'Hits the opponent with a massive wave of water dealing 16 - 30 damage',
        25,
        4
    )
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
        


    