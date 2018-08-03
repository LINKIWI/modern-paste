import json

import mock
from sqlalchemy.exc import SQLAlchemyError

import config
import constants.api
import database.user
import util.testing
from uri.user import *
from uri.authentication import *


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

    def test_create_new_user_disabled(self):
        config.ENABLE_USER_REGISTRATION = False
        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.USER_REGISTRATION_DISABLED_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.USER_REGISTRATION_DISABLED_FAILURE, json.loads(resp.data))

    def test_create_new_user_non_local_auth(self):
        config.AUTH_METHOD = 'oidc'
        resp = self.client.post(
            UserCreateURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_METHOD_DISABLED_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.AUTH_METHOD_DISABLED_FAILURE, json.loads(resp.data))

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

    def test_create_new_user_server_error(self):
        with mock.patch.object(database.user, 'create_new_user', side_effect=SQLAlchemyError):
            resp = self.client.post(
                UserCreateURI.uri(),
                data=json.dumps({
                    'username': 'username',
                    'password': 'password',
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

    def test_update_user_details(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            UserUpdateDetailsURI.uri(),
            data=json.dumps({
                'name': 'name',
                'email': 'email@email.com',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual('name', database.user.get_user_by_id(user.user_id).name)
        self.assertEqual('email@email.com', database.user.get_user_by_id(user.user_id).email)
        self.assertTrue(database.user.authenticate_user('username', 'password'))

    def test_update_user_password(self):
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            UserUpdateDetailsURI.uri(),
            data=json.dumps({
                'current_password': 'password',
                'new_password': 'new_password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertFalse(database.user.authenticate_user('username', 'password'))
        self.assertTrue(database.user.authenticate_user('username', 'new_password'))

    def test_update_user_details_invalid_email(self):
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            UserUpdateDetailsURI.uri(),
            data=json.dumps({
                'name': 'name',
                'email': 'email',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual('invalid_email_failure', json.loads(resp.data)['failure'])

    def test_update_user_details_wrong_current_password(self):
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            UserUpdateDetailsURI.uri(),
            data=json.dumps({
                'current_password': 'invalid',
                'new_password': 'new_password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp.status_code)
        self.assertTrue(database.user.authenticate_user('username', 'password'))
        self.assertFalse(database.user.authenticate_user('username', 'invalid'))

    def test_remove_user_details(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            UserUpdateDetailsURI.uri(),
            data=json.dumps({
                'name': None,
                'email': None,
                'new_password': None,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertIsNone(database.user.get_user_by_id(user.user_id).name)
        self.assertIsNone(database.user.get_user_by_id(user.user_id).email)
        self.assertTrue(database.user.authenticate_user('username', 'password'))

    def test_update_user_details_server_error(self):
        with mock.patch.object(database.user, 'update_user_details', side_effect=SQLAlchemyError):
            util.testing.UserFactory.generate(username='username', password='password')
            self.api_login_user('username', 'password')
            resp = self.client.post(
                UserUpdateDetailsURI.uri(),
                data=json.dumps({
                    'name': None,
                    'email': None,
                    'new_password': None,
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

    def test_deactivate_user_not_logged_in(self):
        util.testing.UserFactory.generate()
        resp = self.client.post(
            UserDeactivateURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.AUTH_FAILURE, json.loads(resp.data))

    def test_deactivate_user_logged_in(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        resp = self.client.post(
            UserDeactivateURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertFalse(database.user.get_user_by_id(user.user_id).is_active)

    def test_deactivate_user_api_key(self):
        user = util.testing.UserFactory.generate()
        resp = self.client.post(
            UserDeactivateURI.uri(),
            data=json.dumps({
                'api_key': 'invalid',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.AUTH_FAILURE, json.loads(resp.data))
        resp = self.client.post(
            UserDeactivateURI.uri(),
            data=json.dumps({
                'api_key': user.api_key,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertFalse(database.user.get_user_by_id(user.user_id).is_active)

    def test_deactivate_user_server_error(self):
        with mock.patch.object(database.user, 'deactivate_user', side_effect=SQLAlchemyError):
            user = util.testing.UserFactory.generate()
            resp = self.client.post(
                UserDeactivateURI.uri(),
                data=json.dumps({
                    'api_key': user.api_key,
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

    def test_api_key_regenerate(self):
        old_api_key = util.testing.UserFactory.generate(username='username', password='password').api_key
        self.api_login_user('username', 'password')
        resp = self.client.post(
            UserAPIKeyRegenerateURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        new_key = json.loads(resp.data)['api_key']
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual(64, len(new_key))
        self.assertNotEqual(old_api_key, new_key)

    def test_api_key_regenerate_server_error(self):
        with mock.patch.object(database.user, 'generate_new_api_key', side_effect=SQLAlchemyError):
            util.testing.UserFactory.generate(username='username', password='password')
            self.api_login_user('username', 'password')
            resp = self.client.post(
                UserAPIKeyRegenerateURI.uri(),
                data=json.dumps({}),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

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

    def test_check_username_availability_server_error(self):
        with mock.patch.object(database.user, 'is_username_available', side_effect=SQLAlchemyError):
            resp = self.client.post(
                CheckUsernameAvailabilityURI.uri(),
                data=json.dumps({
                    'username': 'username',
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

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

    def test_validate_email_address_server_error(self):
        with mock.patch.object(database.user, 'is_email_address_valid', side_effect=SQLAlchemyError):
            resp = self.client.post(
                ValidateEmailAddressURI.uri(),
                data=json.dumps({
                    'email': 'test@test.com',
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))
