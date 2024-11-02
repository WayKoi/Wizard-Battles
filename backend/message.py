from constant import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

CONNECTION = YELLOW + '[CONNECTION]' + RESET
BATTLE = CYAN + '[BATTLE]' + RESET
CHOICE = MAGENTA + '[CHOICE]' + RESET
QUEUE = BLUE + '[QUEUE]' + RESET
DEBUG = RED + '[DEBUG]' + RESET
TOKEN = GREEN + '[TOKEN]' + RESET

debug = True

def out(messageType: str, content: str) -> str:
    print(messageType + content)