import json

from flask_login import logout_user

import constants.api
import util.testing
from uri.main import *
from uri.authentication import *
from uri.user import *


class TestOIDCAuthentication(util.testing.OIDCTestCase):
    def test_login_oidc(self):
        # Assert that when OIDC says user is not logged in, they are not logged in
        self.user = None
        resp = self.client.get(
            HomeURI.uri(),
        )
        self.assertIn('ANONYMOUS', resp.data)

        # Assert that when OIDC says user is logged in, they are created and logged n
        self.has_id_token = True
        self.user = {'sub': 'testuser'}
        resp = self.client.get(
            HomeURI.uri(),
        )
        self.assertIn('TESTUSER', resp.data)

        # Use the code that retrieves a user if it already existed
        logout_user()
        self.has_id_token = True
        self.user = {'sub': 'testuser'}
        resp = self.client.get(
            HomeURI.uri(),
        )
        self.assertIn('TESTUSER', resp.data)

    def test_login_oauth2(self):
        # Assert that when OIDC says user is not logged in, they are not logged in
        self.user = None
        resp = self.client.get(
            HomeURI.uri(),
        )
        self.assertIn('ANONYMOUS', resp.data)

        # Assert that when OIDC says token is invalid, an error is returned
        resp = self.client.get(
            HomeURI.uri(),
            headers={'Authorization': 'Bearer test1'},
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.AUTH_FAILURE)

        # Assert that when OIDC says token is valid, they are authed
        self.token_valid = True
        self.user = {'sub': 'testtoken'}
        resp = self.client.get(
            HomeURI.uri(),
            headers={'Authorization': 'Bearer test1'},
        )
        self.assertIn('TESTTOKEN', resp.data)

        # Use the code that retrieves a user if it already existed
        logout_user()
        self.token_valid = True
        self.user = {'sub': 'testtoken'}
        resp = self.client.get(
            HomeURI.uri(),
            headers={'Authorization': 'Bearer test1'},
        )
        self.assertIn('TESTTOKEN', resp.data)
