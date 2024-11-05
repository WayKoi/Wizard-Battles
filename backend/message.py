from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
from constant import BOLD, DARK, BLINK, SWAP

CONNECTION = YELLOW + '[CONNECTION]' + RESET
MATCHMAKING = CYAN + DARK + '[MATCHMAKING] + RESET'
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