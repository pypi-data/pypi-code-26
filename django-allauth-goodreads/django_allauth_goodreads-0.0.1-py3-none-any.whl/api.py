from allauth.socialaccount.providers.oauth.client import OAuth

import xmltodict


class GoodreadsAPI(OAuth):
    base_url = 'https://www.goodreads.com/'
    request_token_url = 'http://www.goodreads.com/oauth/request_token'

    def get_user_info(self):
        url = self.base_url + 'api/auth_user'
        content = self.query(url)
        return xmltodict.parse(content)['GoodreadsResponse']['user']
