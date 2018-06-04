from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class ConsentMiddleware(MiddlewareMixin):
    """
    This middleware redirects users to sign the site's terms of service or
    other documents if they haven't done so.
    """

    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if the user is on a /legal/ page, if so, pass
            if request.resolver_match.app_name == 'django_signoff':
                return

            # Check if the user owes us any signatures, if so:
            user_owes_signatures = False
            if user_owes_signatures:
                return redirect('legal_index')
            return

