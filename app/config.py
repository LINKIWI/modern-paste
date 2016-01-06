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
