from utils import tools

from test.archi import TestCase, TimeChecker
from time import sleep


class TestTools(TestCase):
    def test_internet(self):
        """
        Connected tests must be decarted with @TestCase.connected .
        When there is no internet connection, connected tests are skiped.
        In that case, this test fails to warn about the issue.
        """
        self.assertFalse(tools.Constant.NO_INTERNET)

    def test_assertTime(self):
        """
        Test the syntax of assertTime utility.
        """
        with TimeChecker(self, 2) as t:
            t.assertEquals(0)
            sleep(1)
            t.assertEquals(1)
            sleep(1)

        with self.assertTime(2) as t:
            t.assertEquals(0)
            sleep(1)
            t.assertEquals(1)
            sleep(1)

        with self.assertRaises(AssertionError):
            with self.assertTime(2) as t:
                sleep(1)
