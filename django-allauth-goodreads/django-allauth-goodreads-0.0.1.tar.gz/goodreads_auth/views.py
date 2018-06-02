from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthLoginView,
    OAuthCallbackView
)

from .provider import GoodreadsProvider
from .api import GoodreadsAPI


class GoodreadsOAuthAdapter(OAuthAdapter):
    provider_id = GoodreadsProvider.id

    request_token_url = 'https://www.goodreads.com/oauth/request_token'
    authorize_url = 'https://www.goodreads.com/oauth/authorize'
    access_token_url = 'https://www.goodreads.com/oauth/access_token'

    def complete_login(self, request, app, token, response):
        client = GoodreadsAPI(request, app.client_id, app.secret,
                              self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuthLoginView.adapter_view(GoodreadsOAuthAdapter)
oauth2_callback = OAuthCallbackView.adapter_view(GoodreadsOAuthAdapter)
