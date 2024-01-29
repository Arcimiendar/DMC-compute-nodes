import oci
import time
from types import ModuleType
from importlib import import_module, invalidate_caches
import os
import contextlib
import pathlib
import secrets

from logs import get_logger
from settings_loader import SettingsLoader
from algorithm_getters.storage.base_storage import BaseStorage

class_name = 'OCIStorage'
settings = SettingsLoader.get_instance()
logger = get_logger(__name__)


class OCIStorage(BaseStorage):
    def __init__(self):
        super(OCIStorage, self).__init__()
        current_work_directory = os.getcwd()
        self.temp_dir_path = os.path.join(current_work_directory, f'tmp{"".join(settings.service_id.split("-"))}')
        with contextlib.suppress(FileExistsError):
            os.mkdir(self.temp_dir_path)
        pathlib.Path(self.temp_dir_path, '__init__.py').touch(exist_ok=True)

    def get_module(self, filename: str) -> ModuleType:
        bucket = settings.algorithm_storage_backend.config.bucket
        namespace = settings.algorithm_storage_backend.config.namespace
        conf = oci.config.from_file('/project/oci.conf')
        client = oci.object_storage.ObjectStorageClient(config=conf)
        object = client.get_object(namespace, bucket, filename)
        module_name, _ = os.path.splitext(filename)
        module_name += '_' + secrets.token_urlsafe(7)

        with open(os.path.join(self.temp_dir_path, module_name + '.py'), 'w') as f:
            f.write(object.data.text)

        import_path = f'tmp{"".join(settings.service_id.split("-"))}.{module_name}'

        while True:
            try:
                invalidate_caches()
                return import_module(import_path)
            except ImportError:
                time.sleep(4)
                logger.info(os.system('ls {}'.format(self.temp_dir_path)))
                logger.info(import_path)
