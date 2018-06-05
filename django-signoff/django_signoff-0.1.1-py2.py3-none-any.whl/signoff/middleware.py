from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from signoff.models import Document


class ConsentMiddleware(MiddlewareMixin):
    """
    This middleware redirects users to sign the site's terms of service or
    other documents if they haven't done so.
    """

    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if the user is on one of our pages, if so, pass
            resolved_url = resolve(request.path)
            allowed_apps = ['signoff']
            allowed_urls = ['auth_logout']
            if hasattr(settings, 'SIGNOFF_ADDITIONAL_ALLOWED_APPS'):
                allowed_apps.extend(settings.SIGNOFF_ADDITIONAL_ALLOWED_APPS)
            if hasattr(settings, 'SIGNOFF_ADDITIONAL_ALLOWED_URLS'):
                allowed_urls.extend(settings.SIGNOFF_ADDITIONAL_ALLOWED_URLS)

            if resolved_url.app_name in allowed_apps:
                return
            if resolved_url.url_name in allowed_urls:
                return

            # Check if the user owes us any signatures, if so:
            user_owes_signatures = False
            for document in Document.objects.with_user(request.user)\
                                    .filter(next_version__isnull=True):
                if document.required_by is None or\
                   document.required_by <= timezone.now():
                    if not document.user_consents:
                        user_owes_signatures = True
            if user_owes_signatures:
                return redirect('signoff:signoff_index')
            return
