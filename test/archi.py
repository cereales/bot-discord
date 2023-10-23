from utils import tools
import logging
logger = logging.getLogger(__name__)

import unittest
import asyncio
import discord
from time import time
from utils.tools import Constant
from interface.bot import DiscordBot
from interface.orchestration import Orchestrator, DiscordOrchestrator


class TestCase(unittest.TestCase):
    # Decorators

    def connected():
        """
        Skip decorator for UnitTests.
        """
        return unittest.skipIf(Constant.NO_INTERNET, "Connected test.")

    def visual_test():
        """
        Skip decorator for UnitTests.
        """
        return unittest.skipIf(Constant.SKIP_VISUAL_TESTS, "Visual test required.")

    def interactive():
        """
        Skip decorator for UnitTests.
        """
        return unittest.skipUnless(Constant.PLAY_INTERACTIVE_TESTS, "interactive")

    def skip(*args, **kwargs):
        return unittest.skip(*args, **kwargs)

    # utils

    def assertIncertitude(self, value, theoric, incertitude=0.02):
        logger.debug("assert  %s in [%s - %s]", value, theoric - incertitude, theoric + incertitude)
        self.assertTrue(theoric - incertitude <= value and value <= theoric + incertitude)

    def assertTime(self, duration):
        return TimeChecker(self, duration)

class TimeChecker:
    """
    This class allows to check for global duration of several commands through the `with` syntax.
    """
    def __init__(self, testcase, duration):
        self.testcase = testcase
        self.duration = duration
        self.start = None

    def assertEquals(self, duration):
        self.testcase.assertIncertitude(time() - self.start, duration)

    # `with` operators

    def __enter__(self):
        self.start = time()
        return self

    def __exit__(self, type, value, traceback):
        logger.log(Constant.VERBOSE, "Exitting `with`.")
        self.assertEquals(self.duration)


class DiscordBotForTest(DiscordBot):
    """
    Sub class of DiscordBot for TEST context.
    """
    CONTEXT = ("test/resources/config.ini", "TEST")

    def __init__(self, config_path=None, config_section=None):
        super().__init__(
                config_path     if config_path is not None else DiscordBotForTest.CONTEXT[0],
                config_section  if config_section is not None else DiscordBotForTest.CONTEXT[1]
                )

    async def on_ready(self):
        await super().on_ready()
        await self.change_presence(activity=discord.Game("tests runnings..."))

    async def on_error(self, event, *args, **kwargs):
        await super().on_error(event, *args, **kwargs)
        logger.log(Constant.VERBOSE, "Error closing.")
        await self.close() # in order not to keep stucked in unit test


class DiscordOrchestratorForTest(DiscordOrchestrator):
    """
    Sub class of DiscordOrchestrator in order to run tests.
    Not linked to any Orchestrator. Not started.
    """
    def __init__(self):
        logger.log(Constant.VERBOSE, "__init__()")
        super().__init__(None, *DiscordBotForTest.CONTEXT)


class OrchestratorForTest(Orchestrator):
    """
    Sub class of Orchestrator in order to run tests.
    """
    def __init__(self, ctrlC=False):
        super().__init__(*DiscordBotForTest.CONTEXT)
        if ctrlC:
            self.add_listener_KeyboardInterrupt()

    def get_discord_bot(self):
        return self.listeners[0]

    def add_listener_KeyboardInterrupt(self):
        async def f():
            raise KeyboardInterrupt()
        res = ListenerForTest(self.get_discord_bot(), f)
        self.listeners.append(res)
        return res

    def add_listener_close(self):
        async def f():
            await self.get_discord_bot().close_all()
        res = ListenerForTest(self.get_discord_bot(), f)
        self.listeners.append(res)
        return res

class ListenerForTest:
    """
    Listener run function as soon as discord bot is ready.
    """
    def __init__(self, bot, function):
        self.bot = bot
        self.f = function

    async def start(self):
        """
        method call asynchronously with others listeners.
        """
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        await self.f()

    async def close(self):
        pass
