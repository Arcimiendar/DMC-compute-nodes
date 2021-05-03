from models.base_algorithm import Context
from models.base_data_getter import BaseDataGetter
from typing import Tuple, Type


class TaskDataGetter:
    @classmethod
    def get_data(cls, task: dict, handler: Type[BaseDataGetter]) -> Tuple[Context, dict]:
        context = Context(task)
        handler_instance = handler()
        task['current_result'] = handler_instance.get_data(context, task['current_result'])
        task['statistic']['getter'] = handler_instance.statistic
        return context, task
