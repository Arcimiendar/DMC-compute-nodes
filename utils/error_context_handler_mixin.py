from logs import get_logger
from contextlib import contextmanager
from settings_loader import SettingsLoader
import threading

logger = get_logger(__name__)
settings = SettingsLoader.get_instance()


class ErrorHandlerContextMixin:
    def __init__(self):
        self.error_number = 0
        self.stop_event = threading.Event()

    @contextmanager
    def error_handler_context(self):
        try:
            yield None
        except Exception as e:
            self.error_number += 1
            logger.exception(e)
            if not settings.error_policy.ignore_all and settings.error_policy.tolerance_number < self.error_number:
                self.stop_event.set()
