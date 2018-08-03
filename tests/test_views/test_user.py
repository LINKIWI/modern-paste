from flask_login import current_user

import config

import util.testing
import views.user
from uri.main import *
from uri.user import *


class TestUser(util.testing.DatabaseTestCase):
    def test_user_login_interface(self):
        self.assertIn('Log in to view, control, and delete your pastes', views.user.user_login_interface())

        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        redirect_resp = views.user.user_login_interface()
        self.assertEqual(302, redirect_resp.status_code)
        self.assertEqual(HomeURI.uri(), redirect_resp.location)

        self.api_logout_user()
        self.assertIn('Log in to view, control, and delete your pastes', views.user.user_login_interface())

    def test_user_logout_interface(self):
        self.assertFalse(current_user.is_authenticated)
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        self.assertTrue(current_user.is_authenticated)
        redirect_resp = views.user.user_logout_interface()
        self.assertEqual(302, redirect_resp.status_code)
        self.assertEqual(HomeURI.uri(), redirect_resp.location)
        self.assertFalse(current_user.is_authenticated)

    def test_user_register_interface(self):
        self.assertIn('Register for an account to view, modify, and delete your pastes', views.user.user_register_interface())

        self.assertFalse(current_user.is_authenticated)
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        self.assertTrue(current_user.is_authenticated)
        redirect_resp = views.user.user_register_interface()
        self.assertEqual(302, redirect_resp.status_code)
        self.assertEqual(HomeURI.uri(), redirect_resp.location)

    def test_user_register_interface_non_local_auth(self):
        config.AUTH_METHOD = 'oidc'
        redirect_resp = views.user.user_register_interface()
        self.assertEqual(HomeURI.uri(), redirect_resp.location)

    def test_user_account_interface(self):
        redirect_resp = views.user.user_account_interface()
        self.assertEqual(302, redirect_resp.status_code)
        self.assertIn(UserLoginInterfaceURI.uri(), redirect_resp.location)
        self.assertFalse(current_user.is_authenticated)

        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        self.assertTrue(current_user.is_authenticated)
        self.assertIn('Modify your account settings', views.user.user_account_interface())
