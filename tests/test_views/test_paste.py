import flask

import database.paste
import util.cryptography
import util.testing
import views.paste


class TestPaste(util.testing.DatabaseTestCase):
    def test_paste_post(self):
        self.assertIsNotNone(views.paste.paste_post())

    def test_paste_view(self):
        self.assertIn('PASTE NOT FOUND', views.paste.paste_view(-1))

        paste = util.testing.PasteFactory.generate()
        self.assertIn(str(paste.paste_id), views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))
        self.assertIn(paste.language, views.paste.paste_view(util.cryptography.get_id_repr(paste.paste_id)))

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
