import json

import constants.api
import util.testing
from uri.user import *


class TestPaste(util.testing.DatabaseTestCase):
    def test_create_new_user_invalid_data(self):
        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

    def test_create_new_user_invalid_username(self):
        util.testing.UserFactory.generate(username='username')
        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual('username_not_available_failure', json.loads(resp.data)['failure'])

    def test_create_new_user_invalid_email(self):
        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
                'email': 'invalid',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual('invalid_email_failure', json.loads(resp.data)['failure'])
 
    def test_create_new_user_valid(self):
        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)

        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({
                'username': 'other_username',
                'password': 'password',
                'name': 'name',
                'email': 'test@test.com',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)

    def test_deactivate_user(self):
        # TODO
        pass

    def test_check_username_availability_invalid_data(self):
        resp = self.client.post(
            CheckUsernameAvailabilityURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

    def test_check_username_availability_available(self):
        resp = self.client.post(
            CheckUsernameAvailabilityURI.uri(),
            data=json.dumps({
                'username': 'username',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertTrue(json.loads(resp.data)['is_available'])

    def test_check_username_availability_unavailable(self):
        util.testing.UserFactory.generate(username='username')
        resp = self.client.post(
            CheckUsernameAvailabilityURI.uri(),
            data=json.dumps({
                'username': 'username',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertFalse(json.loads(resp.data)['is_available'])

        # Case-insensitivity
        resp = self.client.post(
            CheckUsernameAvailabilityURI.uri(),
            data=json.dumps({
                'username': 'useRNaME',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertFalse(json.loads(resp.data)['is_available'])

    def test_validate_email_address_invalid_data(self):
        resp = self.client.post(
            ValidateEmailAddressURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

    def test_validate_email_address_valid(self):
        for email in ['test@test.com', 'test@test.co.uk', 'test.test.test@test.a.b.s']:
            resp = self.client.post(
                ValidateEmailAddressURI.uri(),
                data=json.dumps({
                    'email': email,
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
            self.assertTrue(json.loads(resp.data)['is_valid'])

    def test_validate_email_address_invalid(self):
        for email in ['invalid', 'test@', 'test@', '@test.com', 'spaces in@address.com']:
            resp = self.client.post(
                ValidateEmailAddressURI.uri(),
                data=json.dumps({
                    'email': email,
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
            self.assertFalse(json.loads(resp.data)['is_valid'])
