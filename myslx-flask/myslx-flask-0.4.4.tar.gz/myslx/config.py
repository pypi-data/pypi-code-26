import os

PORTAL_DOMAIN = os.environ.get('DOMAIN', 'my.solarlux.com')
OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID', 'localdev1')
OAUTH_CLIENT_SECRET = os.environ.get(
    'OAUTH_CLIENT_SECRET', 'fDtxU18ltTRk59PLu5VRoh670QoRkaym'
)  # '6Htrqkzel6uqeuHZZrjA5Q2EXka4kw10')
OAUTH_ROLES_REQUIRED = os.environ.get('OAUTH_ROLES_REQUIRED', 'ROLE_CMS_SL_MITARBEITER ROLE_SOLARLUX_ADMIN').split()
_default_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiahLhO5+1bWfqSQhdCR7RJLpveU0OICX5rPb4N5AMx6uGhwCgO9U44kkg1Z/K+atcokYJUW72pij0TjFpz9XOAIR1BbpzpsSE/ixe1cRx2kDG1ABiCvWBsldnuuW/KhZi9FtQGnVBysKiXT/0Y87MtJo63ZQwKOK9DSdQWiz/zWgij9oR4Q2Cl3iBrQ3h8HMYEswhKrZfO+GEz8BKUgLeUMr6TJtJQX85Z+ulWcTsxbAZZPzAiNlnBbbd8MV3rimEcfE/0vbRoFXZ/yfQ8PlD09MdrCXjCGnr1WKrKkse9HgTDjnBiewMZiHswYfHHiEqSCw4o3U2XtjGGXWSZiv5wIDAQAB'
OAUTH_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
%s
-----END PUBLIC KEY-----""" % os.environ.get(
    'OAUTH_PUBLIC_KEY', _default_public_key
)
SCRIPT_NAME = os.environ.get('SCRIPT_NAME', '')
