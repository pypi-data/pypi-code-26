from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class GoodreadsAccount(ProviderAccount):
    pass


class GoodreadsProvider(OAuthProvider):
    id = 'goodreads'
    name = 'Goodreads'
    package = 'goodreads_auth'
    account_class = GoodreadsAccount

    def extract_uid(self, data):
        return str(data['@id'])

    def extract_common_fields(self, data):
        fields = {
            'first_name': data.get('name'),
        }
        return fields


providers.registry.register(GoodreadsProvider)
