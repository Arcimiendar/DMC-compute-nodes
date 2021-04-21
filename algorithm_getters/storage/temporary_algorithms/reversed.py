from models.base_algorithm import BaseAlgorithm, Context

class_name = 'Reversed'


class Reversed(BaseAlgorithm):
    def execute(self, ctx: Context, data: str) -> str:
        return data[::-1]
