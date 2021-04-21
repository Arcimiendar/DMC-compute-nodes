from models.base_data_getter import BaseDataGetter
from models.base_algorithm import Context

class_name = 'TempDataGetter'


class TempDataGetter(BaseDataGetter):
    def execute(self, ctx: Context, data: object) -> object:
        return data
