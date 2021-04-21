from models.base_data_balancer import BaseDataBalancer
from models.base_algorithm import Context
from settings_loader.settings_loader import SettingsLoader

class_name = 'TempDataBalancer'

settings = SettingsLoader.get_instance()


class TempDataBalancer(BaseDataBalancer):
    def execute(self, ctx: Context, data: str) -> object:
        return data.split('/')
