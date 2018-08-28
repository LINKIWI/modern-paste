import constants


# Domain from which you will access this app
# If running on a port other than 80, append it after a colon at the end of the domain, e.g. 'domain.com:8080'
DOMAIN = 'example.com'

# Use HTTPS by default?
# This is only used for deciding whether to use the http:// or https:// prefix when constructing full URLs,
# and is not related to your web server configuration.
DEFAULT_HTTPS = True

# The type of build environment
# build_environment.DEV won't minify CSS and Closure-compile JavaScript; build_environment.PROD will.
# Dev and prod environments also use separate databases, modern_paste_dev and modern_paste, respectively.
BUILD_ENVIRONMENT = constants.build_environment.PROD

# Option to use encrypted IDs rather than integer IDs
# Set this to True if you want paste IDs to be encrypted, e.g. displayed as h0GZ19np17iT~CtpuIH3NcnRi-rYnlYzizqToCmG3BY=
# If False, IDs will be displayed as regular, incrementing integers, e.g. 1, 2, 3, etc.
USE_ENCRYPTED_IDS = False

# Choose to allow paste attachments
# This will allow for users to attach files and images to pastes. If disabled, the MAX_ATTACHMENT_SIZE and
# ATTACHMENTS_DIR configuration constants will be ignored.
ENABLE_PASTE_ATTACHMENTS = True

# Allow only paste attachments below a certain size threshold, in MB
# Set this to 0 for an unlimited file size.
MAX_ATTACHMENT_SIZE = 0

# Location to store paste attachments
# Please use an absolute path and ensure that it is writable by www-data.
# For Google Cloud Storage, this should be relative to your bucket
ATTACHMENTS_DIR = '/var/www/modern-paste-attachments'

# Google Cloud Storage bucket
# Set to True if you're using Cloud Storage
USE_CLOUD_STORAGE = False

# Database host
# Optionally change the host on which the MySQL server is running; defaults to the same server hosting the site.
# For Google App Engine testing, this is used by dev_appserver and should point to the cloud sql proxy
DATABASE_HOST = 'localhost'

# Database name
# It's suggested you leave this as default.
# IMPORTANT NOTE: You must create this database yourself before running this app.
DATABASE_NAME = 'modern_paste'

# Cloud SQL Instance Connection name
# This is only relevant for Google App Engine deployments. Insert the instance connection name of your database from the console here. If you are using App Engine without Cloud SQL, leave this blank
DATABASE_INSTANCE_CONNECTION_NAME = 'my-project:my-location:my-instance'

# Username and password for MySQL identity with R/W access to the DATABASE_NAME database.
# It's suggested you create a new user with permissions only on DATABASE_NAME.
# If you like, you can also use the 'root' identity.
# IMPORTANT NOTE: You must create this database user yourself (if it doesn't already exist) before running this app.
DATABASE_USER = 'modern_paste'
DATABASE_PASSWORD = 'U4bV96S7uchYnJv4WK4akKfzdqKhDFLOpfm0XspYkTF7gyJawhmpZnBi1KdAQNPqxqoUbNDZzuxX0LOgyMc2g8B2NS2j2Fib'

# Choose to enable or disable user registration
# If False, the web interface will not allow access to the user registration page. Additionally, the API endpoint
# for creating new users will respond with an error.
# This is useful for private or internal installations that aren't intended for public use.
ENABLE_USER_REGISTRATION = True

# Choose to require users to be logged in to post pastes
# If True, the web interface will allow access to the paste post interface only if the user is signed in. Additionally,
# the API endpoint for creating new pastes will respond with an error if not authenticated with an API key tied to an
# existing, active user.
# This is useful for private or internal installations that aren't intended for public use.
REQUIRE_LOGIN_TO_PASTE = False

# Choose to require users to be logged in to post attachments
# If True, the web interface will only allow users to add attachments if they are logged in
# This is useful to prevent abuse of attachments system
REQUIRE_LOGIN_TO_ATTACH = False

# AES key for generating encrypted IDs
# This is only relevant if USE_ENCRYPTED_IDS above is True. If not, this config parameter can be ignored.
# It is recommended, but not strictly required, for you to replace the string below with the output of os.urandom(32),
# so that the encrypted IDs generated for the app are specific to this installation.
ID_ENCRYPTION_KEY = '6\x80\x18\xdc\xcf \xad\x14U\xa7\x05X\x7f\x81\x01\xd5\x19i\xf3S;\xcaL\xcf\xe2\x8d\x82\x1a\x12\xd9}\x8c'

# AES iv for CBC block cipher operation, advice as per key gen above
ID_ENCRYPTION_IV = '1234567890123456'

# Flask session secret key
# IMPORTANT NOTE: Open up a Python terminal, and replace the below with the output of os.urandom(32)
# This secret key should be different for every installation of Modern Paste.
FLASK_SECRET_KEY = '\x90]\xd4SDI\xb9h\x89\x01\x9f\xa5\xd9\xa1\xb6\xf8]\xb5\x077\x1d\xceB^\x00+\xf2\xcfs\xef*\xa0'

# Languages
# A list of all languages you want to support with the app. Add 'text' for plain text support.
# Only use strings from the directory app/static/build/lib/codemirror/mode
LANGUAGES = [
    'text',
    'clike',
    'cmake',
    'coffeescript',
    'css',
    'diff',
    'fortran',
    'htmlmixed',
    'javascript',
    'jinja2',
    'markdown',
    'octave',
    'perl',
    'php',
    'python',
    'sass',
    'sql',
    'verilog',
    'vhdl',
    'xml',
    'yaml',
]
