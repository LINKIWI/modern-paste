import random
import time

import mock

import database.paste
import util.cryptography
import util.testing
from util.exception import *


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
        self.assertEqual('Untitled', paste.title)
        self.assertIsNone(paste.password_hash)
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

        paste = util.testing.PasteFactory.generate(expiry_time=int(time.time()) - 1000)
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

    def test_increment_paste_views(self):
        self.assertRaises(
            PasteDoesNotExistException,
            database.paste.increment_paste_views,
            paste_id=-1,
        )
        paste = util.testing.PasteFactory.generate()
        self.assertEqual(0, database.paste.get_paste_by_id(paste.paste_id).views)
        database.paste.increment_paste_views(paste.paste_id)
        self.assertEqual(1, database.paste.get_paste_by_id(paste.paste_id).views)
        for i in range(50):
            database.paste.increment_paste_views(paste.paste_id)
        self.assertEqual(51, database.paste.get_paste_by_id(paste.paste_id).views)

    def test_get_recent_pastes(self):
        pastes = []
        for i in range(15):
            with mock.patch.object(time, 'time', return_value=time.time() + random.randint(-10000, 10000)):
                pastes.append(util.testing.PasteFactory.generate(expiry_time=None))
        recent_pastes_sorted = sorted(pastes, key=lambda paste: paste.post_time, reverse=True)
        self.assertEqual(recent_pastes_sorted[0:5], database.paste.get_recent_pastes(0, 5))
        self.assertEqual(recent_pastes_sorted[5:10], database.paste.get_recent_pastes(1, 5))
        self.assertEqual(recent_pastes_sorted[10:15], database.paste.get_recent_pastes(2, 5))
        self.assertEqual([], database.paste.get_recent_pastes(3, 5))
        self.assertEqual([], database.paste.get_recent_pastes(4, 5))

    def test_get_top_pastes(self):
        pastes = [util.testing.PasteFactory.generate() for i in range(15)]
        for paste in pastes:
            for i in range(random.randint(0, 50)):
                database.paste.increment_paste_views(paste.paste_id)
        for page_num in [0, 1, 2]:
            top_pastes = database.paste.get_top_pastes(page_num, 5)
            for i in range(len(top_pastes) - 1):
                self.assertGreaterEqual(top_pastes[i].views, top_pastes[i + 1].views)
        self.assertEqual([], database.paste.get_top_pastes(3, 5))
        self.assertEqual([], database.paste.get_top_pastes(4, 5))

    def test_get_all_pastes_for_user(self):
        user = util.testing.UserFactory.generate()
        with mock.patch.object(time, 'time', return_value=time.time() + random.randint(-10000, 10000)):
            pastes = [util.testing.PasteFactory.generate(user_id=user.user_id) for i in range(30)]
            util.testing.PasteFactory.generate(user_id=user.user_id + 2)  # Generate pastes for a different user
        queried_pastes = database.paste.get_all_pastes_for_user(user.user_id)
        post_times = [paste.post_time for paste in queried_pastes]
        # Ensure pastes are sorted in reverse chronological order
        self.assertEqual(post_times, sorted(post_times, reverse=True))
        for paste in queried_pastes:
            self.assertIn(paste, pastes)
