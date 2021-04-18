from abc import ABCMeta
from models.base_algorithm import BaseAlgorithm
import time


class BaseDataBalancer(BaseAlgorithm, metaclass=ABCMeta):
    def __init__(self):
        super(BaseDataBalancer, self).__init__()
        self.statistic = {
            "start_time": 0,
            "end_time": 0,
            "spent_time": 0,
            "result": 0
        }

    def balance_task(self, ctx, params):

        start_time = time.time()
        self.statistic['start_time'] = start_time

        splitted_tasks = self.execute(ctx, params)

        end_time = time.time()
        self.statistic['end_time'] = end_time
        self.statistic['spent_time'] = end_time - start_time
        self.statistic['result'] = len(splitted_tasks)

        return splitted_tasks
