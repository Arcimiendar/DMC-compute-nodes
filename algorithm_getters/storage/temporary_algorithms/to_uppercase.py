from models.base_algorithm import BaseAlgorithm, Context

class_name = 'ToUppercase'


class ToUppercase(BaseAlgorithm):
    def execute(self, ctx: Context, data: str) -> str:
        return data.upper()
