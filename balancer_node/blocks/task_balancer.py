from models.base_algorithm import Context
from models.base_data_balancer import BaseDataBalancer
from typing import Dict, Type, Tuple, Any, List


class TaskBalancer:
    @classmethod
    def balance_task(cls, task: dict, handler: Type[BaseDataBalancer]) -> Tuple[Context, List[Dict[str, Any]]]:
        context = Context(task)
        handler_instance = handler()
        tasks = handler_instance.balance_task(context, task['dataSet']['link'])
        task['statistic'] = {'splitter': handler_instance.statistic}
        return context, [{**task, 'current_result': splitted_task} for splitted_task in tasks]
