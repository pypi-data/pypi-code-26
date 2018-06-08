from . import api  # noqa
from . import check  # noqa
from . import error  # noqa
from . import ws  # noqa

from .api.decorators import APIDecorators
from .ws.web_service import WebService  # noqa

wsapi = APIDecorators()
