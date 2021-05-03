from models.base_algorithm import Context, BaseAlgorithm
from typing import Tuple, Type, List


class TaskAlgorithm:
    @classmethod
    def execute(cls, context: Context, task: dict, handlers: List[Type[BaseAlgorithm]]) -> Tuple[Context, dict]:
        for index, handler in enumerate(handlers):
            handler_instance = handler()
            task['current_result'] = handler_instance.execute(context, task['current_result'])
            task['statistic']['algorithms'][f'{index}_{handler.__class__.__name__}'] = handler.statistic
        return context, task
