import time

import util.string
from modern_paste import db


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_active = db.Column(db.Boolean)
    signup_time = db.Column(db.Integer)
    signup_ip = db.Column(db.Text)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.Text)
    name = db.Column(db.Text, default=None)
    email = db.Column(db.Text, default=None)
    api_key = db.Column(db.String(64), index=True)

    def __init__(
        self,
        signup_ip,
        username,
        password_hash,
        name,
        email,
    ):
        self.is_active = True
        self.signup_time = time.time()
        self.signup_ip = signup_ip
        self.username = username
        self.password_hash = password_hash
        self.name = name
        self.email = email
        self.api_key = util.string.random_alphanumeric_string(length=64)

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return unicode(self.user_id)
