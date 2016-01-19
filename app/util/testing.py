import json
import random
import time
import types

from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.testing import TestCase

import constants.api
import database.paste
import database.user
from modern_paste import app
from modern_paste import db
from uri.authentication import LoginUserURI
from uri.authentication import LogoutUserURI


def random_alphanumeric_string(length=64):
    """
    Generate a random alphanumeric string of the specified length.

    :param length: Length of the random string
    :return: A random string of length length containing only alphabetic and numeric characters
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    numbers = '0123456789'
    return ''.join([random.choice(list(alphabet) + list(alphabet.upper()) + list(numbers)) for i in range(length)])


class Factory:
    def __init__(self):
        pass

    @classmethod
    def random_or_specified_value(cls, value):
        """
        Helper utility for choosing between a user-specified value for a field or a randomly generated value.

        :param value: Either a lambda type or a non-lambda type.
        :return: The value itself if not a lambda type, otherwise the value of the evaluated lambda (random value)
        """
        return value() if isinstance(value, types.LambdaType) else value

    @classmethod
    def generate(cls, *args, **kwargs):
        """
        Generates an instance of the requested model and adds it to the test database.
        This method should be overrided by subclasses.

        :return: An instance of the model specified by the subclass type.
        """
        raise NotImplementedError


class UserFactory(Factory):
    @classmethod
    def generate(
        cls,
        username=lambda: random_alphanumeric_string(),
        password=lambda: random_alphanumeric_string(),
        signup_ip=lambda: '127.0.0.1',
        name=lambda: random_alphanumeric_string(),
        email=lambda: '{addr}@{domain}.com'.format(addr=random_alphanumeric_string(), domain=random_alphanumeric_string()),
    ):
        return database.user.create_new_user(
            username=cls.random_or_specified_value(username),
            password=cls.random_or_specified_value(password),
            signup_ip=cls.random_or_specified_value(signup_ip),
            name=cls.random_or_specified_value(name),
            email=cls.random_or_specified_value(email),
        )


class PasteFactory(Factory):
    @classmethod
    def generate(
        cls,
        user_id=lambda: random.getrandbits(16),
        contents=lambda: random_alphanumeric_string(length=8192),
        expiry_time=lambda: int(time.time() + random.getrandbits(16)),
        title=lambda: random_alphanumeric_string(),
        language=lambda: random.choice(['python', 'css', 'javascript', 'text']),
        password=lambda: random_alphanumeric_string(),
    ):
        return database.paste.create_new_paste(
            contents=cls.random_or_specified_value(contents),
            user_id=cls.random_or_specified_value(user_id),
            expiry_time=cls.random_or_specified_value(expiry_time),
            title=cls.random_or_specified_value(title),
            language=cls.random_or_specified_value(language),
            password=cls.random_or_specified_value(password),
        )


class DatabaseTestCase(TestCase):
    """
    Generic subclass of TestCase with Modern Paste-specific test environment initialization for database testing.
    """

    def create_app(self):
        """
        Initializes the test Flask application by setting the app config parameters appropriately.
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_TEST_DATABASE_URI']
        return app

    def setUp(self):
        """
        Initialize a test database environment.
        """
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        """
        Destroys the test database environment, resetting it to a clean state.
        """
        db.session.remove()
        db.drop_all()

    def api_login_user(self, username, password):
        """
        Logs in the specified user via the login API endpoint, and a hard login.

        :param username: Username of the user to log in.
        :param password: Password of the user to log in.
        """
        resp = self.client.post(
            LoginUserURI.uri(),
            data=json.dumps({
                'username': username,
                'password': password,
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        self.assertEqual(json.loads(resp.data)['username'], 'username')
        login_user(database.user.get_user_by_username(username))

    def api_logout_user(self):
        """
        Logs out the current user via the logout API endpoint, and a hard logout.
        """
        resp = self.client.post(LogoutUserURI.uri())
        self.assertEqual(resp.status_code, constants.api.SUCCESS_CODE)
        logout_user()
