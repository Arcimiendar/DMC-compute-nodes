from models.base_algorithm import Context
from models.base_data_getter import BaseDataGetter
class_name = 'SentenceGetter'


class SentenceGetter(BaseDataGetter):
    def execute(self, ctx: Context, data: str):
        return data
