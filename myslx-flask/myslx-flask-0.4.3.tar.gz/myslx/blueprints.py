import jwt
import requests
from flask import Blueprint, make_response, redirect, abort, request, g, current_app, render_template, url_for
from jwt import InvalidTokenError
from requests.auth import HTTPBasicAuth

from myslx import config
from myslx.utils import has_roles

myslx = Blueprint('myslx', __name__, template_folder='templates')


@myslx.before_app_request
def before_request():
    g.user = None
    access_token = request.cookies.get('access_token')
    if not access_token:
        return

    try:
        data = jwt.decode(
            access_token, config.OAUTH_PUBLIC_KEY, algorithms=['RS256']
        )
    except InvalidTokenError as e:
        current_app.logger.warn('authentication failed, token invalid: %s' % e)
        return

    # check minimum roles from config
    if not has_roles(data['authorities'], config.OAUTH_ROLES_REQUIRED):
        abort(403)
    g.user = data


@myslx.route('/accounts/callback')
def callback():
    code = request.args.get('code')
    if not code:
        abort(403)
    res = requests.post(
        f"https://{config.PORTAL_DOMAIN}/auth/oauth/token?grant_type=authorization_code&code={code}&redirect_uri={url_for('myslx.callback', _external=True)}",
        auth=HTTPBasicAuth(config.OAUTH_CLIENT_ID, config.OAUTH_CLIENT_SECRET),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=10,
    )
    if res.status_code != 200:
        current_app.logger.warn(
            'authentication failed, auth svc responsed with %s',
            res.status_code,
        )
        abort(403)
    res_data = res.json()
    access_token = res_data['access_token']
    try:
        data = jwt.decode(
            access_token, config.OAUTH_PUBLIC_KEY, algorithms=['RS256']
        )
        current_app.logger.info('%s logged in successfully', data['email'])
    except InvalidTokenError as e:
        current_app.logger.warn('authentication failed, token invalid: %s' % e)
        abort(403)
    resp = redirect('/')
    for c in ['access_token', 'refresh_token']:
        resp.set_cookie(c, res_data[c])
    resp.set_cookie('expiration_time', str(res_data['expires_in']))
    return resp


@myslx.route('/logout')
def logout():
    resp = make_response(render_template('logged_out.html'))
    for c in ['access_token', 'refresh_token', 'expiration_time']:
        resp.set_cookie(c, '')
    return resp
