"""CAS authentication middleware"""


from django.conf import settings
from django.contrib.auth import logout as do_logout
from django.http import HttpResponseRedirect
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .exceptions import CasTicketException
from .utils import single_sign_out


__all__ = ['CASMiddleware']


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def cas_request_logout_allowed(request):
    """ Checks if the remote server is allowed to send cas logout request
    If nothing is set in the CAS_LOGOUT_REQUEST_ALLOWED parameter, all remote
    servers are allowed. Be careful !
    """
    from socket import gethostbyaddr
    remote_address = get_client_ip(request)
    if remote_address:
        try:
            remote_host = gethostbyaddr(remote_address)[0]
        except Exception:
            return False
        allowed_hosts = settings.CAS_LOGOUT_REQUEST_ALLOWED
        return not allowed_hosts or remote_host in allowed_hosts
    return False


class CASMiddleware(MiddlewareMixin):
    """Middleware that allows CAS authentication on admin pages"""

    def _is_an_admin_view(self, view_func):
        return view_func.__module__.startswith('django.contrib.admin.')

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        logoutRequest = request.POST.get('logoutRequest', '')
        if logoutRequest:
            return single_sign_out(request)
        return None

    def process_exception(self, request, exception):
        """When we get a CasTicketException, that is probably caused by the ticket timing out.
        So logout/login and get the same page again."""
        if isinstance(exception, CasTicketException):
            do_logout(request)
            # This assumes that request.path requires authentication.
            return HttpResponseRedirect(request.path)
        else:
            return None
