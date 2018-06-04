from twisted.internet import defer
from txproductpages.exceptions import ReleaseNotFoundException
from helga_productpages.util import match_release_phrase


def match(message):
    """
    "helga: rhcs 3.0 schedule"
    "helga: rhcs 3.0 release schedule"

    :returns: a ReleaseTask if we matched, or None if no release task.
    """
    return match_release_phrase(message, 'schedule')


@defer.inlineCallbacks
def describe_schedule(pp, release_task, client, channel, nick):
    """
    Link to this release's schedule in a message.
    """
    try:
        release = yield pp.release(release_task.shortname)
    except ReleaseNotFoundException:
        msg = '%s, I could not find release %s in pp.engineering.redhat.com' \
              % (nick, release_task.shortname)
        defer.returnValue(msg)
    url = pp.schedule_url(release_task.shortname)
    tmpl = ('{nick}, {name} schedule: {url}')
    msg = tmpl.format(nick=nick, name=release.name, url=url)
    defer.returnValue(msg)


def send_message(message, shortname, client, channel, nick):
    """
    Send a message to channel.
    """
    client.msg(channel, message)


# List of callbacks to fire on a match:
callbacks = (describe_schedule, send_message)
