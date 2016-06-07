import StringIO
import base64
import time

import flask
import mock

import database.attachment
import database.paste
import util.cryptography
import util.testing
import views.paste


class TestPaste(util.testing.DatabaseTestCase):
    def test_paste_post(self):
        self.assertIsNotNone(views.paste.paste_post())
        util.testing.UserFactory.generate(username='username', password='password')
        self.api_login_user('username', 'password')
        self.assertIn('PASTE TITLE', views.paste.paste_post())

    def test_paste_view(self):
        self.assertIn('PASTE NOT FOUND', views.paste.paste_view(-1))

        paste = util.testing.PasteFactory.generate()
        database.paste.deactivate_paste(paste.paste_id)
        self.assertIn('PASTE NOT FOUND', views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))

        paste = util.testing.PasteFactory.generate(expiry_time=int(time.time()) - 1000)
        database.paste.deactivate_paste(paste.paste_id)
        self.assertIn('PASTE NOT FOUND', views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))

        paste = util.testing.PasteFactory.generate()
        # Deactivation token should appear on the first view of the paste
        self.assertIn(paste.deactivation_token, views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))
        # It should no longer appear on subsequent views
        self.assertNotIn(paste.deactivation_token, views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))
        self.assertIn(str(paste.paste_id), views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))
        self.assertIn(paste.language, views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))

        # Deactivation token should never appear if the paste was posted via the API interface
        paste = util.testing.PasteFactory.generate(is_api_post=True, title='Test title')
        self.assertNotIn(paste.deactivation_token, views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))

        # Ensure that the paste title is the window title
        self.assertIn('Test title - Modern Paste', views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))

    def test_paste_view_raw(self):
        # Non-existent paste
        self.assertEqual('This paste either does not exist or has been deleted.', views.paste.paste_view_raw(-1).data)

        # Password-protected, no password supplied
        paste = util.testing.PasteFactory.generate(password='password')
        self.assertIn(
            'In order to view the raw contents of a password-protected paste',
            views.paste.paste_view_raw(util.cryptography.get_id_repr(paste.paste_id)).data,
        )

        # Password-protected, wrong password supplied
        flask.request.args = {'password': 'invalid'}
        self.assertEqual(
            'The password you supplied for this paste is not correct.',
            views.paste.paste_view_raw(util.cryptography.get_id_repr(paste.paste_id)).data,
        )

        # Password-protected, correct password supplied
        flask.request.args = {'password': 'password'}
        self.assertEqual(paste.contents, views.paste.paste_view_raw(util.cryptography.get_id_repr(paste.paste_id)).data)

        # Deactivated paste
        database.paste.deactivate_paste(paste.paste_id)
        self.assertEqual(
            'This paste either does not exist or has been deleted.',
            views.paste.paste_view_raw(util.cryptography.get_id_repr(paste.paste_id)).data,
        )

    def test_paste_attachment(self):
        paste = util.testing.PasteFactory.generate()
        attachment = util.testing.AttachmentFactory.generate(paste_id=paste.paste_id)

        # Non-existent paste
        resp = views.paste.paste_attachment(util.cryptography.get_id_repr(10), attachment.file_name)
        self.assertIn(
            'No paste with the given ID could be found',
            resp[0],
        )
        self.assertEqual(404, resp[1])

        # Non-existent attachment file name
        resp = views.paste.paste_attachment(util.cryptography.get_id_repr(paste.paste_id), 'nonexistent')
        self.assertIn(
            'No attachment with the given file name could be found',
            resp[0]
        )
        self.assertEqual(404, resp[1])

        # Valid input
        with mock.patch('__builtin__.open') as mock_open:
            mock_file_obj = mock.Mock(spec=file, wraps=StringIO.StringIO(base64.b64encode('file contents')))
            mock_open.return_value = mock_file_obj

            resp = views.paste.paste_attachment(util.cryptography.get_id_repr(paste.paste_id), attachment.file_name)
            self.assertEqual(1, mock_open.call_count)
            self.assertIsNotNone(resp)
            self.assertEqual('file contents', resp.get_data())
            self.assertEqual(200, resp.status_code)

        # Undefined server error
        with mock.patch.object(database.attachment, 'get_attachment_by_name') as mock_get_attachment:
            mock_get_attachment.side_effect = Exception
            resp = views.paste.paste_attachment(util.cryptography.get_id_repr(paste.paste_id), attachment.file_name)
            self.assertIn(
                'Undefined error',
                resp[0],
            )
            self.assertEqual(500, resp[1])

    def test_paste_archive(self):
        self.assertIsNotNone(views.paste.paste_archive())
