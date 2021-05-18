from models.base_data_saver import BaseDataSaver
from models.base_algorithm import Context
from settings_loader.settings_loader import SettingsLoader
import os

class_name = 'TempDataSaver'

settings = SettingsLoader.get_instance()


class TempDataSaver(BaseDataSaver):
    def execute(self, ctx: Context, data: str) -> None:
        if not os.path.exists('temp'):
            os.mkdir('temp')
        with open(os.path.join('temp', f'{settings.service_id}'), 'a') as f:
            f.write(data + ' ')
