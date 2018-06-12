# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from json_render import json_render


def set_or_del_cookie(response, setcookie=False, delcookie=False, signedcookie=True, cookie_key=None, cookie_value=None, cookie_salt=None,
                  cookie_max_age=None, cookie_expires=None, cookie_path='/', cookie_domain=None, cookie_secure=False, cookie_httponly=False):
    if setcookie:
        if signedcookie:
            response.set_signed_cookie(cookie_key, cookie_value, salt=cookie_salt, **{
                'max_age': cookie_max_age,
                'expires': cookie_expires,
                'path': cookie_path,
                'domain': cookie_domain,
                'secure': cookie_secure,
                'httponly': cookie_httponly,
            })
        else:
            response.set_cookie(cookie_key, cookie_value, max_age=cookie_max_age, expires=cookie_expires, path=cookie_path, domain=cookie_domain, secure=cookie_secure, httponly=cookie_httponly)

    if delcookie:
        response.delete_cookie(cookie_key)

    return response


def cookie_redirect(to, setcookie=False, delcookie=False, signedcookie=True, cookie_key=None, cookie_value=None, cookie_salt=None,
                    cookie_max_age=None, cookie_expires=None, cookie_path='/', cookie_domain=None, cookie_secure=False, cookie_httponly=False, *args, **kwargs):

    response = redirect(to, *args, **kwargs)

    return set_or_del_cookie(
        response,
        setcookie=setcookie,
        delcookie=delcookie,
        signedcookie=signedcookie,
        cookie_key=cookie_key,
        cookie_value=cookie_value,
        cookie_salt=cookie_salt,
        cookie_max_age=cookie_max_age,
        cookie_expires=cookie_expires,
        cookie_path=cookie_path,
        cookie_domain=cookie_domain,
        cookie_secure=cookie_secure,
        cookie_httponly=cookie_httponly
    )
