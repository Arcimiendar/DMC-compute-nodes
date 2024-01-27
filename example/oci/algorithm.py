from models.base_algorithm import BaseAlgorithm, Context


class_name = 'Upper'

class Upper(BaseAlgorithm):
    def execute(self, ctx: Context, data: str) -> object:
        return data.upper()
