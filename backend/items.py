import random, json

from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from constant import DARK, BOLD
from constant import DAMAGING, HEALING, BUFF

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
    
    def display_pattern(self):
        build = TYPE_NAMES[self.attack_type] +'\n'
        
        spots = self.get_spots()

        for y in range(5):
            for x in range(5):
                if (x, y) in spots:
                    build += self.colour + ' ■ ' + RESET
                elif (x, y) == (2, 2) and self.attack_type <= 1:
                    build += GREEN + ' ☺ ' + RESET
                else:
                    build += ' • '
            
            build += RESET + '\n'
        
        return build
    
    def get_spots(self, position = (2, 2), direction = UP) -> list[(int, int)]:
        spots = []
        
        if self.attack_type == RELATIVE or self.attack_type == RELATIVE_SYMMETRIC:
            pattern = self.pattern
            
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
    
    def display_spell(self):
        pattern = self.display_pattern().split('\n')
        
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
        'Inferno',
        RED,
        '',
        'Causes',
        2,
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
        2,
        2
    ),
    Spell(
        'Tidal Wave',
        BLUE,
        '',
        'Summons a',
        2,
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
        1,
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
        3,
        STATIC,
        [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)
        ],
        6,
        3
    ),
    Spell(
        'Earthquake',
        DARK + YELLOW,
        '',
        'Forces an',
        3,
        RELATIVE,
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
    return random.choices(found, k = amount)
    
def create_message(spell_tier):
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

    spells = get_tier(spell_tier)

    for spell in spells:
        start['messages'].append(spell.display_spell())
        start['prompts'][0]['choices'].append(spell.name.lower())

    return json.dumps(start)

def get_spell(name):
    for spell in spells:
        if name.lower() == spell.name.lower():
            return spell
    
    return None

if __name__ == '__main__':
    for spell in spells:
        print(spell.display_spell())

    