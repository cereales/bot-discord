"""
Definitions of Controller and Callback objects for Pendu game.
"""
from utils import tools
import logging
logger = logging.getLogger(__name__)

import asyncio
from game.pendu.model import Model
from mvc.controller import AbstractController, AbstractCallback


class Controller(AbstractController):
    """
    Controller for Pendu game.
    """
    def __init__(self, orchestrator, context, view):
        super().__init__(orchestrator, Model(), view)
        assert not self.model.is_over()

    # Lifecycle

    async def loop(self):
        """
        Main game loop.
        """
        previous_try = None

        while not self.model.is_over():
            callback = Callback(self.model.get_word_list(), self.model.get_lifes(), self.model.get_errors(), previous_try)
            try:
                await self.call(self.main_view, callback, timeout=10*60)
                letter = callback.letter

                # if no error, then play the letter
                previous_try = letter if self.model.play_letter(letter) else False
            except TimeoutError:
                logger.warning("Player did not answer before timeout.") # should never appear in case of no timeout.
            except asyncio.exceptions.CancelledError:
                logger.error("Ctrl+C catched.")
                raise
            except:
                logger.exception("Call to player failed.")
                raise

        self.orchestrator.close_view(self.main_view.id)
        if self.model.lost():
            await self.main_view.send_game_over(self.model.secret_word)
        else:
            await self.main_view.send_victory(self.model.secret_word)


class Callback(AbstractCallback):
    """
    Callback object for Pendu game.
    """
    def __init__(self, word_list, lifes, errors, previous_try):
        super().__init__()
        # inputs
        self.word_list = word_list
        self.lifes = lifes
        self.errors = errors
        self.previous_try = previous_try
        # output
        self.letter = None

    def answered(self):
        return self.letter is not None

    # call

    def play_letter(self, letter):
        """
        The view must call this method to play a move.
        """
        self.letter = letter
