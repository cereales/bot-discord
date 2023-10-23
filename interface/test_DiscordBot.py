from utils import tools
import logging
logger = logging.getLogger(__name__)

import asyncio, time
import configparser
from interface.bot import DiscordBot
from test.archi import TestCase, DiscordBotForTest
from test.interaction import DiscordBotThreadForTest
from utils.exceptions import ExpectedError, UnexpectedError


class TestDiscordBot(TestCase):
    @TestCase.connected()
    @TestCase.interactive()
    def test_send_messages_interactive(self):
        """
        Send messages from console input.
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
                logger.debug("%s: %s", type(self.target_channel), self.target_channel)

                logger.info("Start interactive session... (ctrl+C to close.)")
                try:
                    while True:
                        message = input("> ")
                        if message != "":
                            await self.send(message)
                except KeyboardInterrupt:
                    await self.close()
        Bot().run()

class TestDiscordBotForTest(TestCase):
    """
    Test architecture for DiscordBotForTest class, and usage syntax.
    """
    @TestCase.connected()
    def test_bot_on_ready_failure(self):
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                raise Exception()   # catched in on_error but no close
                # raise KeyboardInterrupt() # close bot but asyncio never awaited
                # raise asyncio.exceptions.CancelledError() # not even printed
            async def on_error(self, event, *args, **kwargs):
                await super().on_error(event, *args, **kwargs)
                await self.close()  # close when catch an error
        bot = Bot()
        bot.run()

    @TestCase.connected()
    def test_bot_checks_error_on_close(self):
        """
        Check of errors is done at stop/close.
        """
        bot = DiscordBotThreadForTest(self)
        bot.error = True # simul an error
        with self.assertRaises(AssertionError):
            bot.stop()

    @TestCase.connected()
    def test_BotForTest_lifecycle(self):
        bot = DiscordBotThreadForTest(self)
        self.assertTrue(bot.is_ready())

        logger.log(tools.Constant.VERBOSE, "Start bot.")
        time.sleep(2)

        bot.stop()
        self.assertTrue(bot.is_closed())

    @TestCase.connected()
    def test_BotForTest_lifecycle_fail(self):
        class Bot(DiscordBotThreadForTest):
            def fail(self):
                raise Exception()
        bot = Bot(self)
        self.assertTrue(bot.is_ready())

        logger.log(tools.Constant.VERBOSE, "Start bot.")
        with self.assertRaises(Exception):
            bot.fail()      # bot cannot catch exceptions outside listen methods
        time.sleep(2)

        self.assertFalse(bot.is_closed())
        bot.stop()
        self.assertTrue(bot.is_closed())

    @TestCase.connected()
    def test_BotForTest_lifecycle_on_error(self):
        class Bot(DiscordBotThreadForTest):
            async def on_ready(self):
                await super().on_ready()
                self.fail()
            def fail(self):
                raise Exception()
        bot = Bot(self) # fails without exception
        self.assertTrue(bot.is_ready()) # Failed once: bot was ready and close at the same time.
        bot.assertError()

        self.assertTrue(bot.is_ready())
        logger.log(tools.Constant.VERBOSE, "Start bot.")
        time.sleep(2) # on_ready is called AFTER is_ready. So need to wait for the error to be processed.

        self.assertTrue(bot.is_closed())

    @TestCase.connected()
    def test_BotForTest_lifecycle_with(self):
        """
        `with` syntax for bot test.
        """
        with DiscordBotThreadForTest(self) as bot:
            self.assertTrue(bot.is_ready())

            logger.log(tools.Constant.VERBOSE, "Start bot.")
            time.sleep(2)

        self.assertTrue(bot.is_closed())

    @TestCase.connected()
    def test_BotForTest_lifecycle_with_fail(self):
        """
        Bot can close if any exception is raised in `with` loop
        """
        with self.assertRaises(ExpectedError):
            with DiscordBotThreadForTest(self) as bot:
                self.assertTrue(bot.is_ready())

                logger.log(tools.Constant.VERBOSE, "Start bot.")
                raise ExpectedError()
                logger.log(tools.Constant.VERBOSE, "not reached.")
                raise UnexpectedError() # never reached because of failure

        self.assertTrue(bot.is_closed())

    @TestCase.connected()
    def test_BotForTest_lifecycle_with_on_error(self):
        """
        Exceptions in listeners cannot be detected.
        But errors are checked at the close.
        """
        class Bot(DiscordBotThreadForTest):
            async def on_ready(self):
                await super().on_ready()
                self.fail()
            def fail(self):
                raise Exception()
            def stop(self):
                try:
                    super().stop()
                except:
                    logger.exception("Check error is done at __exit__. Traceback of catched exception")
                    raise ExpectedError()
        with self.assertRaises(ExpectedError):
            with Bot(self) as bot:
                logger.log(tools.Constant.VERBOSE, "Start bot.")
                time.sleep(2) # on_ready is called AFTER is_ready. So need to wait for the error to be processed.
                # reached even if on_ready raises
                self.assertFalse(bot.is_ready())
                self.assertTrue(bot.is_closed())
            raise UnexpectedError() # check of errors must be done while exitting with loop

        self.assertTrue(bot.is_closed())

class TestConfigInit(TestCase):
    def test_syntax(self):
        config = configparser.ConfigParser(default_section="DEFAULT", inline_comment_prefixes=('#'), allow_no_value=True, empty_lines_in_values=False)
        config.read("test/resources/config_syntax.ini")
        self.assertIn("TEST", config.sections())

        self.assertEqual(".", config.get("TEST", "test"))
        self.assertEqual("default1", config.get("TEST", "mand1"))
        self.assertEqual("default1", config.get("TEST", "mand1", fallback="Not Set"))
        self.assertEqual("Not Set", config.get("TEST", "tokn", fallback="Not Set"))
        with self.assertRaises(configparser.NoOptionError):
            logger.debug(config.get("TEST", "tokn"))
        self.assertEqual(None, config.get("TEST", "tokn", fallback=None))

        self.assertEqual("1", config["TEST"]["mand2"])
        self.assertEqual("1", config.get("TEST", "mand2"))
        self.assertNotEqual("1", config.getint("TEST", "mand2"))
        self.assertEqual(1, config.getint("TEST", "mand2"))

        sec = config["SECTION"]
        logger.debug(sec)
        for key in sec.items():
            logger.debug(key)
        self.assertEqual(2, len(sec.items()))
        sec = config["EMPTY"]
        logger.debug(sec)
        for key in sec.items():
            logger.debug(key)
        self.assertEqual(2, len(sec.items()))
        sec = config["ADMINS"]
        logger.debug(sec)
        for key in sec.items():
            logger.debug(key)
        self.assertEqual(3, len(sec.items()))
        self.assertEqual(3, len(sec))

        self.assertEqual(None, config.get("ADMINS", "001"))
        self.assertNotEqual("None", config.get("ADMINS", "001"))
        self.assertNotEqual(None, config.get("TEST", "001"))

    def test_complet(self):
        bot = DiscordBot("test/resources/config_complet.ini", "TEST")
        bot = DiscordBot("test/resources/config_complet.ini", "PROD")

    @TestCase.connected()
    def test_error_channel(self):
        """
        Send a message on error_channel.
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
                raise Exception()
        bot = Bot(config_section="error_channel")
        bot.run()
