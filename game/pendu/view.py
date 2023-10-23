from utils import tools
import logging
logger = logging.getLogger(__name__)

from utils.tools import Constant
from mvc.view import UserInteractView
from utils.language import MessageNLS
from utils.language_resources.MessageLiterals import MessageLiterals


class View(UserInteractView):
    """
    View of pendu game.
    """
    def __init__(self, ui):
        super().__init__(ui)

    # UserInteractView specific

    def is_expected_on_message(self, message):
        """
        To be called on on_message event.
        """
        return (super().is_expected_on_message(message)
                and len(message) == 1)

    async def on_message(self, message):
        content = self.ui.get_message(message)
        id = self.ui.get_message_id(message)
        if not self.is_expected_on_message(content):
            logger.log(Constant.VERBOSE, "Ignore message %s.", id)
        else:
            callback = self.get_callback()
            callback.play_letter(content)

    # Pendu specific

    async def send(self, callback):
        """
        Send updated main message.
        """
        await self.ui.send(self.str(callback.word_list, callback.lifes, callback.errors, callback.previous_try))

    async def send_game_over(self, word):
        await self.ui.send(MessageNLS.get_message(MessageLiterals.PENDU_LOSE, word))

    async def send_victory(self, word):
        await self.ui.send(self.str(list(word), Constant.PENDU_NB_MAX_ERRORS, []))
        await self.ui.send(MessageNLS.get_message(MessageLiterals.PENDU_WIN))

    def str(self, word_list, lifes, errors, previous_try=None):
        return self.str_discord(word_list, lifes, errors, previous_try)

    def str_oneline(self, word_list, lifes, errors):
        return "{}  {} {}".format(
                ' '.join(word_list),
                '' if lifes == Constant.PENDU_NB_MAX_ERRORS else MessageNLS.get_message(MessageLiterals.PENDU_ERRORS, Constant.PENDU_NB_MAX_ERRORS - lifes, Constant.PENDU_NB_MAX_ERRORS),
                '' if lifes == Constant.PENDU_NB_MAX_ERRORS else errors)

    def str_discord(self, word_list, lifes, errors, previous_try):
        return str(PenduDrawing(word_list, lifes, errors))

class PenduDrawing:
    """
    Drawing of the pendu in ascii.
    Shown with the multilines block-code quotes (``).
    """
    def __init__(self, word_list, lifes, errors):
        assert Constant.PENDU_NB_MAX_ERRORS == 11, f"The current pendu drawing is done for 11 steps (+1 for no error), not {Constant.PENDU_NB_MAX_ERRORS}."
        self.word = ' '.join(word_list)
        self.word_size = len(word_list) * 2 - 1
        self.nb_errors = Constant.PENDU_NB_MAX_ERRORS - lifes
        self.errors = errors

    def error_step(self, index, string):
        """
        Alias for printing or not a part of the drawing, based on the internal
        count of errors.

        @param  index   minimal step index to show the part.
        @param  string  the part of the drawing to show.
        """
        return string if self.nb_errors >= index else ' ' * len(string)

    def __str__(self):
        if self.nb_errors == 0:
            return "```{}```".format(self.word)
        prefix = ' ' * self.word_size
        inter = '   '
        return "\n".join([
                "```",
                "{}{}  {}".format(prefix, inter, self.error_step(4, '_____')),
                "{}{}  {}{}  {}".format(prefix, inter, self.error_step(2, '|'), self.error_step(3, '/'), self.error_step(5, '|')),
                "{}{}  {}  {}{}{}  {}:".format(prefix, inter, self.error_step(2, '|'), self.error_step(10, '\\'), self.error_step(6, 'O'), self.error_step(11, '/'), MessageNLS.get_message(MessageLiterals.ERRORS)),
                "{}{}  {}   {}   {}".format(self.word, inter, self.error_step(2, '|'), self.error_step(7, '|'), self.errors),
                "{}{}  {}  {} {}".format(prefix, inter, self.error_step(2, '|'), self.error_step(8, '/'), self.error_step(9, '\\')),
                "{}{}{}{}{}".format(prefix, inter, self.error_step(1, '__'), self.error_step(1, '_' if self.nb_errors == 1 else '|'), self.error_step(1, '__')),
                "```"])
