from __future__ import absolute_import, unicode_literals

import base64

from django.http import HttpResponse
from django.utils.encoding import smart_bytes

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text

from .models import PasswordProtectedUrl


class PasswordProtectMiddleware(object):

    def process_request(self, request):
        """
        Check each request against the list of password-protected URLs
        and enforce HTTP authentication when required.

        Based on https://github.com/plumdog/django-password-protect
        """
        try:
            protected_url = PasswordProtectedUrl.objects.get(url=request.path)
        except PasswordProtectedUrl.DoesNotExist:
            return

        if "HTTP_AUTHORIZATION" in request.META:
            authentication = smart_text(request.META["HTTP_AUTHORIZATION"], "ascii")
            method, credentials = authentication.split(" ", 1)
            credentials = credentials.strip()

            if method.lower() == "basic":
                credentials = base64.decodestring(smart_bytes(credentials)).decode("ascii")
                username, password = credentials.split(":", 1)
                username_ok = username == protected_url.username
                password_ok = password == protected_url.password

                if username_ok and password_ok:
                    return

        html = (
            "<html>"
            "<title>Auth required</title>"
            "<body><h1>Authorization Required</h1></body>"
            "</html>")
        response = HttpResponse(html, content_type="text/html")
        response["WWW-Authenticate"] = "Basic realm=\"This page is password-protected\""
        response.status_code = 401
        return response
