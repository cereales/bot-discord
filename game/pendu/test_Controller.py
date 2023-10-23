from utils import tools
import logging
logger = logging.getLogger(__name__)

import asyncio
from game.pendu.controller import Controller, Callback
from game.pendu.view import View
from test.archi import TestCase, DiscordOrchestratorForTest
from test.interaction import ConsoleUIForTest, UIForTest
from time import time


class TestAbstractController(TestCase):
    """
    Tests AbstractController through Pendu classes.
    This allows to detect regressions or changes of method signatures in Pendu also.
    """
    def get_user_view(self, sleep, no_return=False):
        class ViewForTest:
            async def call(self, cb): # user method
                logger.log(tools.Constant.VERBOSE, "Start user script.")
                await asyncio.sleep(sleep)
                logger.log(tools.Constant.VERBOSE, "\tUser answers.")
                cb.call()
                while no_return:
                    await asyncio.sleep(.5)
                    logger.log(tools.Constant.VERBOSE, "\tUser still processing...")
                logger.log(tools.Constant.VERBOSE, "-->\tUser returns.")
        return ViewForTest()

    def get_callback(self):
        class CallbackForTest(Callback):
            def __init__(self):
                super().__init__(None, None, None, None)
            def call(self):
                self.letter = 0
        return CallbackForTest()


    def test_callback_wait(self):
        cb = self.get_callback()
        t = time()
        with self.assertRaises(TimeoutError):
            asyncio.run(cb.wait(timeout=2))
        t = time() - t
        self.assertIncertitude(t, 2.05)

        cb.call()
        cb.end_call = True
        t = time()
        asyncio.run(cb.wait(timeout=2))
        t = time() - t
        self.assertIncertitude(t, 0.05)

    def test_controller_user_timeout(self):
        view, cb = self.get_user_view(2), self.get_callback()
        t = time()
        with self.assertRaises(TimeoutError):
            asyncio.run(Controller.call(view, cb, timeout=1))
        t = time() - t
        self.assertIncertitude(t, 1.05)

    def test_controller_user_answer(self):
        view, cb = self.get_user_view(.5), self.get_callback()
        t = time()
        asyncio.run(Controller.call(view, cb, timeout=2))
        t = time() - t
        self.assertIncertitude(t, 1.05) # timeout works by units of 1 sec

        t = time()
        cb.letter = None # not answered
        asyncio.run(Controller.call(view, cb, timeout=2))
        cb.letter = None # not answered
        asyncio.run(Controller.call(view, cb, timeout=2))
        cb.letter = None # not answered
        asyncio.run(Controller.call(view, cb, timeout=2))
        cb.letter = None # not answered
        asyncio.run(Controller.call(view, cb, timeout=2))
        cb.letter = None # not answered
        asyncio.run(Controller.call(view, cb, timeout=2))
        t = time() - t
        self.assertIncertitude(t, 5.25, .03) # timeout works by units of 1 sec

    def test_controller_user_answer_but_no_return(self):
        view, cb = self.get_user_view(.5, no_return=True), self.get_callback()
        t = time()
        with self.assertRaises(TimeoutError):
            asyncio.run(Controller.call(view, cb, timeout=2))
        t = time() - t
        self.assertIncertitude(t, 2.05) # timeout works by units of 1 sec

class TestController(TestCase):
    """
    Tests Pendu game.
    """
    @TestCase.interactive()
    def test_play_game_interact(self):
        """
        Play an entire game, from console.
        """
        orchestrator = DiscordOrchestratorForTest()
        view = View(ConsoleUIForTest())
        orchestrator.lock_new_view(view.id)
        orchestrator.open_new_view(view.id, view)

        game = Controller(orchestrator, None, view)
        asyncio.run(game.loop())

    def test_play_game(self):
        """
        Play an entire game to the lose.
        """
        orchestrator = DiscordOrchestratorForTest()
        view = View(UIForTest(['w'] * 12))
        orchestrator.lock_new_view(view.id)
        orchestrator.open_new_view(view.id, view)

        game = Controller(orchestrator, None, view)
        asyncio.run(game.loop())
        self.assertTrue(game.model.is_over())
        self.assertTrue(game.model.lost())
