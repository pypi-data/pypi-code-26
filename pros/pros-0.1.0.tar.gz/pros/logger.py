import logging


# https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLORS = {
    'DEBUG': BLUE,
    'INFO': GREEN,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': RED,
}


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % COLORS[levelname] + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


formatter = ColoredFormatter("%(levelname)s: %(message)s")
console = logging.StreamHandler()
logger = logging.Logger('cli', logging.INFO)

console.setFormatter(formatter)
logger.addHandler(console)
