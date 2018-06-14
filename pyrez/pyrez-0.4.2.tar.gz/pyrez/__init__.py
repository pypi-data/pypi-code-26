name = "pyrez"

from pyrez.api import PaladinsAPI as PaladinsAPI
from pyrez.api import SmiteAPI as SmiteAPI
from pyrez.api import HiRezAPI as HiRezAPI

from pyrez.enumerations import Champions as Champions
from pyrez.enumerations import Endpoint as Endpoint
from pyrez.enumerations import LanguageCode as LanguageCode
from pyrez.enumerations import Platform as Platform
from pyrez.enumerations import PlayerStatus as PlayerStatus
from pyrez.enumerations import ResponseFormat as ResponseFormat
from pyrez.enumerations import Tier as Tier

from pyrez.models import APIResponse as APIResponse
from pyrez.models import Champion as Champion
from pyrez.models import ChampionRank as ChampionRank
from pyrez.models import DataUsed as DataUsed
from pyrez.models import Friend as Friend
from pyrez.models import God as God
from pyrez.models import HiRezServerStatus as HiRezServerStatus
from pyrez.models import PlayerPaladins as PlayerPaladins
from pyrez.models import PlayerSmite as PlayerSmite
from pyrez.models import Session as Session

from pyrez.exceptions import CustomException as CustomException
from pyrez.exceptions import DailyLimitException as DailyLimitException
from pyrez.exceptions import KeyOrAuthEmptyException as KeyOrAuthEmptyException
from pyrez.exceptions import NotFoundException as NotFoundException
from pyrez.exceptions import SessionLimitException as SessionLimitException
from pyrez.exceptions import WrongCredentials as WrongCredentials
