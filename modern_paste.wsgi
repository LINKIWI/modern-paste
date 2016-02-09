import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
sys.path.insert(0, os.path.join(here, 'app'))
from modern_paste import app as application
