import datetime
from twisted.internet import defer
from txproductpages.exceptions import ReleaseNotFoundException
from txproductpages.exceptions import TaskNotFoundException
from helga_productpages.util import match_release_phrase
from rhcalendar import networkdays


def match(message):
    """
    "helga: rhcs 3.0 beta date"
    "helga: rhcs 3.0 release date"

    :returns: a ReleaseTask if we matched, or None if no release task.
    """
    return match_release_phrase(message, 'date')


@defer.inlineCallbacks
def describe_milestone(pp, release_task, client, channel, nick):
    """
    Describe this release's milestone date in a message.
    """
    try:
        release = yield pp.release(release_task.shortname)
    except ReleaseNotFoundException:
        msg = '%s, I could not find release %s in pp.engineering.redhat.com' \
              % (nick, release_task.shortname)
        defer.returnValue(msg)
    try:
        task_date = yield release.task_date(release_task.task_re)
    except TaskNotFoundException:
        # TODO: link to web ui for all tasks?
        tmpl = ('{nick}, I could not find a {milestone} task for '
                '{shortname} in {url}')
        url = pp.schedule_url(release_task.shortname)
        msg = tmpl.format(nick=nick, milestone=release_task.milestone,
                          shortname=release_task.shortname, url=url)
        defer.returnValue(msg)
    msg = construct_message(nick, release, release_task.milestone, task_date)
    defer.returnValue(msg)


def send_message(message, shortname, client, channel, nick):
    """
    Send a message to channel.
    """
    client.msg(channel, message)


def construct_message(nick, release, milestone, task_date):
    """
    Construct message string about this release's ship date.
    """
    today = datetime.date.today()
    days = networkdays(from_date=today, to_date=task_date) - 1
    description = describe_date_from_today(task_date)
    tmpl = '{nick}, {name} {milestone} {verb} {description}'
    verb = 'is'
    if days < 0:
        verb = 'was'
    return tmpl.format(nick=nick, name=release.name, milestone=milestone,
                       verb=verb, description=description)


def describe_date_from_today(to_date):
    """
    Human-readable description for the given date, compared to today.
    """
    datestr = to_date.strftime("%a %b %-d, %Y")
    today = datetime.date.today()
    days = networkdays(from_date=today, to_date=to_date) - 1
    if days == 1:
        tmpl = 'on {date} (one business day from today)'
    if days > 1:
        tmpl = 'on {date} ({days} business days from today)'
    if days == 0:
        tmpl = 'today'
    if days == -1:
        days = -days
        tmpl = 'on {date} (one business day ago)'
    if days < -1:
        days = -days
        tmpl = 'on {date} ({days} business days ago)'
    return tmpl.format(date=datestr, days=days)


# List of callbacks to fire on a match:
callbacks = (describe_milestone, send_message)
