import json

import constants.api
import util.testing
from uri.authentication import *


class TestAuthentication(util.testing.DatabaseTestCase):
    def test_login_logout_user(self):
        util.testing.UserFactory.generate(username='username', password='password')

        # Authentication failure
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'invalid password',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.AUTH_FAILURE)

        # Invalid data
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.INCOMPLETE_PARAMS_FAILURE)

        # Nonexistent user
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'invalid username',
                'password': 'invalid password',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.NONEXISTENT_USER_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.NONEXISTENT_USER_FAILURE)

        # Valid login
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertEqual(json.loads(resp.data)['username'], 'username')

        # Logout
        resp = self.client.post(LogoutUserURI.uri())
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertEqual(json.loads(resp.data)['username'], 'username')
