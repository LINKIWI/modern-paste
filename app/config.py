import constants


# Domain from which you will access this app.
# If running on a port other than 80, append it after a colon at the end of the domain, e.g. 'domain.com:8080'
DOMAIN = 'domain.com'

# Use HTTPS by default?
DEFAULT_HTTPS = True

# The type of build environment
# build_environment.DEV won't minify CSS and Closure-compile JavaScript; build_environment.PROD will.
# Dev and prod environments also use separate databases, modern_paste_dev and modern_paste, respectively.
BUILD_ENVIRONMENT = constants.build_environment.DEV

# Option to use encrypted IDs rather than integer IDs
# Set this to True if you want paste IDs to be encrypted, e.g. displayed as h0GZ19np17iT~CtpuIH3NcnRi-rYnlYzizqToCmG3BY=
# If False, IDs will be displayed as regular, incrementing integers, e.g. 1, 2, 3, etc.
USE_ENCRYPTED_IDS = False

# Database name
# It's suggested you leave this as default.
# IMPORTANT NOTE: You must create this database yourself before running this app.
DATABASE_NAME = 'modern_paste'

# Username and password for MySQL identity with R/W access to the DATABASE_NAME database.
# It's suggested you create a new user with permissions only on DATABASE_NAME.
# If you like, you can also use the 'root' identity.
# IMPORTANT NOTE: You must create this database user yourself (if it doesn't already exist) before running this app.
DATABASE_USER = 'modern_paste'
DATABASE_PASSWORD = 'U4bV96S7uchYnJv4WK4akKfzdqKhDFLOpfm0XspYkTF7gyJawhmpZnBi1KdAQNPqxqoUbNDZzuxX0LOgyMc2g8B2NS2j2Fib'

# Languages
# A list of all languages you want to support with the app. Add 'text' for plain text support.
# Only use strings from the directory app/static/build/lib/codemirror/mode
LANGUAGES = [
    'text',
    'cmake',
    'coffeescript',
    'css',
    'diff',
    'fortran',
    'htmlmixed',
    'javascript',
    'jinja2',
    'markdown',
    'php',
    'sass',
    'sql',
    'verilog',
    'vhdl',
    'yaml',
]

# AES key for generating encrypted IDs
# This is only relevant if USE_ENCRYPTED_IDS above is True. If not, this config parameter can be ignored.
# It is recommended, but not strictly required, for you to replace the string below with the output of os.urandom(32),
# so that the encrypted IDs generated for the app are specific to this installation.
ID_ENCRYPTION_KEY = '6\x80\x18\xdc\xcf \xad\x14U\xa7\x05X\x7f\x81\x01\xd5\x19i\xf3S;\xcaL\xcf\xe2\x8d\x82\x1a\x12\xd9}\x8c'
