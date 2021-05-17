import unittest
from utils.error_context_handler_mixin import ErrorHandlerContextMixin
from settings_loader import SettingsLoader
import random
import time


class TestErrorContextHandlerMixin(unittest.TestCase):
    def test_tolerance_number(self):
        random.seed(int(time.time()))
        settings = SettingsLoader.get_instance()
        settings.error_policy.ignore_all = False
        settings.error_policy.tolerance_number = random.randint(5, 10)

        error_handler = ErrorHandlerContextMixin()
        for i in range(settings.error_policy.tolerance_number + 1):
            self.assertFalse(error_handler.stop_event.is_set())
            with error_handler.error_handler_context():
                raise ValueError
        self.assertTrue(error_handler.stop_event.is_set())

    def test_ignore_all(self):
        random.seed(int(time.time()))
        settings = SettingsLoader.get_instance()
        settings.error_policy.ignore_all = True
        settings.error_policy.tolerance_number = 0
        iterations = random.randint(5, 10)
        error_handler = ErrorHandlerContextMixin()
        for i in range(iterations):
            self.assertFalse(error_handler.stop_event.is_set())
            with error_handler.error_handler_context():
                raise ValueError
        self.assertFalse(error_handler.stop_event.is_set())
