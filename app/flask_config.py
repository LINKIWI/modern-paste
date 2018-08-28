"""
Config parameters for the Flask app itself.
Nothing here is user-configurable; all config variables you can set yourself are in config.py.
Generally speaking, don't touch this file unless you know what you're doing.
"""

import config
import constants
import os

socket = ''
database_host = config.DATABASE_HOST

# Add the connection instance name if we're running in App Engine
if config.DATABASE_INSTANCE_CONNECTION_NAME != '' and \
   os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    socket = '?unix_socket=/cloudsql/{}'.format(config.DATABASE_INSTANCE_CONNECTION_NAME)
    database_host = ''

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql://{database_user}:{database_password}@{database_host}/{database_name}{socket}'.format(
    database_user=config.DATABASE_USER,
    database_password=config.DATABASE_PASSWORD,
    database_host=database_host,
    database_name=config.DATABASE_NAME if config.BUILD_ENVIRONMENT == constants.build_environment.PROD else config.DATABASE_NAME + '_dev',
    socket=socket
)

SQLALCHEMY_TEST_DATABASE_URI = 'mysql://{database_user}:{database_password}@{database_host}/{database_name}{socket}'.format(
    database_user=config.DATABASE_USER,
    database_password=config.DATABASE_PASSWORD,
    database_host=database_host,
    database_name=config.DATABASE_NAME + '_test',
    socket=socket
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask session cookie name
SESSION_COOKIE_NAME = 'modern-paste-session'

# Flask session secret key
SECRET_KEY = config.FLASK_SECRET_KEY
