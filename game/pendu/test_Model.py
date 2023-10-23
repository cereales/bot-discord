from utils import tools
import logging
logger = logging.getLogger(__name__)

from game.pendu.model import Model
from test.archi import TestCase
from utils.tools import Constant


class TestModel(TestCase):
    def test_str(self):
        """
        Test the output of str function.
        """
        model = Model()
        model.secret_word = "test"
        model.restart()
        logger.info(model)
        self.assertEqual("t _ _ _", str(model))

    @TestCase.interactive()
    def test_play_interactive(self):
        """
        Play the game on word 'test'
        """
        model = Model()
        model.secret_word = "test"
        model.restart()
        logger.info(model)
        self.assertEqual("t _ _ _", str(model))
        while not model.is_over():
            letter = ''
            while len(letter) != 1:
                letter = input('> ')
            model.play_letter(letter)
            logger.info(f"{model} \t{model.lifes}/{Constant.PENDU_NB_MAX_ERRORS}")
        if model.lost():
            logger.info("Game lost...")
        else:
            logger.info("Winner !")
