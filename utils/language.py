"""
Manage language text messages from tags.
These messages are define in literals class that must inherit from Enum.

Default language (english) is MessageLiterals.
Others languages must be defined in a dedicated class.
Text messages can support arguments, formated {i} with index i starting from 0.
"""
from utils import tools
import logging
logger = logging.getLogger(__name__)

from utils.language_resources.MessageLiterals import MessageLiterals
from utils.language_resources.MessageLiterals_fr import MessageLiterals_fr

SUPPORTED_LANG_CODES = {
        "en": MessageLiterals,
        "fr": MessageLiterals_fr
}


class MessageNLS:
    """
    This class allows to retrieve text messages in any supported language,
    based on tags.
    The language is set once for the entire program.
    To get a text, call:
    `MessageNLS.get_message(MessageLiterals.*TAG*)`

    Arguments can be given to method, if any:
    `MessageNLS.get_message(MessageLiterals.*TAG*, arg1)`
    """
    message_literals = MessageLiterals

    def set_language(lang_code):
        """
        Setup language for all follong calls in the current program.
        Class method.

        @param  lang_code   String of the code identifier of the language.
        @raise  AttributeError  on bad provided lang_code.
        """
        if lang_code in SUPPORTED_LANG_CODES:
            MessageNLS.message_literals = SUPPORTED_LANG_CODES[lang_code]
        else:
            raise AttributeError(f"'{lang_code}' is not supported.")

    def get_message(key, *args):
        """
        Return the text message (in the current language) associated to the provided tag.
        Class method.

        @param  key     tag in MessageLiterals.
        @param  args    Optional. Parameters to fill the {i} in text.

        In case of error, a default message is returned.
        """
        try:
            return getattr(MessageNLS.message_literals, key.name).value.format(*args)
        except IndexError:
            logger.error("Missing parameters for message '%s'", key.name)
            return MessageNLS.get_message(MessageLiterals.DEFAULT)
        except AttributeError as e:
            logger.error("Cannot get requested message: '%s'", key)
            return MessageNLS.get_message(MessageLiterals.DEFAULT)
