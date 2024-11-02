
BLACK = '\u001b[30m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
YELLOW = '\u001b[33m'
BLUE = '\u001b[34m'
MAGENTA = '\u001b[35m'
CYAN = '\u001b[36m'
WHITE = '\u001b[37m'
RESET = '\u001b[0m'

CONNECTION = YELLOW + '[CONNECTION]' + RESET
BATTLE = CYAN + '[BATTLE]' + RESET
CHOICE = MAGENTA + '[CHOICE]' + RESET
QUEUE = BLUE + '[QUEUE]' + RESET
DEBUG = RED + '[DEBUG]' + RESET
TOKEN = GREEN + '[TOKEN]' + RESET

debug = True

def out(messageType: str, content: str) -> str:
    print(messageType + content)