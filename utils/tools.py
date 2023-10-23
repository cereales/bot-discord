"""
This module centralise all utils methods, as for example logging settings.
To take benefit from this, all other modules must first import this one :

`from utils import tools`
"""
import logging
class Constant:
    """
    All CONSTANTS must be declared here.
    """
    CONFIG_PATH = "resources/config.ini"
    NO_INTERNET = False         # Set to True when internet connection is unavailable.
    PENDU_DATABASE_FILE = "game/pendu/database.txt"
    PENDU_NB_MAX_ERRORS = 11
    PLAY_INTERACTIVE_TESTS = False
    SKIP_VISUAL_TESTS = True
    VERBOSE = 5
    VISUAL_WARN_VERBOSE = logging.DEBUG + 1


## Logging setup
logging.basicConfig(level=Constant.VERBOSE, format="[%(asctime)s.%(msecs)03d] [ %(levelname)s\t] %(thread)d | %(process)d  | %(name)s:%(lineno)d:\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S") # NOTE: '\t' character is of lenght > 0
logging.addLevelName(Constant.VERBOSE, "VERBOSE") # level must be > 0
logging.addLevelName(Constant.VISUAL_WARN_VERBOSE, "   /!\\")
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

import sys          # console inputs


def read_input():
    """
    Return context value from input argument.
    Exit program if no given context.
    """
    if len(sys.argv) < 2:
        print("You should provide a context keyword.")
        print("Usage:\t{} context".format(sys.argv[0]))
        exit(1)
    return sys.argv[1]
