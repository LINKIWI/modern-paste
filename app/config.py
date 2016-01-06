from constants import build_environment


# Domain from which you will access this app.
# If running on a port other than 80, append it after a colon at the end of the domain, e.g. 'domain.com:8080'
DOMAIN = 'domain.com'

# Use HTTPS by default?
DEFAULT_HTTPS = True

# The type of build environment
# build_environment.DEV won't minify CSS and Closure-compile JavaScript; build_environment.PROD will.
# Dev and prod environments also use separate databases, modern_paste_dev and modern_paste, respectively.
BUILD_ENVIRONMENT = build_environment.DEV
