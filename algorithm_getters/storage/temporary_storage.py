from types import ModuleType
from importlib import import_module
import os

from algorithm_getters.storage.base_storage import BaseStorage

class_name = 'TemporaryStorage'


class TemporaryStorage(BaseStorage):

    def get_module(self, filename: str) -> ModuleType:
        filename, _ = os.path.splitext(filename)
        return import_module('algorithm_getters.storage.temporary_algorithms.' + filename)
