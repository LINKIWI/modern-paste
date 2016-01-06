from flask.ext.testing import TestCase
from util.exception import *

import util.testing
import util.cryptography
import database.user


class TestUser(TestCase):
    def create_app(self):
        return util.testing.initialize_test_app()

    def setUp(self):
        util.testing.initialize_test_db_env()

    def tearDown(self):
        util.testing.destroy_test_db_env()

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
