from enum import Enum

class MessageLiterals_fr(Enum):
    DEFAULT     = "ValeurDefaut"
    ERRORS      = "Erreurs"
    HELLO       = "Bonjour {0}"
    INVALID_ROLE    = "Tu n'as pas les authorisations pour cette commande."
    PENDU_ERRORS    = "{0} erreurs/{1}"
    PENDU_LOSE  = "Perdu... Le mot à trouver était {0}."
    PENDU_WIN   = "Gagné !"
