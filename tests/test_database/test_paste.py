from util.exception import *

import util.testing
import util.cryptography
import database.paste


class TestPaste(util.testing.DatabaseTestCase):
    def test_create_new_paste(self):
        paste = database.paste.create_new_paste('contents', 1, 1452119965, 'title', 'python', 'password')
        self.assertEqual(1, paste.user_id)
        self.assertEqual('contents', paste.contents)
        self.assertEqual(1452119965, paste.expiry_time)
        self.assertEqual('title', paste.title)
        self.assertEqual('python', paste.language)
        self.assertEqual('python', paste.language)
        self.assertEqual(util.cryptography.secure_hash('password'), paste.password_hash)
        # Should also be able to create pastes with all optional fields blank
        paste = database.paste.create_new_paste('contents')
        self.assertEqual('text', paste.language)
        self.assertIsNone(paste.password_hash)
        self.assertIsNone(paste.title)
        self.assertIsNone(paste.user_id)
        self.assertIsNone(paste.expiry_time)

    def test_get_paste_by_id(self):
        self.assertRaises(
            PasteDoesNotExistException,
            database.paste.get_paste_by_id,
            -1,
        )
        paste = util.testing.PasteFactory.generate()
        self.assertEqual(paste, database.paste.get_paste_by_id(paste.paste_id))
        database.paste.deactivate_paste(paste.paste_id)
        self.assertEqual(paste, database.paste.get_paste_by_id(paste.paste_id))
        self.assertRaises(
            PasteDoesNotExistException,
            database.paste.get_paste_by_id,
            paste.paste_id,
            active_only=True,
        )

    def test_deactivate_paste(self):
        util.testing.PasteFactory.generate()
        self.assertTrue(database.paste.get_paste_by_id(1).is_active)
        database.paste.deactivate_paste(1)
        self.assertFalse(database.paste.get_paste_by_id(1).is_active)

    def test_get_all_pastes_for_user(self):
        user = util.testing.UserFactory.generate()
        pastes = [util.testing.PasteFactory.generate(user_id=user.user_id) for i in range(30)]
        for paste in database.paste.get_all_pastes_for_user(user.user_id):
            self.assertIn(paste, pastes)
