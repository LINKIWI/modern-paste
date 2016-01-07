import random
import time

from flask.ext.testing import TestCase

import database.user
import database.paste
from modern_paste import app
from modern_paste import db


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
    def generate(cls, *args, **kwargs):
        raise NotImplementedError


class UserFactory(Factory):
    @classmethod
    def generate(
        cls,
        username=random_alphanumeric_string(),
        password=random_alphanumeric_string(),
        signup_ip='127.0.0.1',
        name=random_alphanumeric_string(),
        email='{addr}@{domain}.com'.format(addr=random_alphanumeric_string(), domain=random_alphanumeric_string()),
    ):
        return database.user.create_new_user(username, password, signup_ip, name, email)


class PasteFactory(Factory):
    languages = ['python', 'java', 'html', 'css', 'javascript', 'matlab', 'text']

    @classmethod
    def generate(
        cls,
        user_id=random.getrandbits(16),
        contents=random_alphanumeric_string(length=8192),
        expiry_time=int(time.time() + random.getrandbits(16)),
        title=random_alphanumeric_string(),
        language=random.choice(languages),
        password=random_alphanumeric_string(),
    ):
        return database.paste.create_new_paste(contents, user_id, expiry_time, title, language, password)


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
        db.create_all()

    def tearDown(self):
        """
        Destroys the test database environment, resetting it to a clean state.
        """
        db.session.remove()
        db.drop_all()
