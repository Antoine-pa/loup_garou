from .cupidon import *
from .voyante import *
from .loups import *
from .voleur import *
from .sorciere import *
from .vote import *
from .chien_loup import *
from .distribution_role import *
from .enfant_sauvage import *
from .loup_blanc import *
from ..tools import *
class Phases(Cupidon, Voleur, Voyante, Loups, Sorciere, Vote, Distribution, ChienLoup, EnfantSauvage, LoupBlanc):
    pass
"""
ordre:
- voleur
- enfant-sauvage
- chien-loup
- cupidon
    - voyante
    - loup
    - loup-blanc
    - sorière
    - vote
"""