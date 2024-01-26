from models.base_algorithm import Context
from models.base_data_saver import BaseDataSaver

class_name = 'SentenceSaver'


class SentenceSaver(BaseDataSaver):
    def execute(self, ctx: Context, data: str):
        return data
