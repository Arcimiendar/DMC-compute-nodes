from models.base_algorithm import BaseAlgorithm, Context
from models.base_data_balancer import BaseDataBalancer
from models.base_data_getter import BaseDataGetter
from models.base_data_saver import BaseDataSaver
from settings_loader import SettingsLoader
from typing import Type


settings = SettingsLoader.get_instance()


class AlgorithmGetter:
    def get_algorithm(self, algorithm_name: str) -> Type[BaseAlgorithm]:
        if algorithm_name == 'to_uppercase.py':
            class TempAlgorithm(BaseAlgorithm):
                def execute(self, ctx: Context, data: str) -> str:
                    return data.upper()
        else:
            class TempAlgorithm(BaseAlgorithm):
                def execute(self, ctx: Context, data: str) -> str:
                    return data[::-1]

        return TempAlgorithm

    def get_balancer(self, balancer_name: str) -> Type[BaseDataBalancer]:
        class TempDataBalancer(BaseDataBalancer):
            def execute(self, ctx: Context, data: str) -> object:
                return data.split('/')

        return TempDataBalancer

    def get_saver(self, saver_name: str) -> Type[BaseDataSaver]:
        class TempDataSaver(BaseDataSaver):
            def execute(self, ctx: Context, data: str) -> object:
                with open(f'{data}_{settings.service_id}', 'a') as f:
                    f.write(data)
        return TempDataSaver

    def get_getter(self, getter_name: str) -> Type[BaseDataGetter]:
        class TempDataGetter(BaseDataGetter):
            def execute(self, ctx: Context, data: object) -> object:
                return data

        return TempDataGetter
