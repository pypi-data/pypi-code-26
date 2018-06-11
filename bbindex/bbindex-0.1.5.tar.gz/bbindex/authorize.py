# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import requests
import traceback
import os


class Authorize(object):
    """
        权限认证
    """
    def __init__(self, username='', password='', token='', session=None):
        self.__username = username
        self.__password = password
        self.__token = token
        self.session = session


    def _authorize(self):
        """账户验证
        """
        username, password, token = self.__username, self.__password, \
                                                  self.__token
        if username and password:
            self._isvalid, token = self.__authorize_user(username, password)
            #预留
        elif token:
            self._isvalid = self.__is_token_valid(token)
            #预留



    def __get_permanent_token_and_set_to_cookie(self, token='', cookies={}):
        if not token:
            ret_json = requests.post('', data={'grant_type':'permanent'}, cookies=cookies).json()
            token = ret_json.get('access_token')

        self.__set_token_to_cookie(token)

        return token


    def __set_token_to_cookie(self, token):
        os.environ['dataapi_token'] = token
        cookie_dict = {'cloud-sso-token': token}
        self.session.cookies = requests.utils.cookiejar_from_dict(cookie_dict)
        return token


    def __authorize_user(self, user, pwd):

        ### 2 user type
        data_type = dict(username=user, password=pwd)

        def user_type(data=None):
            res = self.session.post('AUTHORIZE_URL', data)

            if not res.ok or not res.json().get('content', {}).get('accountId', 0):
                return False, None
            else:
                result = res.json()
                token = result.get('content', {}).get('token', {}).get('tokenString', '')
                principal_name = result.get('content', {}).get('principalName', '')
                os.environ['DatayesPrincipalName'] = principal_name
                return True, token

        valid, token = user_type(data_type)

        if not valid:
            return False, None
        else:
            os.environ['access_token'] = token
            return True, token


    def __is_token_valid(self, token):
        """
                        检验 token 是否有效
        """
        try:
            r = self.session.get('URL', cookies={'token': token})
            r_json = r.json()

            if type(r_json) == list:
                r = self.session.get('AUTH_URL', cookies={'token': token})
                r_json = r.json()

                return True
            elif type(r_json) == dict and r_json.get('code', 0) == -403:
                print ('token {} 无效或过期'.format(token))
                return False
            else:
                print ('token 验证异常: {}'.format(r.text))
                return False
        except:
            print ('token 验证异常')
            print ('-' * 80)
            traceback.print_exc()
            print ('-' * 80)
            return False









