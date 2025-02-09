import random, json

from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from constant import DARK, BOLD
from constant import DAMAGING, HEALING, BUFF

import os

clear = 'cls' if os.name == 'nt' else 'clear'

# attack types

RELATIVE = 0
RELATIVE_SYMMETRIC = 1 # its the same regardless of direction
ROW = 2
COLUMN = 3
STATIC = 4

TYPE_NAMES = [
    BOLD + BLUE + "    Relative" + RESET,
    BOLD + BLUE + "    Relative" + RESET,
    RED + "   Full  Row" + RESET,
    YELLOW + "  Full Column" + RESET,
    BOLD + GREEN + "     Static" + RESET
]

from constant import UP, DOWN, LEFT, RIGHT

class Spell:
    def __init__(self, name: str, colour: str, extra: str, cast: str, damage: int, attack_type: int, pattern: list[(int, int)], cooldown: int, tier: int):
        self.name = name
        self.colour = colour
        self.extra = extra
        # this is the middle section of the print of them casting the spell
        self.cast = cast
        
        self.damage = damage
        self.attack_type = attack_type
        self.pattern = pattern
        
        self.cooldown = cooldown
        # this organizes the spells into classes
        self.tier = tier
    
    def display_pattern(self, position = (2, 2), direction = UP):
        build = TYPE_NAMES[self.attack_type] +'\n'
        
        spots = self.get_spots(position, direction)

        for y in range(5):
            for x in range(5):
                if (x, y) in spots:
                    build += self.colour + ' ■ ' + RESET
                elif (x, y) == position and self.attack_type <= 1:
                    build += GREEN + ' ☺ ' + RESET
                else:
                    build += ' • '
            
            build += RESET + '\n'
        
        return build
    
    def get_spots(self, position = (2, 2), direction = UP) -> list[(int, int)]:
        spots = []
        
        if self.attack_type == RELATIVE or self.attack_type == RELATIVE_SYMMETRIC:
            pattern = self.pattern.copy()
            
            # up    = 0
            # left  = 1
            # down  = 2
            # right = 3
            
            if direction % 2 == 1:
                # left or right
                for i in range(len(pattern)):
                    pattern[i] = (pattern[i][1], pattern[i][0])
            
            if direction > 1:
                for i in range(len(pattern)):
                    pattern[i] = (-pattern[i][0], -pattern[i][1])
            
            for spot in pattern:
                add = (spot[0] + position[0], spot[1] + position[1])
                spots.append(add)

        elif self.attack_type == ROW:
            for i in range(5):
                spots.append((i, position[1]))
                
        elif self.attack_type == COLUMN:
            for i in range(5):
                spots.append((position[0], i))
                
        elif self.attack_type == STATIC:
            for spot in self.pattern:
                spots.append(spot)

        return spots
    
    def display_name(self):
        return f'{self.colour}{self.name}{RESET}'
    
    def get_cast_print(self, wizard_name):
        return f'{wizard_name} {self.cast} {self.display_name()}'
    
    def display_damage(self):
        return RED + ('♥' * self.damage) + RESET
    
    def display_spell(self, position = (2, 2), direction = UP):
        pattern = self.display_pattern(position, direction).split('\n')
        
        pattern[1] += f' {self.display_name()}'
        pattern[2] += f' {BOLD + BLACK}Tier {self.tier}{RESET}'
        pattern[3] += f' {BOLD + BLACK}Damage   : {self.display_damage()}'
        pattern[4] += f' {BOLD + BLACK}Cooldown : {self.cooldown} Turns{RESET}'
        pattern[5] += f' {self.extra}'
        
        return '\n'.join(pattern)


spells = [
    Spell(
        'Fireball',
        RED,
        '',
        'Shoots a',
        1,
        RELATIVE,
        [(0, -1), (0, -2)],
        1,
        1
    ),
    Spell(
        'Bolt',
        YELLOW,
        '',
        'Shoots a',
        1,
        RELATIVE,
        [(-1, -1), (1, -1), (-2, -2), (2, -2)],
        1,
        1
    ),
    Spell(
        'Wave',
        BLUE,
        '',
        'Causes a',
        1,
        RELATIVE,
        [(-1, -1), (0, -1), (1, -1)],
        1,
        1
    ),
    Spell(
        'Mud Bomb',
        DARK + YELLOW,
        '',
        'Throws a',
        1,
        RELATIVE_SYMMETRIC,
        [(0, 1), (1, 0), (-1, 0), (0, -1)],
        1,
        1
    ),
    Spell(
        'Icicles',
        WHITE,
        '',
        'Shoots out',
        1,
        RELATIVE_SYMMETRIC,
        [(1, 1), (-1, 1), (1, -1), (-1, -1)],
        1,
        1
    ),
    
    Spell(
        'Inferno',
        RED,
        '',
        'Causes',
        3,
        RELATIVE_SYMMETRIC,
        [(0, 1), (0, 2), (0, -1), (0, -2), (1, 0), (2, 0), (-1, 0), (-2, 0)],
        2,
        2
    ),
    Spell(
        'Lightning',
        YELLOW,
        '',
        'Calls Upon',
        2,
        COLUMN,
        [],
        4,
        2
    ),
    Spell(
        'Tidal Wave',
        BLUE,
        '',
        'Summons a',
        3,
        RELATIVE,
        [(-1, -1), (0, -1), (1, -1), (-1, -2), (0, -2), (1, -2)],
        2,
        2
    ),
    Spell(
        'Tremors',
        DARK + YELLOW,
        '',
        'Causes',
        2,
        RELATIVE_SYMMETRIC,
        [(0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, -2), (0, 2), (-2, 0), (2, 0)],
        3,
        2
    ),
    Spell(
        'Flakes',
        WHITE,
        '',
        'Makes it Snow',
        3,
        RELATIVE_SYMMETRIC,
        [
            (1, 1), (-1, 1), (1, -1), (-1, -1),
            (-2, 0), (0, -2), (2, 0), (0, 2),
            (-2, -2), (2, -2), (-2, 2), (2, 2)
        ],
        3,
        2
    ),
    Spell(
        'Geyser',
        CYAN,
        '',
        'Erupts a',
        3,
        RELATIVE_SYMMETRIC,
        [
            (2, 0), (2, -1), (2, 1),
            (-2, 0), (-2, -1), (-2, 1),
            (0, 2), (1, 2), (-1, 2),
            (0, -2), (1, -2), (-1, -2)
        ],
        3,
        2
    ),

    Spell(
        'Hellfire',
        RED,
        '',
        'Summons a',
        2,
        ROW,
        [],
        3,
        3
    ),
    Spell(
        'Static',
        YELLOW,
        '',
        'Creates',
        2,
        STATIC,
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (2, 0), (3, 0), (4, 0),
            (4, 1), (4, 2), (4, 3), (4, 4),
            (1, 4), (2, 4), (3, 4)
        ],
        1,
        3
    ),
    Spell(
        'Tsunami',
        BLUE,
        '',
        'Calls a',
        5,
        STATIC,
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
        ],
        7,
        3
    ),
    Spell(
        'Earthquake',
        DARK + YELLOW,
        '',
        'Forces an',
        3,
        RELATIVE_SYMMETRIC,
        [
            (0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), 
            (-1, 1), (1, -1), (-1, -1), (0, -2), (0, 2), 
            (-2, 0), (2, 0), (2, -1), (2, 1),
            (-2, 1), (-2, -1),
            (-1, 2), (1, 2),
            (-1, -2), (1, -2)
        ],
        5,
        3
    ),
    Spell(
        'Growth V',
        GREEN,
        '',
        'Causes rapid',
        4,
        STATIC,
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
        ],
        6,
        3
    ),
    Spell(
        'Growth H',
        GREEN,
        '',
        'Causes rapid',
        4,
        STATIC,
        [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)
        ],
        6,
        3
    ),
    Spell(
        'Blizzard',
        WHITE,
        '',
        'Summons a',
        4,
        RELATIVE_SYMMETRIC,
        [
            (0, 1), (1, 0), (-1, 0), (0, -1), 
            (1, 1), (-1, 1), (1, -1), (-1, -1), 
            (0, -2), (0, 2), (-2, 0), (2, 0),
            (2, 2), (-2, 2), (2, -2), (-2, -2)
        ],
        6,
        3
    ),
    Spell(
        'Hurricane',
        CYAN,
        'Starts with a cooldown of 4 turns',
        'Calls forth a',
        6,
        RELATIVE_SYMMETRIC,
        [
            (0, -1), (0, 1),
            (-1, -2), (1, 2),
            (-2, -1), (2, 1),
            (-2, 0), (2, 0),
            (-2, 1), (2, -1)
        ],
        10,
        3
    )

]

def get_tier(tier):
    found = []
    
    for spell in spells:
        if spell.tier == tier:
            found.append(spell)
    
    return found

def get_tier_amount(tier, amount):
    found = get_tier(tier)
    random.shuffle(found)
    return found[0:min(amount, len(found))]
    
def create_message(spell_tier, amount = 100):
    start = {
        'messages': [
            '!CLEAR',
            'Which spell would you like?'
        ],
        'prompts': [
            {
                'input': 'choice',
                'choices': []
            }
        ]
    }

    spells = get_tier_amount(spell_tier, amount)

    for spell in spells:
        start['messages'].append(spell.display_spell())
        start['prompts'][0]['choices'].append(spell.name.lower())

    return json.dumps(start)

def get_spell(name):
    for spell in spells:
        if name.lower() == spell.name.lower():
            return spell
    
    return None

class Potion:
    def __init__(self, name, colour, heal):
        self.name: str = name
        self.colour: str = colour
        
        self.heal: int = heal
    
    def display_name(self):
        return self.colour + self.name + RESET


potions: list[Potion] = [
    Potion(
        'Healing Potion',
        RED,
        3
    ),
    Potion(
        'Greater Healing Potion',
        RED,
        5
    )
]

def get_potion() -> Potion:
    return random.choice(potions)

if __name__ == '__main__':
    for spell in spells:
        print(spell.display_spell())
    
    input('Press enter to see potions')
    os.system(clear)

    for potion in potions:
        print(potion.display_name())

    