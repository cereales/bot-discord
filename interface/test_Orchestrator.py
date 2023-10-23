from utils import tools
import logging
logger = logging.getLogger(__name__)

import asyncio, time
from test.archi import TestCase, DiscordBotForTest, OrchestratorForTest


class TestAsyncBotLifecycle(TestCase):
    def test_interactive(self):
        """
        Need to run interactive tests.
        """
        self.assertTrue(tools.Constant.PLAY_INTERACTIVE_TESTS, "Need to run interactive tests.")

    @TestCase.interactive()
    def test_classic_bot_run(self):
        """
        Ctrl+C is catched by bot.run
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
                logger.warning("Ctrl+C required.")
        bot = Bot()
        bot.run()
        logger.debug("Reached.")
        self.assertTrue(bot.is_closed())

    @TestCase.interactive()
    def test_classic_bot_start(self):
        """
        Ctrl+C is catched by asyncio.run, need to be catched.
        CancelledError is generated for bot.start
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
                logger.warning("Ctrl+C required.")
        async def async1():
            try:
                await bot.start()
            except asyncio.exceptions.CancelledError as e:
                logger.exception("bot catched: %s", type(e))
                await bot.close()
        bot = Bot()
        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(async1())
        logger.debug("Reached.")
        self.assertTrue(bot.is_closed())

    @TestCase.interactive()
    def test_dual_bot_start(self):
        """
        Ctrl+C is catched by asyncio.run, need to be catched.
        CancelledError is generated for bot.start
        CancelledError is generated for asyncio.gather
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
                logger.warning("Ctrl+C required.")
        async def async1():
            try:
                await asyncio.sleep(10)
                logger.warning("Too late.")
            except BaseException as e:
                logger.exception("Sleep catched: %s", type(e))
        async def async2():
            try:
                await bot.start()
            except BaseException as e:
                logger.exception("bot catched: %s", type(e))
                await bot.close()
        async def gather():
            try:
                await asyncio.gather(async1(), async2())
            except BaseException as e:
                logger.exception("Gather catched: %s", type(e))
        bot = Bot()
        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(gather())
        logger.debug("Reached.")
        self.assertTrue(bot.is_closed())

    def test_dual_bot_start_auto(self):
        """
        Ctrl+C is catched by asyncio.run, need to be catched.
        CancelledError is generated for bot.start
        KeyboardInterrupt is forwarded to asyncio.gather !!
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
        async def async1():
            while not bot.is_ready():
                await asyncio.sleep(1)
            raise KeyboardInterrupt()
        async def async2():
            try:
                await bot.start()
            except BaseException as e:
                logger.exception("bot catched: %s", type(e))
                await bot.close()
        async def gather():
            try:
                await asyncio.gather(async1(), async2())
            except BaseException as e:
                logger.exception("Gather catched: %s", type(e))
        bot = Bot()
        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(gather())
        logger.debug("Reached.")
        self.assertTrue(bot.is_closed())

    def test_bot_self_close(self):
        """
        Bot is well closed by calling close()
        """
        class Bot(DiscordBotForTest):
            async def on_ready(self):
                await super().on_ready()
                await self.close()
        bot = Bot()
        bot.run()
        logger.debug("Reached.")
        self.assertTrue(bot.is_closed())

class TestOrchestratorClose(TestCase):
    @TestCase.interactive()
    def test_orchestrator_interact(self):
        orch = OrchestratorForTest()
        logger.warning("Ctrl+C required.")
        orch.run()
        bot = orch.get_discord_bot()
        self.assertTrue(bot.is_closed())

    def test_orchestrator_KeyboardInterrupt(self):
        orch = OrchestratorForTest()
        bot = orch.get_discord_bot()
        orch.add_listener_KeyboardInterrupt()
        orch.run()
        self.assertTrue(bot.is_closed())

    def test_orchestrator_close_command(self):
        orch = OrchestratorForTest()
        bot = orch.get_discord_bot()
        orch.add_listener_close()
        orch.run()
        self.assertTrue(bot.is_closed())

    @TestCase.interactive()
    def test_input_interrupt(self):
        """
        input() is not interrupted by exception.
        needs one input to release process.
        """
        async def async1(interactive):
            logger.debug("in")
            try:
                while True:
                    await asyncio.sleep(1)
                    if interactive:
                        logger.warning("Ctrl+C required.")
                    a = input(">")
                    logger.debug("Get: %s", a)
            except:
                logger.debug("out")
                raise
        async def async2():
            try:
                while True:
                    logger.debug("listening.")
                    await asyncio.sleep(0.5)
            except asyncio.exceptions.CancelledError:
                logger.error("out")
        async def async3():
            await asyncio.sleep(3)
            raise KeyboardInterrupt()
        async def gather(interactive=False):
            try:
                if interactive:
                    await asyncio.gather(async1(True), async2())
                else:
                    await asyncio.gather(async1(False), async3())
            except:
                logger.exception("catched")
                await asyncio.sleep(1)

        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(gather(interactive=True))

        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(gather(interactive=False))

class TestAsyncThreadLifecycle(TestCase):
    @TestCase.interactive()
    def test_interrupt_asyncio(self):
        """
        Ctrl+C is forwarded by asyncio.
        """
        async def async1():
            logger.warning("Ctrl+C required.")
            while True:
                await asyncio.sleep(3)
        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(async1())

    @TestCase.interactive()
    def test_interrupt_asyncio_try_catch(self):
        """
        asyncio catches the KeyboardInterrupt and raises from the run (?)
        """
        async def async1():
            logger.warning("Ctrl+C required.")
            try:
                while True:
                    await asyncio.sleep(3)
            except:
                pass
            logger.debug("Reached.")
        with self.assertRaises(KeyboardInterrupt):
            asyncio.run(async1())
        # asyncio catches the KeyboardInterrupt and raises from the run (?)

    @TestCase.interactive()
    def test_interrupt(self):
        """
        KeyboardInterrupt is not raised by using time.sleep
        See test above.
        """
        async def async1():
            logger.warning("Ctrl+C required.")
            try:
                while True:
                    time.sleep(3)
            except:
                pass
        asyncio.run(async1())

    def test_try_catch(self):
        """
        Correctly catch raised exception outside asyncio.sleep.
        """
        async def async1():
            try:
                await asyncio.sleep(1)
                raise KeyboardInterrupt()
            except:
                pass
        asyncio.run(async1())

    def test_gather_duration(self):
        """
        gather waits for all subprocess.
        """
        async def async1():
            await asyncio.sleep(3)
        async def async2():
            await asyncio.sleep(1)
        async def gather():
            await asyncio.gather(async1(), async2())
        with self.assertTime(3):
            asyncio.run(gather())

    def test_logger_exception(self):
        """
        logger.exception does not raise.
        """
        async def main():
            try:
                raise Exception()
            except:
                logger.exception("catched")
        async def gather():
            await asyncio.gather(main())
        asyncio.run(main())
        asyncio.run(gather())

    def test_gather_interrupt_KeyboardInterrupt(self):
        """
        raised KeyboardInterrupt is catched by asyncio.gather
        and forwarded by all asyncio methods
        - asyncio.exceptions.CancelledError     in sleep of async1
        - KeyboardInterrupt     in gather
        - KeyboardInterrupt     in run, despite try/catch
        """
        async def async1():
            try:
                await asyncio.sleep(3)
                logger.debug("Not Reached.")
            except BaseException as e:
                logger.exception("Sleep catched: %s", type(e))
            logger.debug("Reached.")
        async def async2():
            await asyncio.sleep(1)
            raise KeyboardInterrupt()
        async def gather():
            try:
                await asyncio.gather(async1(), async2())
            except BaseException as e:
                logger.exception("Gather catched: %s", type(e))
        with self.assertRaises(KeyboardInterrupt):
            with self.assertTime(1):
                asyncio.run(gather())
                logger.debug("Not Reached.")
            logger.debug("Not Reached.")
        with self.assertTime(1):
            with self.assertRaises(KeyboardInterrupt):
                asyncio.run(gather())
                logger.debug("Not Reached.")
            logger.debug("Reached.")
        try:
            asyncio.run(gather())
        except BaseException as e:
            logger.exception("Run catched: %s", type(e))

    def test_gather_interrupt_Exception(self):
        """
        raised Exception is forwarded to caller asyncio.gather
        """
        async def async1():
            try:
                await asyncio.sleep(3)
                logger.debug("Not Reached.")
            except BaseException as e:
                logger.exception("Sleep catched: %s", type(e))
                raise
        async def async2():
            await asyncio.sleep(1)
            raise Exception()
        async def gather():
            try:
                await asyncio.gather(async1(), async2())
            except BaseException as e:
                logger.exception("Gather catched: %s", type(e))
        with self.assertTime(1):
            asyncio.run(gather())
            logger.debug("Reached.")

    def test_gather_interrupt_CancelledError(self):
        """
        raised asyncio.exceptions.CancelledError is forwarded to caller asyncio.gather
        like any Exception
        """
        async def async1():
            try:
                await asyncio.sleep(3)
                logger.debug("Not Reached.")
            except BaseException as e:
                logger.exception("Sleep catched: %s", type(e))
                raise
        async def async2():
            await asyncio.sleep(1)
            raise asyncio.exceptions.CancelledError()
        async def gather():
            try:
                await asyncio.gather(async1(), async2())
            except BaseException as e:
                logger.exception("Gather catched: %s", type(e))
        with self.assertTime(1):
            asyncio.run(gather())
            logger.debug("Reached.")
