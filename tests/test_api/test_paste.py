# coding=utf-8

import json
import random
import time

import mock
from sqlalchemy.exc import SQLAlchemyError

import config
import constants.api
import database.attachment
import database.paste
import database.user
import util.cryptography
import util.string
import util.testing
from uri.authentication import *
from uri.main import *
from uri.paste import *


class TestPaste(util.testing.DatabaseTestCase):
    def test_submit_paste_invalid(self):
        # Invalid input
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.INCOMPLETE_PARAMS_FAILURE_CODE)
        self.assertEqual(json.loads(resp.data), constants.api.INCOMPLETE_PARAMS_FAILURE)

    def test_submit_paste_login_required(self):
        # Config requires authentication to post paste
        config.REQUIRE_LOGIN_TO_PASTE = True
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'paste',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.UNAUTHENTICATED_PASTES_DISABLED_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.UNAUTHENTICATED_PASTES_DISABLED_FAILURE, json.loads(resp.data))

        user = util.testing.UserFactory.generate()
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'paste',
                'api_key': user.api_key,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)

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
        self.assertIsNotNone(resp_data['deactivation_token'])

        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'contents',
                'user_id': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        resp_data = json.loads(resp.data)
        self.assertIsNotNone(resp_data['post_time'])
        self.assertIsNotNone(resp_data['paste_id_repr'])
        self.assertTrue(resp_data['is_active'])
        self.assertEquals('contents', resp_data['contents'])
        self.assertIsNone(database.paste.get_paste_by_id(1).user_id)

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
        self.assertIsNotNone(resp_data['deactivation_token'])
        self.assertEqual(user.user_id, database.paste.get_paste_by_id(util.cryptography.get_decid(resp_data['paste_id_repr'])).user_id)

    def test_submit_paste_api_post(self):
        # Ensure that the is_api_post flag is appropriately set
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'contents',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        paste_id = util.cryptography.get_decid(json.loads(resp.data)['paste_id_repr'], force=True)
        self.assertTrue(database.paste.get_paste_by_id(paste_id).is_api_post)

    def test_submit_paste_non_api_post(self):
        for referrer in [PastePostInterfaceURI.full_uri(), HomeURI.full_uri(), PastePostInterfaceURI.full_uri() + '/?extra=stuff']:
            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                }),
                content_type='application/json',
                headers={
                    'referer': referrer,  # TIL "referer" is a deliberate misspelling of "referrer"
                },
            )
            self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
            paste_id = util.cryptography.get_decid(json.loads(resp.data)['paste_id_repr'], force=True)
            self.assertFalse(database.paste.get_paste_by_id(paste_id).is_api_post)

    def test_submit_paste_non_ascii(self):
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': '어머',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)

        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': json.loads(resp.data)['paste_id_repr'],
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertEqual(json.loads(resp.data)['details']['contents'], unicode('어머', 'utf8'))

    def test_submit_paste_attachments_disabled(self):
        config.ENABLE_PASTE_ATTACHMENTS = False
        resp = self.client.post(
            PasteSubmitURI.uri(),
            data=json.dumps({
                'contents': 'contents',
                'attachments': [
                    {
                        'name': 'file name',
                        'size': 12345,
                        'mime_type': 'image/png',
                        'data': 'binary data',
                    }
                ]
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.PASTE_ATTACHMENTS_DISABLED_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.PASTE_ATTACHMENTS_DISABLED_FAILURE, json.loads(resp.data))

    def test_submit_paste_with_attachments(self):
        with mock.patch.object(database.attachment, '_store_attachment_file') as mock_store_attachment_file:
            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                    'attachments': [
                        {
                            'name': 'file name',
                            'size': 12345,
                            'mime_type': 'image/png',
                            'data': 'binary data',
                        },
                        {
                            'name': 'file name 2',
                            'size': 12345,
                            'mime_type': 'image/png',
                            'data': 'binary data 2',
                        }
                    ]
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
            self.assertEqual(2, mock_store_attachment_file.call_count)

            resp_data = json.loads(resp.data)
            self.assertEqual('file_name', resp_data['attachments'][0]['name'])
            self.assertEqual(12345, resp_data['attachments'][0]['size'])
            self.assertEqual('image/png', resp_data['attachments'][0]['mime_type'])
            self.assertIsNotNone(database.attachment.get_attachment_by_name(
                util.cryptography.get_decid(resp_data['paste_id_repr']),
                'file_name')
            )
            self.assertEqual('file_name_2', resp_data['attachments'][1]['name'])
            self.assertEqual(12345, resp_data['attachments'][1]['size'])
            self.assertEqual('image/png', resp_data['attachments'][1]['mime_type'])
            self.assertIsNotNone(database.attachment.get_attachment_by_name(
                util.cryptography.get_decid(resp_data['paste_id_repr']),
                'file_name_2')
            )

    def test_submit_paste_invalid_attachments(self):
        with mock.patch.object(database.attachment, '_store_attachment_file') as mock_store_attachment_file:
            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                    'attachments': [
                        {
                            'name': 'file name',
                        }
                    ]
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
            self.assertEqual(1, mock_store_attachment_file.call_count)

    def test_submit_paste_too_large(self):
        config.MAX_ATTACHMENT_SIZE = 10.0 / (1000 * 1000)  # 10 B
        with mock.patch.object(database.attachment, '_store_attachment_file'):
            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                    'attachments': [
                        {
                            'name': 'file name',
                            'size': 12345,
                            'mime_type': 'image/png',
                            'data': util.string.random_alphanumeric_string(length=20),
                        },
                    ]
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.PASTE_ATTACHMENT_TOO_LARGE_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.PASTE_ATTACHMENT_TOO_LARGE_FAILURE, json.loads(resp.data))

            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                    'attachments': [
                        {
                            'name': 'file name',
                            'size': 12345,
                            'mime_type': 'image/png',
                            'data': util.string.random_alphanumeric_string(length=5),
                        },
                    ]
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)

    def test_submit_paste_base64_size_threshold(self):
        config.MAX_ATTACHMENT_SIZE = 3.0 / (1000 * 1000)  # 3 B
        with mock.patch.object(database.attachment, '_store_attachment_file'):
            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                    'attachments': [
                        {
                            'name': 'file name',
                            'size': 12345,
                            'mime_type': 'image/png',
                            'data': util.string.random_alphanumeric_string(length=5),
                        },
                    ]
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.PASTE_ATTACHMENT_TOO_LARGE_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.PASTE_ATTACHMENT_TOO_LARGE_FAILURE, json.loads(resp.data))

            resp = self.client.post(
                PasteSubmitURI.uri(),
                data=json.dumps({
                    'contents': 'contents',
                    'attachments': [
                        {
                            'name': 'file name',
                            'size': 12345,
                            'mime_type': 'image/png',
                            'data': util.string.random_alphanumeric_string(length=4),
                        },
                    ]
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)

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
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
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
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertFalse(database.paste.get_paste_by_id(paste.paste_id).is_active)

    def test_deactivate_paste_api_key(self):
        # Deactivate paste by authentication via an API key
        user = util.testing.UserFactory.generate()
        paste = util.testing.PasteFactory.generate(user_id=user.user_id)
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'api_key': user.api_key,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertFalse(database.paste.get_paste_by_id(paste.paste_id).is_active)

    def test_deactivate_paste_token(self):
        # Deactivate paste using deactivation token
        paste = util.testing.PasteFactory.generate()
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'deactivation_token': 'invalid',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'deactivation_token': paste.deactivation_token,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertFalse(database.paste.get_paste_by_id(paste.paste_id).is_active)

    def test_deactivate_paste_already_deactivated(self):
        # Deactivate paste using deactivation token
        paste = util.testing.PasteFactory.generate()
        database.paste.deactivate_paste(paste.paste_id)
        resp = self.client.post(
            PasteDeactivateURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'deactivation_token': paste.deactivation_token,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE, json.loads(resp.data))

    def test_deactivate_paste_server_error(self):
        with mock.patch.object(database.paste, 'deactivate_paste', side_effect=SQLAlchemyError):
            paste = util.testing.PasteFactory.generate()
            resp = self.client.post(
                PasteDeactivateURI.uri(),
                data=json.dumps({
                    'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                    'deactivation_token': paste.deactivation_token,
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)

    def test_set_paste_password(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        paste = util.testing.PasteFactory.generate(user_id=user.user_id)
        old_password_hash = paste.password_hash
        resp = self.client.post(
            PasteSetPasswordURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertNotEqual(database.paste.get_paste_by_id(paste.paste_id).password_hash, old_password_hash)

    def test_set_paste_password_unauth(self):
        # Modifying your own paste without authorization
        user = util.testing.UserFactory.generate(username='username', password='password')
        paste = util.testing.PasteFactory.generate(user_id=user.user_id)
        resp = self.client.post(
            PasteSetPasswordURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp.status_code)
        self.assertEqual('auth_failure', json.loads(resp.data)[constants.api.FAILURE])

    def test_set_paste_password_invalid_auth(self):
        # Modifying someone else's paste
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        paste = util.testing.PasteFactory.generate(user_id=user.user_id + 1)
        resp = self.client.post(
            PasteSetPasswordURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp.status_code)
        self.assertEqual('auth_failure', json.loads(resp.data)[constants.api.FAILURE])

    def test_set_paste_password_nonexistent(self):
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            PasteSetPasswordURI.uri(),
            data=json.dumps({
                'paste_id': -1,
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE, json.loads(resp.data))

    def test_add_paste_password(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        paste = util.testing.PasteFactory.generate(user_id=user.user_id, password=None)
        self.assertIsNone(paste.password_hash)
        resp = self.client.post(
            PasteSetPasswordURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertIsNotNone(database.paste.get_paste_by_id(paste.paste_id).password_hash)

    def test_remove_paste_password(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        paste = util.testing.PasteFactory.generate(user_id=user.user_id, password='password')
        self.assertIsNotNone(paste.password_hash)
        resp = self.client.post(
            PasteSetPasswordURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': None,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertIsNone(database.paste.get_paste_by_id(paste.paste_id).password_hash)

    def test_set_paste_password_server_error(self):
        with mock.patch.object(database.paste, 'set_paste_password', side_effect=SQLAlchemyError):
            user = util.testing.UserFactory.generate(username='username', password='password')
            self.api_login_user('username', 'password')
            paste = util.testing.PasteFactory.generate(user_id=user.user_id)
            resp = self.client.post(
                PasteSetPasswordURI.uri(),
                data=json.dumps({
                    'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                    'password': 'password',
                }),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

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
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        paste_details = database.paste.get_paste_by_id(paste.paste_id).as_dict()
        paste_details['poster_username'] = 'username'
        paste_details['attachments'] = []
        self.assertEqual(paste_details, json.loads(resp.data)['details'])

    def test_paste_details_password(self):
        user = util.testing.UserFactory.generate(username='username')
        paste = util.testing.PasteFactory.generate(password='None', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        paste = util.testing.PasteFactory.generate(password='password', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        paste = util.testing.PasteFactory.generate(password='password', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': 'invalid',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.AUTH_FAILURE_CODE)

        paste = util.testing.PasteFactory.generate(password='password', user_id=user.user_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                'password': 'password',
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        paste_details = database.paste.get_paste_by_id(paste.paste_id).as_dict()
        paste_details['poster_username'] = 'username'
        paste_details['attachments'] = []
        self.assertEqual(paste_details, json.loads(resp.data)['details'])

    def test_paste_details_anonymous(self):
        paste = util.testing.PasteFactory.generate(password=None, user_id=None)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
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
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE, json.loads(resp.data))

    def test_paste_details_nonexistent(self):
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(1),
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE, json.loads(resp.data))

    def test_paste_details_inactive(self):
        paste = util.testing.PasteFactory.generate(password=None, user_id=None)
        database.paste.deactivate_paste(paste.paste_id)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE, json.loads(resp.data))

    def test_paste_details_expired(self):
        paste = util.testing.PasteFactory.generate(password=None, user_id=None, expiry_time=int(time.time()) - 1000)
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.NONEXISTENT_PASTE_FAILURE, json.loads(resp.data))

    def test_paste_details_with_attachments(self):
        paste = util.testing.PasteFactory.generate(password=None, user_id=None)
        attachments = [
            util.testing.AttachmentFactory.generate(paste_id=paste.paste_id).as_dict()
            for _ in range(5)
        ]
        resp = self.client.post(
            PasteDetailsURI.uri(),
            data=json.dumps({
                'paste_id': util.cryptography.get_id_repr(paste.paste_id),
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual(5, len(json.loads(resp.data)['details']['attachments']))
        for attachment in attachments:
            self.assertIn(attachment, json.loads(resp.data)['details']['attachments'])

    def test_paste_details_server_error(self):
        with mock.patch.object(database.paste, 'get_paste_by_id', side_effect=SQLAlchemyError):
            paste = util.testing.PasteFactory.generate(password=None)
            resp = self.client.post(
                PasteDetailsURI.uri(),
                data=json.dumps({
                    'paste_id': util.cryptography.get_id_repr(paste.paste_id),
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)

    def test_pastes_for_user_unauthorized(self):
        resp = self.client.post(
            PastesForUserURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.AUTH_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.AUTH_FAILURE, json.loads(resp.data))

    def test_pastes_for_user_empty(self):
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        resp = self.client.post(
            PastesForUserURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual([], json.loads(resp.data)['pastes'])

    def test_pastes_for_user_no_inactive(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        pastes = [util.testing.PasteFactory.generate(user_id=user.user_id).as_dict() for i in range(10)]
        [database.paste.deactivate_paste(util.cryptography.get_decid(paste['paste_id_repr'], force=True)) for paste in pastes]
        resp = self.client.post(
            PastesForUserURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual(0, len(json.loads(resp.data)['pastes']))

    def test_pastes_for_user_valid(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        pastes = [util.testing.PasteFactory.generate(user_id=user.user_id).as_dict() for i in range(10)]
        resp = self.client.post(
            PastesForUserURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual(len(pastes), len(json.loads(resp.data)['pastes']))
        for paste in json.loads(resp.data)['pastes']:
            self.assertIn(paste, pastes)

    def test_pastes_for_user_server_error(self):
        user = util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        for i in range(3):
            util.testing.PasteFactory.generate(user_id=user.user_id)
        with mock.patch.object(database.paste, 'get_all_pastes_for_user', side_effect=SQLAlchemyError):
            resp = self.client.post(
                PastesForUserURI.uri(),
                data=json.dumps({}),
                content_type='application/json',
            )
            self.assertEqual(constants.api.UNDEFINED_FAILURE_CODE, resp.status_code)
            self.assertEqual(constants.api.UNDEFINED_FAILURE, json.loads(resp.data))

    def test_recent_pastes_invalid(self):
        resp = self.client.post(
            RecentPastesURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

        resp = self.client.post(
            RecentPastesURI.uri(),
            data=json.dumps({
                'page_num': 0,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

    def test_recent_pastes_no_results(self):
        resp = self.client.post(
            RecentPastesURI.uri(),
            data=json.dumps({
                'page_num': 0,
                'num_per_page': 5,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual([], json.loads(resp.data)['pastes'])

        resp = self.client.post(
            RecentPastesURI.uri(),
            data=json.dumps({
                'page_num': 3,
                'num_per_page': 5,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual([], json.loads(resp.data)['pastes'])

    def test_recent_pastes_results(self):
        pastes = []
        for i in range(15):
            with mock.patch.object(time, 'time', return_value=time.time() + random.randint(-10000, 10000)):
                pastes.append(util.testing.PasteFactory.generate(expiry_time=None))
        recent_pastes_sorted = map(
            lambda paste: paste.as_dict(),
            sorted(pastes, key=lambda paste: paste.post_time, reverse=True),
        )

        resp = self.client.post(
            RecentPastesURI.uri(),
            data=json.dumps({
                'page_num': 0,
                'num_per_page': 5,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual(recent_pastes_sorted[0:5], json.loads(resp.data)['pastes'])

    def test_top_pastes_invalid(self):
        resp = self.client.post(
            TopPastesURI.uri(),
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

        resp = self.client.post(
            TopPastesURI.uri(),
            data=json.dumps({
                'page_num': 0,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE_CODE, resp.status_code)
        self.assertEqual(constants.api.INCOMPLETE_PARAMS_FAILURE, json.loads(resp.data))

    def test_top_pastes_no_results(self):
        resp = self.client.post(
            TopPastesURI.uri(),
            data=json.dumps({
                'page_num': 0,
                'num_per_page': 5,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual([], json.loads(resp.data)['pastes'])

        resp = self.client.post(
            TopPastesURI.uri(),
            data=json.dumps({
                'page_num': 3,
                'num_per_page': 5,
            }),
            content_type='application/json',
        )
        self.assertEqual(constants.api.SUCCESS_CODE, resp.status_code)
        self.assertEqual([], json.loads(resp.data)['pastes'])

    def test_recent_pastes_server_error(self):
        with mock.patch.object(database.paste, 'get_recent_pastes', side_effect=SQLAlchemyError):
            resp = self.client.post(
                RecentPastesURI.uri(),
                data=json.dumps({
                    'page_num': 0,
                    'num_per_page': 5,
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)

    def test_top_pastes_results(self):
        pastes = [util.testing.PasteFactory.generate() for i in range(15)]
        for paste in pastes:
            for i in range(random.randint(0, 50)):
                database.paste.increment_paste_views(paste.paste_id)

        for page_num in range(3):
            resp = self.client.post(
                TopPastesURI.uri(),
                data=json.dumps({
                    'page_num': page_num,
                    'num_per_page': 5,
                }),
                content_type='application/json',
            )
            self.assertEqual(5, len(json.loads(resp.data)['pastes']))
            for i in range(4):
                self.assertGreaterEqual(
                    json.loads(resp.data)['pastes'][i]['views'],
                    json.loads(resp.data)['pastes'][i + 1]['views']
                )

        resp = self.client.post(
            TopPastesURI.uri(),
            data=json.dumps({
                'page_num': 3,
                'num_per_page': 5,
            }),
            content_type='application/json',
        )
        self.assertEqual([], json.loads(resp.data)['pastes'])

    def test_top_pastes_server_error(self):
        with mock.patch.object(database.paste, 'get_top_pastes', side_effect=SQLAlchemyError):
            resp = self.client.post(
                TopPastesURI.uri(),
                data=json.dumps({
                    'page_num': 0,
                    'num_per_page': 5,
                }),
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, constants.api.UNDEFINED_FAILURE_CODE)
            self.assertEqual(json.loads(resp.data), constants.api.UNDEFINED_FAILURE)
