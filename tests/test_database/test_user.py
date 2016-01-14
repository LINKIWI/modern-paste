from util.exception import *

import util.testing
import util.cryptography
import database.user


class TestUser(util.testing.DatabaseTestCase):
    def test_user_properties(self):
        user = util.testing.UserFactory.generate()
        self.assertEqual(unicode(user.user_id), user.get_id())
        self.assertTrue(user.is_authenticated())
        self.assertFalse(user.is_anonymous())

    def test_create_new_user(self):
        database.user.create_new_user('username', 'password', '127.0.0.1', 'name', 'test@test.com')
        self.assertRaises(
            UsernameNotAvailableException,
            database.user.create_new_user,
            'username',
            'password',
            '127.0.0.1',
        )
        self.assertRaises(
            InvalidEmailException,
            database.user.create_new_user,
            'username2',
            'password',
            '127.0.0.1',
            email='invalid',
        )
        self.assertEqual(
            database.user.create_new_user('username3', 'password', '127.0.0.1', 'name', 'test@test.com'),
            database.user.get_user_by_username('username3')
        )

    def test_get_user_by_id(self):
        self.assertRaises(
            UserDoesNotExistException,
            database.user.get_user_by_id,
            1,
        )
        database.user.create_new_user('username', 'password', '127.0.0.1', 'name', 'test@test.com')
        user = database.user.get_user_by_id(1)
        self.assertEqual('username', user.username)
        self.assertEqual(util.cryptography.secure_hash('password'), user.password_hash)
        self.assertEqual('127.0.0.1', user.signup_ip)
        self.assertEqual('name', user.name)
        self.assertEqual('test@test.com', user.email)

    def test_get_user_by_username(self):
        self.assertRaises(
            UserDoesNotExistException,
            database.user.get_user_by_username,
            'username',
        )
        database.user.create_new_user('username', 'password', '127.0.0.1', 'name', 'test@test.com')
        user = database.user.get_user_by_username('username')
        self.assertEqual('username', user.username)
        self.assertEqual(util.cryptography.secure_hash('password'), user.password_hash)
        self.assertEqual('127.0.0.1', user.signup_ip)
        self.assertEqual('name', user.name)
        self.assertEqual('test@test.com', user.email)
        self.assertEqual(user, database.user.get_user_by_username('uSeRnAME'))

    def test_get_user_by_api_key(self):
        self.assertRaises(
            UserDoesNotExistException,
            database.user.get_user_by_api_key,
            'api key',
        )
        generated_user = database.user.create_new_user('username', 'password', '127.0.0.1', 'name', 'test@test.com')
        user = database.user.get_user_by_api_key(generated_user.api_key)
        self.assertEqual('username', user.username)
        self.assertEqual(util.cryptography.secure_hash('password'), user.password_hash)
        self.assertEqual('127.0.0.1', user.signup_ip)
        self.assertEqual('name', user.name)
        self.assertEqual('test@test.com', user.email)

    def test_generate_new_api_key(self):
        user = util.testing.UserFactory.generate()
        old_api_key = str(user.api_key)
        self.assertIsNotNone(old_api_key)
        user_api_key_modified = database.user.generate_new_api_key(user.user_id)
        self.assertNotEqual(old_api_key, user_api_key_modified.api_key)
        self.assertNotEqual(old_api_key, database.user.get_user_by_id(user.user_id).api_key)

    def test_authenticate_user(self):
        self.assertRaises(
            UserDoesNotExistException,
            database.user.authenticate_user,
            'username',
            'password',
        )
        util.testing.UserFactory.generate(username='username', password='password')
        self.assertTrue(database.user.authenticate_user('username', 'password'))
        self.assertTrue(database.user.authenticate_user('userNAME', 'password'))
        self.assertTrue(database.user.authenticate_user('uSeRnAME', 'password'))

    def test_deactivate_user(self):
        util.testing.UserFactory.generate()
        self.assertTrue(database.user.get_user_by_id(1).is_active)
        database.user.deactivate_user(1)
        self.assertFalse(database.user.get_user_by_id(1).is_active)

    def test_is_username_available(self):
        self.assertTrue(database.user.is_username_available('username'))
        self.assertTrue(database.user.is_username_available('Username'))
        self.assertTrue(database.user.is_username_available('UsErNAME'))
        database.user.create_new_user('username', 'password', '127.0.0.1', 'name', 'test@test.com')
        for username in ['username', 'Username', 'UsErNAME']:
            self.assertFalse(database.user.is_username_available(username))

    def test_is_email_address_valid(self):
        self.assertTrue(database.user.is_email_address_valid('test@test.com'))
        self.assertTrue(database.user.is_email_address_valid('test@test.co.uk'))
        self.assertTrue(database.user.is_email_address_valid('test+234@test.com'))
        self.assertFalse(database.user.is_email_address_valid('qwerty'))
        self.assertFalse(database.user.is_email_address_valid('test.com'))
        self.assertFalse(database.user.is_email_address_valid('test@@test.com'))
        self.assertFalse(database.user.is_email_address_valid('test@testcom'))
        self.assertFalse(database.user.is_email_address_valid('@test.com'))

    def test_load_user(self):
        self.assertIsNone(database.user.load_user(1))
        database.user.create_new_user('username', 'password', '127.0.0.1', 'name', 'test@test.com')
        user = database.user.load_user(1)
        self.assertEqual('username', user.username)
        self.assertEqual(util.cryptography.secure_hash('password'), user.password_hash)
        self.assertEqual('127.0.0.1', user.signup_ip)
        self.assertEqual('name', user.name)
        self.assertEqual('test@test.com', user.email)
