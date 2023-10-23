"""
This module define the data model for Pendu game.
The data model store data of the game and provide method to interact with it.
It is manipulated by a controller.
"""
from utils import tools
import logging
logger = logging.getLogger(__name__)

from random import randint
from utils.tools import Constant


class Model:
    """
    Represent the data model of Pendu game.
    """
    def __init__(self):
        self.secret_word = self.pick_random_word()
        self.restart()

    def restart(self):
        """
        Initialise the game instance from the internal secret_word data member.
        """
        # list of letters, seen from the user; '_' for hiden letter
        self.letters = ['_' for _ in range(len(self.secret_word))]
        self.letters[0] = self.secret_word[0]
        # remaining tries. Lose when reach zero
        self.lifes = Constant.PENDU_NB_MAX_ERRORS
        # list of unsuccessful tries
        self.errors = []

    def pick_random_word(self):
        """
        Return a random word from french dictionary.
        The word must be at least 3 letters long. Random selection is repeated
        if the word is too short, but the last tentative will be returned even
        if it is still too short.

        @return     French word in lowercase
        """
        with open(Constant.PENDU_DATABASE_FILE) as file:
            lines = file.readlines()
            retry = 10
            word = ""
            while len(word) < 3 and retry >= 0:
                index = randint(0, len(lines) - 1)
                word = lines[index].strip()
                retry -= 1
                logger.log(Constant.VERBOSE, "The secret word is '%s'", word)
            return word.lower()

    # Getters

    def lost(self):
        """
        True if the game is lost.
        """
        return self.lifes <= 0

    def is_over(self):
        """
        True if the game is done.
        """
        return self.lost() or '_' not in self.letters

    def get_word_list(self):
        return self.letters.copy()

    def get_lifes(self):
        return self.lifes

    def get_errors(self):
        return self.errors.copy()

    def __str__(self):
        """
        Word seen by the user.
        For example : "test" -> "t _ _ _"
        """
        return ' '.join(self.letters)

    # play

    def play_letter(self, test_letter):
        """
        Main play action.
        Try the provided letter and return if this was a successful move, or not.

        @param  test_letter     a single letter

        @return     True if a new letter was discovered. False otherwise.
        """
        win = False
        test_letter = test_letter.lower()
        for secret_index, secret_letter in enumerate(self.secret_word):
            if secret_letter == test_letter and self.letters[secret_index] == '_':
                win = True
                self.letters[secret_index] = secret_letter
        if not win:
            self.lifes -= 1
            self.errors.append(test_letter)
        return win
