from txproductpages import Connection
from txproductpages.exceptions import ProductPagesException
from twisted.internet import defer
from helga.plugins import match, ResponseNotReady
from helga import log
from helga_productpages.actions import release_date
from helga_productpages.actions import release_schedule

__version__ = '1.1.0'


logger = log.getLogger(__name__)


def match_pp(message):
    for action in (release_date, release_schedule):
        m = action.match(message)
        if m:
            return (action, m)


@match(match_pp)
def helga_productpages(client, channel, nick, message, action_and_match):
    """
    Match information related to Product Pages.
    """
    pp = Connection()

    d = defer.succeed(pp)
    (action, match) = action_and_match
    for callback in action.callbacks:
        d.addCallback(callback, match, client, channel, nick)
        d.addErrback(send_err, client, channel)
    raise ResponseNotReady


def send_err(e, client, channel):
    client.msg(channel, str(e.value))
    # Provide the file and line number if this was an an unexpected error.
    if not isinstance(e.value, ProductPagesException):
        tb = e.getBriefTraceback().split()
        client.msg(channel, str(tb[-1]))
