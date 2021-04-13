from models.base_algorithm import BaseAlgorithm
from models.base_data_balancer import BaseDataBalancer
from models.base_data_getter import BaseDataGetter
from models.base_data_saver import BaseDataSaver


class AlgorithmGetter:
    def get_algorithm(self, algorithm_name: str) -> BaseAlgorithm:
        pass

    def get_balancer(self, balancer_name: str) -> BaseDataBalancer:
        pass

    def get_saver(self, saver_name: str) -> BaseDataSaver:
        pass

    def get_getter(self, getter_name: str) -> BaseDataGetter:
        pass