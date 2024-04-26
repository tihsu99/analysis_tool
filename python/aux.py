import os
import sys
import re

# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class colors:
   colordict = {
                'RED'        : '\033[91m',
                'GREEN'      : '\033[92m',
                'BLUE'       : '\033[34m',
                'GRAY'       : '\033[90m',
                'WHITE'      : '\033[00m',
                'ORANGE'     : '\033[33m',
                'CYAN'       : '\033[36m',
                'PURPLE'     : '\033[35m',
                'LIGHTRED'   : '\033[91m',
                'PINK'       : '\033[95m',
                'YELLOW'     : '\033[93m',
                'BLINK'      : '\033[5m' ,
                'NORMAL'     : '\033[28m' ,
                "WARNING"    : '\033[33m',
                "CEND"       : '\033[0m',
                }
