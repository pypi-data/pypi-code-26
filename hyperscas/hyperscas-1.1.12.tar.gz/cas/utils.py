import logging

from django.core.cache import cache
from django.contrib import auth
from django.conf import settings
from django.http import HttpResponseRedirect
from six.moves.urllib_parse import urlencode
from six.moves import urllib_parse as urlparse
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

from .models import SessionServiceTicket

logger = logging.getLogger('cas')


def _logout_url(request, next_page=None, cas_url=None):
    """
    Generates CAS logout URL

    :param: request RequestObj
    :param: next_page Page to redirect after logout.

    """

    url = urlparse.urljoin(cas_url, 'logout')

    if next_page and getattr(settings, 'CAS_PROVIDE_URL_TO_LOGOUT', True):
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'service': protocol + host + next_page})

    return url


def _redirect_url(request):
    """
    Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.

    :param: request RequestObj

    """

    next = request.GET.get("next", "")

    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)

        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        prefix = protocol + host

        if next.startswith(prefix):
            next = next[len(prefix):]

    return next


def _get_session(samlp):
    """ Recovers the session mapped with the CAS service ticket
    received in the SAML CAS request at CAS logout
    """

    tree = ET.fromstring(samlp)
    if tree[1].tag.endswith('SessionIndex'):
        ticket = tree[1].text
    sst = SessionServiceTicket.get_by_id(ticket)
    if not sst:
        logger.error('cant find sst for ticket %s' % ticket)
        return None
    return sst.get_session()


def cacheByTime(seconds=5 * 60):
    """
    根据时间来cache
    """

    def wapper(func):
        def inner(*args):  # 参数必须是位置参数
            response = cache.get(args)
            if response:
                return response
            response = func(*args)
            cache.set(args, response, seconds)
            return response

        return inner

    return wapper


def getCasKey(email):
    return 'CAS:{}'.format(email)


def single_sign_out(request, next_page=None):
    domain = request.domain
    ticket = request.POST.get('logoutRequest')
    if ticket:
        request.session = _get_session(ticket)
        request.user = auth.get_user(request)
        logger.debug(
            "Got single sign out callback from CAS for user %s session %s",
            request.user, request.session.session_key)
    auth.logout(request)
    casUrl = domain.auth.url + '/cas/'
    if not next_page:
        next_page = _redirect_url(request)
    return HttpResponseRedirect(_logout_url(request, next_page, casUrl))
