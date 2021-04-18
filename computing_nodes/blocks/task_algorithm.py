from models.base_algorithm import Context, BaseAlgorithm
from typing import List, Type


class TaskAlgorithm:
    @classmethod
    def execute(cls, context: Context, task: dict, handlers: List[Type[BaseAlgorithm]]) -> List[dict]:
        for handler in handlers:
            handler_instance = handler()
            task['current_result'] = handler_instance.execute(context, task['current_result'])
        return context, task