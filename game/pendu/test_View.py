from utils import tools
import logging
logger = logging.getLogger(__name__)

import time
from game.pendu.view import PenduDrawing
from test.archi import TestCase
from utils.tools import Constant


class TestView(TestCase):
    @TestCase.visual_test()
    def test_visual(self):
        a = str(PenduDrawing(['t', '_', '_', '_'], Constant.PENDU_NB_MAX_ERRORS, []))
        logger.info(a)
        self.assertEqual(a, "```t _ _ _```")
        a = str(PenduDrawing(['t', '_', '_', '_'], Constant.PENDU_NB_MAX_ERRORS - 1, ['a']))
        logger.info(a)
        self.assertIn('\n', a)
        a = str(PenduDrawing(['t', '_', '_', '_'], 4, []))
        logger.info(a)
        self.assertIn('\n', a)
        a = str(PenduDrawing(['t', '_', '_', '_'], 0, ['y']))
        logger.info(a)
        self.assertIn('\n', a)

    @TestCase.visual_test()
    def test_visual_painting(self):
        for lifes in range(Constant.PENDU_NB_MAX_ERRORS, -1, -1):
            time.sleep(.5)
            logger.info("Lifes %s/%s: %s", lifes, Constant.PENDU_NB_MAX_ERRORS, str(PenduDrawing(['t', '_', '_', '_'], lifes, ['y', 'a'])))
