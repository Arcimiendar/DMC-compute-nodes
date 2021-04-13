from abc import ABCMeta
from models.base_algorithm import BaseAlgorithm
import time


class BaseDataGetter(BaseAlgorithm, metaclass=ABCMeta):
    def __init__(self):
        super(BaseDataGetter, self).__init__()
        self.statistic = {
            "start_time": 0,
            "end_time": 0,
            "spent_time": 0
        }

    def get_data(self, ctx, params):

        start_time = time.time()
        self.statistic['start_time'] = start_time

        result = self.execute(ctx, params)

        end_time = time.time()
        self.statistic['end_time'] = end_time
        self.statistic['spent_time'] = end_time - start_time

        return result
