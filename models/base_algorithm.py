from logs import get_logger
from abc import ABCMeta, abstractmethod

logger = get_logger(__name__)


class Context:
    def __init__(self, raw_request):
        self.raw_request = raw_request


class BaseAlgorithm(metaclass=ABCMeta):

    def __init__(self):
        self.statistic = {}

    @abstractmethod
    def execute(self, ctx: Context, data: object) -> object:
        pass
