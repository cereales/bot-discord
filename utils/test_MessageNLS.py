from utils import tools
import logging
logger = logging.getLogger(__name__)

from test.archi import TestCase
from enum import Enum
from utils.language import MessageNLS, SUPPORTED_LANG_CODES
from utils.language_resources.MessageLiterals import MessageLiterals
from utils.language_resources.MessageLiterals_fr import MessageLiterals_fr


class TestMessageNLS(TestCase):
    def test_basic_class_member(self):
        """
        Test that language setting is shared to all instances.
        """
        a = MessageNLS()
        self.assertEqual(MessageLiterals, a.message_literals)
        logger.debug(MessageNLS.get_message(MessageLiterals.DEFAULT))
        self.assertEqual("Default", MessageNLS.get_message(MessageLiterals.DEFAULT))

        b = MessageNLS()
        MessageNLS.set_language("fr")
        self.assertEqual(MessageLiterals_fr, b.message_literals)

        b = MessageNLS() # new instance
        self.assertEqual(MessageLiterals_fr, b.message_literals)
        logger.debug(MessageNLS.get_message(MessageLiterals.DEFAULT))

        # end
        MessageNLS.set_language("en")

    def test_message_arguments(self):
        """
        Test the syntax of arguments in nls message.

        Note: It is ok to give too many arguments.
        """
        # expecting 1 args  1/1
        msg = MessageNLS.get_message(MessageLiterals.HELLO, "toto")
        logger.debug(msg)
        self.assertIn("toto", msg)

        # not enought args  0/1
        msg = MessageNLS.get_message(MessageLiterals.HELLO)
        logger.debug(msg)
        self.assertEqual("Default", msg) # no exception

        # too many args  2/1
        msg = MessageNLS.get_message(MessageLiterals.HELLO, "toto", "extra arg")
        logger.debug(msg)
        self.assertIn("toto", msg)

        # args for 0 expected  1/0
        msg = MessageNLS.get_message(MessageLiterals.ERRORS, "extra arg")
        logger.debug(msg)
        self.assertEqual("Errors", msg)

    def test_wrong_tag(self):
        msg = MessageNLS.get_message("grekjndsj", "extra arg")
        logger.debug(msg)
        self.assertEqual("Default", msg) # no exception

    def test_set_error(self):
        """
        Set language to a non supported must raise an error.
        """
        with self.assertRaises(AttributeError):
            MessageNLS.set_language("FR")

    def test_check_languages_unicity(self):
        """
        All nls literals must exist in all supported languages.
        """
        logger.log(logging.ERROR + 1, "Starting NLS literals check.") # to make sure following logs start on a newline.
        error = 0
        en_keys = set(MessageLiterals._member_names_)
        for lang_code, message_literals in SUPPORTED_LANG_CODES.items():
            with self.subTest(literals=lang_code):
                self.assertTrue(issubclass(message_literals, Enum))
            lang_keys = set(message_literals._member_names_)
            for key in en_keys - lang_keys:
                error += 1
                logger.error("MessageLiterals_%s\t: Missing '%s' literal.", lang_code, key)
            for key in lang_keys - en_keys:
                error += 1
                logger.error("MessageLiterals \t: Missing '%s' literal from MessageLiterals_%s.", key, lang_code)
        self.assertEqual(0, error,
                         f"There are {error} missing literals. See logs for details.")
