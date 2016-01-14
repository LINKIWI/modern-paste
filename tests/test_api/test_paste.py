import json

import mock
from sqlalchemy.exc import SQLAlchemyError

import constants.api
import database.paste
import database.user
import util.testing
from uri.authentication import *
from uri.paste import *


class TestPaste(util.testing.DatabaseTestCase):
    def test_submit_paste_invalid_input(self):
        # Invalid input
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.INCOMPLETE_PARAMS_FAILURE)

    def test_submit_paste_auth_failure(self):
        # Needs authentication
        util.testing.UserFactory.generate(username='username', password='password')
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'user_id': 1,
                'contents': 'contents',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.AUTH_FAILURE)

        # Attempting to post with the wrong user ID
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, constants.api.SUCCESS_CODE)
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'user_id': 2,
                'contents': 'contents',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.AUTH_FAILURE)

    def test_submit_paste_no_auth(self):
        # Successful paste without authentication
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'contents',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        resp_data = json.loads(resp.data)
        self.assertIsNotNone(resp_data['post_time'])
        self.assertIsNotNone(resp_data['paste_id_repr'])
        self.assertTrue(resp_data['is_active'])
        self.assertEquals('contents', resp_data['contents'])

    def test_submit_paste_with_auth(self):
        # Successful paste with authentication
        util.testing.UserFactory.generate(username='username', password='password')
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, constants.api.SUCCESS_CODE)
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'user_id': 1,
                'contents': 'contents',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        resp_data = json.loads(resp.data)
        self.assertIsNotNone(resp_data['post_time'])
        self.assertIsNotNone(resp_data['paste_id_repr'])
        self.assertTrue(resp_data['is_active'])
        self.assertEquals('contents', resp_data['contents'])

    def test_submit_paste_logged_in(self):
        # Paste should automatically be associated with user who is logged in
        user = util.testing.UserFactory.generate(username='username', password='password')
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, constants.api.SUCCESS_CODE)
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'contents',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        resp_data = json.loads(resp.data)
        self.assertIsNotNone(resp_data['post_time'])
        self.assertIsNotNone(resp_data['paste_id_repr'])
        self.assertTrue(resp_data['is_active'])
        self.assertEquals('contents', resp_data['contents'])
        self.assertEqual(user.user_id, database.paste.get_paste_by_id(resp_data['paste_id_repr']).user_id)

    def test_submit_paste_server_error(self):
        with mock.patch.object(database.paste, 'create_new_paste', side_effect=SQLAlchemyError):
            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)

    def test_deactivate_paste_invalid(self):
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.INCOMPLETE_PARAMS_FAILURE)

        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': -1,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.NONEXISTENT_PASTE_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.NONEXISTENT_PASTE_FAILURE)

    def test_deactivate_paste_auth(self):
        # Deactivate paste by being authenticated and owning the paste
        user = util.testing.UserFactory.generate(username='username', password='password')
        paste = util.testing.PasteFactory.generate(user_id=user.user_id)
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': 'username',
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEquals(resp.status_code, constants.api.SUCCESS_CODE)
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertFalse(database.paste.get_paste_by_id(paste.paste_id).is_active)

    def test_deactivate_paste_token(self):
        # Deactivate paste using deactivation token
        paste = util.testing.PasteFactory.generate()
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
                'deactivation_token': 'invalid',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
                'deactivation_token': paste.deactivation_token,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertFalse(database.paste.get_paste_by_id(paste.paste_id).is_active)

    def test_deactivate_paste_server_error(self):
        with mock.patch.object(database.paste, 'deactivate_paste', side_effect=SQLAlchemyError):
            paste = util.testing.PasteFactory.generate()
            resp = self.client.post(
                PasteDeactivateURI.uri(),
                data=json.dumps({
                    'paste_id': paste.paste_id,
                    'deactivation_token': paste.deactivation_token,
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)

    def test_paste_details_invalid(self):
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.INCOMPLETE_PARAMS_FAILURE)

        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': -1,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.NONEXISTENT_PASTE_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.NONEXISTENT_PASTE_FAILURE)

    def test_paste_details_no_password(self):
        user = util.testing.UserFactory.generate(username='username')
        paste = util.testing.PasteFactory.generate(password=None, user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        paste_details = database.paste.get_paste_by_id(paste.paste_id).as_dict()
        paste_details['poster_username'] = 'username'
        self.assertEqual(paste_details, json.loads(resp.data)['details'])

    def test_paste_details_password(self):
        user = util.testing.UserFactory.generate(username='username')
        paste = util.testing.PasteFactory.generate(password='None', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        paste = util.testing.PasteFactory.generate(password='password', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        paste = util.testing.PasteFactory.generate(password='password', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
                'password': 'invalid',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        paste = util.testing.PasteFactory.generate(password='password', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        paste_details = database.paste.get_paste_by_id(paste.paste_id).as_dict()
        paste_details['poster_username'] = 'username'
        self.assertEqual(paste_details, json.loads(resp.data)['details'])

    def test_paste_details_anonymous(self):
        paste = util.testing.PasteFactory.generate(password=None, user_id=None)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual('Anonymous', json.loads(resp.data)['details']['poster_username'])

        user = util.testing.UserFactory.generate(username='username')
        paste = util.testing.PasteFactory.generate(password=None, user_id=user.user_id)
        database.user.deactivate_user(user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': paste.paste_id,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual('Anonymous', json.loads(resp.data)['details']['poster_username'])

    def test_paste_details_server_error(self):
        with mock.patch.object(database.paste, 'get_paste_by_id', side_effect=SQLAlchemyError):
            paste = util.testing.PasteFactory.generate(password=None)
            resp = self.client.post(
                PasteDetailsURI.uri(),
                data=json.dumps({
                    'paste_id': paste.paste_id,
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)
