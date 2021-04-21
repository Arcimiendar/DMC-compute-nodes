from abc import abstractmethod, ABCMeta
from types import ModuleType


class BaseStorage(metaclass=ABCMeta):
    @abstractmethod
    def get_module(self, filename: str) -> ModuleType:
        raise NotImplemented
