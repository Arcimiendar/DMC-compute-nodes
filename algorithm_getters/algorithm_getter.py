from models.base_algorithm import BaseAlgorithm, Context
from models.base_data_balancer import BaseDataBalancer
from models.base_data_getter import BaseDataGetter
from models.base_data_saver import BaseDataSaver
from typing import Type


class AlgorithmGetter:
    def get_algorithm(self, algorithm_name: str) -> Type[BaseAlgorithm]:
        pass

    def get_balancer(self, balancer_name: str) -> Type[BaseDataBalancer]:
        class TempDataBalancer(BaseDataBalancer):
            def execute(self, ctx: Context, data: str) -> object:
                return data.split('/')

        return TempDataBalancer

    def get_saver(self, saver_name: str) -> Type[BaseDataSaver]:
        pass

    def get_getter(self, getter_name: str) -> Type[BaseDataGetter]:
        pass
