import unittest
import os
from settings_loader import SettingsLoader
from tests import *


if __name__ == '__main__':
    os.environ['SETTINGS'] = 'settings_loader/test_settings.json'
    SettingsLoader.get_instance().reload_settings()

    unittest.main()
