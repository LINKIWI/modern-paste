import re
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))

# This is not allowed on AppEngine (or the app_devserver)
if not re.match('(Google App Engine/)|(Development/)', os.getenv('SERVER_SOFTWARE', '')):
    os.chdir(here)

sys.path.insert(0, os.path.join(here, 'app'))
from modern_paste import app as application
