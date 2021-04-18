from models.base_algorithm import Context
from models.base_data_balancer import BaseDataBalancer
from typing import List, Type


class TaskBalancer:
    @classmethod
    def balance_task(cls, task: dict, handler: Type[BaseDataBalancer]) -> List[dict]:
        context = Context(task)
        handler_instance = handler()
        tasks = handler_instance.balance_task(context, task['dataSet']['link'])
        return context, [{**task, 'current_result': splitted_task} for splitted_task in tasks]
