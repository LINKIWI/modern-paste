"""
Config parameters for the Flask app itself.
Nothing here is user-configurable; all config variables you can set yourself are in config.py.
Generally speaking, don't touch this file unless you know what you're doing.
"""

import config
import constants


# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql://{database_user}:{database_password}@localhost/{database_name}'.format(
    database_user=config.DATABASE_USER,
    database_password=config.DATABASE_PASSWORD,
    database_name=config.DATABASE_NAME if config.BUILD_ENVIRONMENT == constants.build_environment.PROD else config.DATABASE_NAME + '_dev',
)
SQLALCHEMY_TEST_DATABASE_URI = 'mysql://{database_user}:{database_password}@localhost/{database_name}'.format(
    database_user=config.DATABASE_USER,
    database_password=config.DATABASE_PASSWORD,
    database_name=config.DATABASE_NAME + '_test',
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask session secret key
SECRET_KEY = config.FLASK_SECRET_KEY
