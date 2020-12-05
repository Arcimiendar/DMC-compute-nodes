import os

if os.environ.get('DEBUG'):
    from settings.settings import *  # put debug settings here
else:
    from settings.settings import *