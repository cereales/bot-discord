from utils import tools
import logging
logger = logging.getLogger(__name__)
logger_readiness = logging.getLogger("bot_readiness")
logger_thread = logging.getLogger("async_thread")
logger_readiness.setLevel(logging.WARNING)
logger_thread.setLevel(logging.WARNING)

import asyncio, threading
from utils.tools import Constant
from test.archi import TestCase, DiscordBotForTest
from mvc.ui import ConsoleUI


class DiscordBotThreadForTest(DiscordBotForTest):
    """
    Sub class of DiscordBot in order to run tests.
    Unlike DiscordBot, this class' `run` method is not blocking.

    @param  testcase    The testcase instance itself

    Usage:
    - with DiscordBotThreadForTest() as bot

    OR
    - init the bot instance.
    - Execute commands.
    - Do not forget to close the bot !
    """

    def __init__(self, testcase):
        super().__init__()
        assert isinstance(testcase, TestCase), "First parameter must be unittest instance."
        self.testcase = testcase
        self.error = False      # will be set to True is an exception is catched.
        self.terminate = False  # internal value for bot lifecycle; set to True to stop.
        self.run() # run is threaded, and waits for is_ready.

    # `with` operators

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        logger.log(Constant.VERBOSE, "Close by exitting `with`.")
        self.stop()     # `stop` waits for is_closed.

    # bot lifecycle

    def run(self):
        """
        Non blocking method to start bot.
        Return as soon as it is ready.
        """
        logger_thread.log(Constant.VERBOSE, "Starting bot on another thread.")
        threading.Thread(target=super().run, kwargs={"log_handler": None}, daemon=True).start() # start the thread
        asyncio.run(self.wait_is_ready())
        logger_thread.log(Constant.VERBOSE, "`run` completed.")

    async def start(self, token, *args, **kwargs):
        logger_thread.info("New thread.")
        logger_thread.log(Constant.VERBOSE, "Gathering `start` and detection.")
        await asyncio.gather(super().start(token, *args, **kwargs), self.wait_for_end())
        logger_thread.log(Constant.VERBOSE, "Out of gathering.")

    async def wait_is_ready(self):
        """
        Waiting the bot to be ready before running commands.
        """
        logger.log(Constant.VERBOSE, "Wait to be ready.")
        while not self.is_ready() and not self.is_closed(): # on on_ready error, bot can close in the same time is ready
            logger_readiness.log(Constant.VERBOSE, "ready: %s;\tclosed: %s", self.is_ready(), self.is_closed())
            await asyncio.sleep(.2)
        logger_readiness.log(Constant.VERBOSE, "ready: %s;\tclosed: %s", self.is_ready(), self.is_closed())
        logger.log(Constant.VERBOSE, "Is ready.")
        logger_readiness.log(Constant.VERBOSE, "ready: %s;\tclosed: %s", self.is_ready(), self.is_closed())

    async def wait_for_end(self):
        logger_thread.log(Constant.VERBOSE, "Start end detection.")
        while not self.terminate:
            logger_readiness.log(Constant.VERBOSE, "ready: %s,\tclosed: %s", self.is_ready(), self.is_closed())
            await asyncio.sleep(.5)
        logger_readiness.log(Constant.VERBOSE, "ready: %s,\tclosed: %s", self.is_ready(), self.is_closed())
        logger.debug("Detected stop instruction.")
        await super().close()
        logger_readiness.log(Constant.VERBOSE, "ready: %s,\tclosed: %s", self.is_ready(), self.is_closed())

    def stop(self):
        """
        Non async method to close.
        """
        asyncio.run(self.close())

    async def close(self):
        logger.log(Constant.VERBOSE, "Stop instruction.")
        self.terminate = True
        while not self.is_closed():
            await asyncio.sleep(.2)
        # possible to raise exceptions: TestCase can work
        self.testcase.assertFalse(self.error, "An exception occured in unit test.")

    # error management

    async def on_error(self, event, *args, **kwargs):
        # cannot raise any exception because it is catched by asyncio
        self.error = True
        await super().on_error(event, *args, **kwargs)

    def assertError(self):
        """
        Call this method after an error was expected.
        """
        self.testcase.assertTrue(self.error)
        logger.log(Constant.VERBOSE, "Failed as expected.")
        self.error = False      # reset errors, to succeed at close method.


class ConsoleUIForTest(ConsoleUI):
    """
    Sub class of ConsoleUI in order to run tests direclty with console.
    Bypass orchestrator.
    """
    def __init__(self):
        super().__init__()

    async def send(self, message):
        """
        Independantly read input to reconnect to on_message.
        """
        await super().send(message)
        if self.view.callback is not None: # ignore when no answer required.
            answer = input("> ")
            await self.view.on_message(answer)


class UIForTest(ConsoleUI):
    """
    Scheduled inputs from user, for test.
    """
    def __init__(self, answers):
        super().__init__()
        self.answers = answers

    async def send(self, message):
        """
        Independantly read input to reconnect to on_message.
        """
        if self.view.callback is not None: # ignore when no answer required.
            answer = self.answers.pop()
            await self.view.on_message(answer)
