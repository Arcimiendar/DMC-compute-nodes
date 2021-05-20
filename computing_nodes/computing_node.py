from dataclasses import dataclass
from logs import get_logger
from typing import NoReturn, Union
from settings_loader.settings_loader import SettingsLoader
from message_putter.computing_node_putter import PingPutter, DoneTaskPutter
from message_accepters.computing_node_accepter import StatisticTaskAccepter, BalancedTaskAccepter
from utils.error_context_handler_mixin import ErrorHandlerContextMixin
from algorithm_getters.algorithm_getter import AlgorithmGetter
from computing_nodes.blocks.task_algorithm import TaskAlgorithm
from computing_nodes.blocks.task_data_getter import TaskDataGetter
from computing_nodes.blocks.task_data_saver import TaskDataSaver
from utils.timed_dict import TimedDict

import threading

logger = get_logger(__name__)
settings = SettingsLoader.get_instance()


@dataclass
class NodeInfo:
    status: str
    node_name = settings.service_id


class ComputingNode(ErrorHandlerContextMixin):
    def __init__(self):
        super(ComputingNode, self).__init__()
        self.current_state = None
        self.ping = PingPutter()
        self.done_task = DoneTaskPutter()
        self.task_accepter = BalancedTaskAccepter()
        self.statistic_accepter = StatisticTaskAccepter(settings.service_id)
        self.node_info = NodeInfo(status='working')
        self.algorithm_getter = AlgorithmGetter()
        self.task: Union[dict, None] = None
        main = threading.Thread(target=self.run_main_logic)
        pings = threading.Thread(target=self.run_pings)
        statistic = threading.Thread(target=self.run_statistic_logic)
        self.current_statistics = TimedDict(60)
        main.start()
        pings.start()
        statistic.start()

        main.join()
        pings.join()
        statistic.join()

    def preprocess_task(self, task):
        task['statistic'] = {}
        task['statistic']['getter'] = None
        task['statistic']['saver'] = None
        task['statistic']['algorithms'] = {}
        return task

    def run_main_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                _, self.task = self.task_accepter.get_task()
                self.task: dict
                self.task = self.preprocess_task(self.task)
                logger.info(f'got task: {self.task}')

                data_getter = self.algorithm_getter.get_getter(self.task['dataSet']['dataGetter']['fileName'])
                algorithm = [
                    self.algorithm_getter.get_algorithm(step['fileName'])
                    for step in self.task['algorithm']['tasks']
                ]

                data_saver = self.algorithm_getter.get_saver(self.task['dataSet']['dataSaver']['fileName'])
                ###
                context, self.task = TaskDataGetter.get_data(self.task, data_getter)
                context, self.task = TaskAlgorithm.execute(context, self.task, algorithm)
                context, self.task = TaskDataSaver.save_data(context, self.task, data_saver)
                ###
                self.current_statistics[self.task['taskId']] = self.task['statistic']
                self.done_task.put_task(self.task)
                self.done_task.return_response()

    def run_statistic_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                call_info, statistic_request = self.statistic_accepter.get_task()
                statistic_request: dict
                logger.info(f'got statistic_request {statistic_request} {self.current_statistics.dict}')
                self.statistic_accepter.respond_to_task(
                    call_info, self.current_statistics.dict.get(statistic_request['taskId'])
                )

    def run_pings(self) -> NoReturn:
        self.ping.put_task(self.node_info)
        while not self.stop_event.wait(60):
            self.ping.put_task(self.node_info)

        self.node_info.status = 'quit'
        self.ping.put_task(self.node_info)
