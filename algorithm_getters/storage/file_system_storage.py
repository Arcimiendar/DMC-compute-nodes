import time
from types import ModuleType
from importlib import import_module, invalidate_caches
import os
import contextlib
import pathlib
import shutil

from logs import get_logger
from settings_loader import SettingsLoader
from algorithm_getters.storage.base_storage import BaseStorage

class_name = 'FileSystemStorage'
settings = SettingsLoader.get_instance()
logger = get_logger(__name__)


class FileSystemStorage(BaseStorage):
    def __init__(self):
        super(FileSystemStorage, self).__init__()
        current_work_directory = os.getcwd()
        self.temp_dir_path = os.path.join(current_work_directory, f'tmp{"".join(settings.service_id.split("-"))}')
        with contextlib.suppress(FileExistsError):
            os.mkdir(self.temp_dir_path)
        pathlib.Path(self.temp_dir_path, '__init__.py').touch(exist_ok=True)

    def get_module(self, filename: str) -> ModuleType:
        dir_location = settings.algorithm_storage_backend.config.directory
        file_path = os.path.join(dir_location, filename)
        if os.path.exists(file_path):
            shutil.copy(file_path, os.path.join(self.temp_dir_path, filename))
            module_name, _ = os.path.splitext(filename)
            import_path = f'tmp{"".join(settings.service_id.split("-"))}.{module_name}'
            while True:
                try:
                    invalidate_caches()
                    return import_module(import_path)
                except ImportError:
                    time.sleep(4)
                    logger.info(os.system('ls'))
                    logger.info(import_path)
