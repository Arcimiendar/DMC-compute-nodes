import time
import base64
import uuid
from types import ModuleType
from importlib import import_module, invalidate_caches
import os
import contextlib
import pathlib

from logs import get_logger
from settings_loader import SettingsLoader
from algorithm_getters.storage.base_storage import BaseStorage

class_name = 'Base64Storage'
settings = SettingsLoader.get_instance()
logger = get_logger(__name__)


class Base64Storage(BaseStorage):
    def __init__(self):
        super(Base64Storage, self).__init__()
        current_work_directory = os.getcwd()
        self.temp_dir_path = os.path.join(current_work_directory, f'tmp{"".join(settings.service_id.split("-"))}')
        with contextlib.suppress(FileExistsError):
            os.mkdir(self.temp_dir_path)
        pathlib.Path(self.temp_dir_path, '__init__.py').touch(exist_ok=True)

    def get_module(self, filename: str) -> ModuleType:
        module_name = 't' + ''.join(str(uuid.uuid4()).split('-'))
        import_path = f'tmp{"".join(settings.service_id.split("-"))}.{module_name}'
        with open(os.path.join(self.temp_dir_path, module_name) + '.py', 'w') as f:
            f.write(base64.b64decode(filename).decode('utf8'))
        while True:
            try:
                invalidate_caches()
                return import_module(import_path)
            except ImportError:
                time.sleep(4)
                logger.info(os.system('ls {}'.format(self.temp_dir_path)))
                logger.info(import_path)
