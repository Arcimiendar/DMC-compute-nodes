from types import ModuleType
from importlib import import_module
import os
import sys

from settings_loader import SettingsLoader
from algorithm_getters.storage.base_storage import BaseStorage

class_name = 'FileSystemStorage'
settings = SettingsLoader.get_instance()


class FileSystemStorage(BaseStorage):

    def get_module(self, filename: str) -> ModuleType:
        dir_location = settings.algorithm_storage_backend.directory
        sys.path.append(dir_location)
        if os.path.exists(os.path.join(dir_location, filename)):
            filename, _ = os.path.splitext(filename)
            return import_module(filename)
