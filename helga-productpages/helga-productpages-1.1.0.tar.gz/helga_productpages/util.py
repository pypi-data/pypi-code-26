import re
from helga import log
from helga_productpages.task import ReleaseTask
from helga import settings


logger = log.getLogger(__name__)


def match_release_phrase(message, phrase):
    """
    Match a release task in this message.

    "helga: rhcs 3.0 beta date"
    "helga: rhcs 3.0 schedule"

    :returns: a ReleaseTask if we matched, or None if no release task.
    """
    botnick = settings.NICK
    pattern = re.compile('%s[,:]? (.+) %s\??$' % (botnick, phrase))
    m = re.match(pattern, message)
    if not m:
        return
    maybe_release = m.group(1)
    result = ReleaseTask.from_text(maybe_release)
    return result
