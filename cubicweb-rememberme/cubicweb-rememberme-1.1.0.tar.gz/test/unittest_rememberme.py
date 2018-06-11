from datetime import timedelta

from cubicweb.devtools.webtest import CubicWebTestTC


class RememberMeAuthenticationTC(CubicWebTestTC):
    def init_auth_cookie(self, login, magic):
        self.auth_cookie.value = '%s|__magic=%s' % (login, str(magic))
        self.webapp.cookiejar.set_cookie(self.auth_cookie)

    def init_login_password(self, login):
        req, origcnx = self.init_authentication('cookie')
        req.session = req.cnx = None
        req.form['__login'] = login
        req.form['__password'] = login
        return req, origcnx

    def test_auth_cookie_authentication(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, 'user')

        # valid login / password, not asked to remember user
        self.login('user')
        self.assertEqual('user', self.webapp.cookies['__data_session'][:4])

        with self.admin_access.repo_cnx() as cnx:
            cookies = cnx.find(
                'CWUser', login='user'
            ).one().reverse_auth_cookie_for_user
            self.assertEqual(len(cookies), 0)

        self.logout()
        self.assertNotIn('__data_session', self.webapp.cookies)

        # valid login / password, ask to remember user
        self.login('user', __setauthcookie=1)
        self.assertEqual('user', self.webapp.cookies['__data_session'][:4])

        for cookie in self.webapp.cookiejar:
            if cookie.name == '__cw_auth_cookie':
                self.auth_cookie = cookie

        with self.admin_access.repo_cnx() as cnx:
            cookies = cnx.find(
                'CWUser', login='user'
            ).one().reverse_auth_cookie_for_user
            self.assertEqual(len(cookies), 1)

            magic = cookies[0].magic
            self.assertEqual(cookies[0].lifetime, timedelta(days=30))

        self.webapp.reset()

        # bad magic number
        self.init_auth_cookie('user', '1234')
        self.webapp.get('/')
        self.assertEqual('anon', self.webapp.cookies['__data_session'][:4])

        # bad login in auth cookie
        self.init_auth_cookie('admin', magic)
        self.webapp.get('/')
        self.assertEqual('anon', self.webapp.cookies['__data_session'][:4])

        # valid auth cookie
        self.init_auth_cookie('user', magic)
        self.webapp.get('/')
        self.assertEqual('user', self.webapp.cookies['__data_session'][:4])

        with self.admin_access.repo_cnx() as cnx:
            cookies = cnx.find(
                'CWUser', login='user'
            ).one().reverse_auth_cookie_for_user
            self.assertEqual(len(cookies), 1)

            magic2 = cookies[0].magic
            self.assertNotEqual(magic2, magic)

        self.logout()


if __name__ == '__main__':
    import unittest
    unittest.main()
