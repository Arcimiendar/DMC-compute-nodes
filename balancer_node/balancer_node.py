from utils.timed_dict import TimedDict
from utils.error_context_handler_mixin import ErrorHandlerContextMixin
from message_putter.balancer_node_putter import (
    StatisticTaskPutter, BalancedTaskPutter
)
from message_accepters.balancer_node_accepter import (
    StatisticAccepter, TaskAccepter, PingAccepter, DoneTaskAccepter
)
from algorithm_getters.algorithm_getter import AlgorithmGetter
from balancer_node.blocks.task_balancer import TaskBalancer
from logs import get_logger
from typing import NoReturn
import threading
import uuid
import time


logger = get_logger(__name__)


class Balancer(ErrorHandlerContextMixin):
    def __init__(self):
        super(Balancer, self).__init__()
        self.available_nodes = TimedDict(120)
        self.pending_tasks = {}  # redo through redis

        self.pings = PingAccepter()
        self.statistic = StatisticAccepter()
        self.tasks = TaskAccepter()
        self.done_tasks = DoneTaskAccepter()
        self.algorithm_getter = AlgorithmGetter()
        self.balanced_task_putter = BalancedTaskPutter()

        pings = threading.Thread(target=self.run_pings_logic)
        statistics = threading.Thread(target=self.run_statistics_logic)
        tasks = threading.Thread(target=self.run_task_accept_logic)
        done_tasks = threading.Thread(target=self.run_done_task_accept_logic)

        pings.start()
        statistics.start()
        tasks.start()
        done_tasks.start()

        pings.join()
        statistics.join()
        tasks.join()
        done_tasks.join()

    def run_pings_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                ping: dict
                _, ping = self.pings.get_task()
                self.available_nodes[ping['node_name']] = ping
                logger.info(f'got ping {ping}')
                if ping['status'] == 'quit':
                    self.available_nodes.pop(ping['node_name'])

    def run_statistics_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            promises = []
            node_statistic = []
            with self.error_handler_context():
                return_address, statistics_request = self.statistic.get_task()
                logger.info(f'got statistic request {statistics_request}')
                for node in self.available_nodes.values():
                    promises.append(StatisticTaskPutter(node['node_name']))

                for promise in promises:
                    promise.put_task(statistics_request)

                for promise in promises:
                    node_statistic.append(promise.return_response())

                merged_statistic = self.merge_statistic(node_statistic)

                promises.clear()
                node_statistic.clear()

                self.statistic.respond_to_task(return_address, merged_statistic)

    def merge_statistic(self, node_statistic):
        return node_statistic.copy()

    def run_task_accept_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                _, task = self.tasks.get_task()
                task: dict
                task['taskId'] = str(uuid.uuid4())  # temp, remove when Egor finish it
                self.pending_tasks[task['taskId']] = task
                balancer = self.algorithm_getter.get_balancer(task["dataSet"]['dataSplitter']['fileName'])
                _, result = TaskBalancer.balance_task(task, balancer)
                task['number_of_tasks'] = len(result)
                task['time_start'] = time.time()

                for splitted_task in result:
                    self.balanced_task_putter.put_task(splitted_task)

                # self.tasks.respond_to_task(None, 'task_accepted')

    def run_done_task_accept_logic(self):
        while not self.stop_event.is_set():
            with self.error_handler_context():
                call_info, done_task = self.done_tasks.get_task()
                done_task: dict
                if done_task['taskId'] in self.pending_tasks:
                    self.pending_tasks[done_task['taskId']]['number_of_tasks'] -= 1
                    self.done_tasks.respond_to_task(call_info, {'status': 'ok'})

                    if self.pending_tasks[done_task['taskId']]['number_of_tasks'] == 0:
                        result = {
                            'taskId': done_task['taskId'],
                            'status': 'ok',
                            'timeSpent': str(time.time() - self.pending_tasks[done_task['taskId']]['time_start']),
                            'message': 'ok'
                        }
                        logger.info(f'result = {result}')
                    # self.tasks.respond_to_task(None, result)
