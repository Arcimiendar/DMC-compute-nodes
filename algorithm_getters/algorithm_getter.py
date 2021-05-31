from models.base_algorithm import BaseAlgorithm, Context
from models.base_data_balancer import BaseDataBalancer
from models.base_data_getter import BaseDataGetter
from models.base_data_saver import BaseDataSaver
from logs import get_logger
from settings_loader import SettingsLoader
from importlib import import_module
from algorithm_getters.storage.base_storage import BaseStorage
from typing import Type


settings = SettingsLoader.get_instance()
logger = get_logger(__name__)


class AlgorithmGetter:
    def __init__(self):
        module = import_module('algorithm_getters.storage.' + settings.algorithm_storage_backend.type)
        storage_type: Type[BaseStorage] = getattr(module, module.class_name)
        self.storage = storage_type()
        logger.info(self.storage)

    def get_algorithm(self, algorithm_name: str, file_content: str = None) -> Type[BaseAlgorithm]:
        if file_content:
            algorithm_module = self.storage.get_module(file_content)
        else:
            algorithm_module = self.storage.get_module(algorithm_name)
        algorithm_class = getattr(algorithm_module, algorithm_module.class_name)
        assert algorithm_class not in [
            BaseAlgorithm, BaseDataGetter, BaseDataSaver, BaseDataBalancer
        ], 'invalid algorithm'
        assert issubclass(algorithm_class, BaseAlgorithm), 'invalid algorithm'
        return algorithm_class

    def get_balancer(self, balancer_name: str, file_content: str = None) -> Type[BaseDataBalancer]:
        if file_content:
            algorithm_module = self.storage.get_module(file_content)
        else:
            algorithm_module = self.storage.get_module(balancer_name)
        algorithm_class = getattr(algorithm_module, algorithm_module.class_name)
        assert algorithm_class != BaseDataBalancer, 'invalid algorithm'
        assert issubclass(algorithm_class, BaseDataBalancer), 'invalid algorithm'
        return algorithm_class

    def get_saver(self, saver_name: str, file_content: str = None) -> Type[BaseDataSaver]:
        if file_content:
            algorithm_module = self.storage.get_module(file_content)
        else:
            algorithm_module = self.storage.get_module(saver_name)
        algorithm_class = getattr(algorithm_module, algorithm_module.class_name)
        assert algorithm_class != BaseDataSaver, 'invalid algorithm'
        assert issubclass(algorithm_class, BaseDataSaver), 'invalid algorithm'
        return algorithm_class

    def get_getter(self, getter_name: str, file_content: str = None) -> Type[BaseDataGetter]:
        if file_content:
            algorithm_module = self.storage.get_module(file_content)
        else:
            algorithm_module = self.storage.get_module(getter_name)
        algorithm_class = getattr(algorithm_module, algorithm_module.class_name)
        assert algorithm_class != BaseDataGetter, 'invalid algorithm'
        assert issubclass(algorithm_class, BaseDataGetter), 'invalid algorithm'
        return algorithm_class
