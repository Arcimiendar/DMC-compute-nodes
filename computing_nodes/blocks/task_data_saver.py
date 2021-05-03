from models.base_algorithm import Context
from models.base_data_saver import BaseDataSaver
from typing import Tuple, Type


class TaskDataSaver:
    @classmethod
    def save_data(cls, context: Context, task: dict, handler: Type[BaseDataSaver]) -> Tuple[Context, dict]:
        handler_instance = handler()
        handler_instance.save_data(context, task['current_result'])
        task.pop('current_result')
        task['statistic']['saver'] = handler_instance.statistic
        return context, task
