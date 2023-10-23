"""
This is the main executable.

Usage:
    python main.py CONTEXT

with CONTEXT the name of the section in resources/config.ini .
Several sections can be created in order not to overwrite values when you need to switch context.
"""
## Setup logger
from utils import tools
import logging
logger = logging.getLogger(__name__)

from interface.orchestration import Orchestrator


if __name__ == '__main__':
    CONTEXT = tools.read_input()
    bot = Orchestrator(tools.Constant.CONFIG_PATH, CONTEXT)
    # start Bot
    bot.run()       # Stop with ctrl+C
