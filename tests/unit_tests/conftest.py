import os
import sys

os.environ["APP_ENV"] = "test"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
