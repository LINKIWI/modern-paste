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
        # Second valid login should also return success
        for i in range(2):
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

    def test_auth_status_logged_in(self):
        util.testing.UserFactory.generate(username='username', password='password')
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

        resp = self.client.post(
            AuthStatusURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertEqual(
            json.loads(resp.data),
            {
                'is_authenticated': True,
                'user_details': {
                    'username': 'username',
                    'user_id': 1,
                }
            },
        )

    def test_auth_status_logged_out(self):
        resp = self.client.post(
            AuthStatusURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertEqual(
            json.loads(resp.data),
            {
                'is_authenticated': False,
                'user_details': {
                    'username': None,
                    'user_id': None,
                }
            },
        )
