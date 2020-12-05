import logging

from multiprocessing import Pool, Semaphore
from typing import Callable, NoReturn

import settings

from executors.executors.calculator import calculator
from executors.executors.convolution import convolution


from models.task import Task

logger = logging.getLogger(__name__)


class ExecutorManager:
    def __init__(self):
        self.pool = Pool(settings.WORKERS_NUMBER, maxtasksperchild=1)
        self.semaphore = Semaphore(settings.WORKERS_NUMBER)

    def get_task_executor(self, task: Task) -> Callable[[Task], NoReturn]:
        if task.type == task.TaskTypes.CALCULATOR:
            return calculator
        elif task.type == task.TaskTypes.CONVOLUTION:
            return convolution

        return lambda x: x

    def proceed_task(self, task):
        self.get_task_executor(task)(task)
        self.semaphore.release()

    def execute_task(self, task: Task) -> NoReturn:
        self.semaphore.acquire()

        if settings.DEBUG:
            self.proceed_task(task)
        else:
            self.pool.apply_async(
                self.proceed_task, args=(task,)
            )
