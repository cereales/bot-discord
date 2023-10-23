from enum import Enum

class MessageLiterals(Enum):
    DEFAULT     = "Default"
    ERRORS      = "Errors"
    HELLO       = "Hello {0}"
    INVALID_ROLE    = "You do not have permissions for this command."
    PENDU_ERRORS    = "{0} errors/{1}"
    PENDU_LOSE  = "Game Over... The correct word was {0}."
    PENDU_WIN   = "Winner !"
