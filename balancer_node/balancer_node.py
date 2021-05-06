import json

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

    def handle_system_statistics(self, statistics_request):
        result = {"key": ""}
        if statistics_request['key'] == "done_percent":
            task_id = statistics_request['taskId']
            pending_task = self.pending_tasks.get(task_id, {'total_number_of_tasks': 0, 'number_of_tasks': 0})
            total_number_of_tasks = pending_task["total_number_of_tasks"]
            number_of_tasks = pending_task["number_of_tasks"]
            result['key'] = json.dumps({
                "total_number_of_tasks": total_number_of_tasks,
                "number_of_tasks": number_of_tasks,
                "percent": 100 if number_of_tasks == 0 or total_number_of_tasks == 0
                else (total_number_of_tasks - number_of_tasks) / total_number_of_tasks
            })

        elif statistics_request['key'] == 'available_nodes':
            nodes = []
            for node in self.available_nodes.values():
                nodes.append(node['name'])
            result['key'] = json.dumps({'available_nodes': nodes})
        return result

    def handle_user_statistics(self, statistics_request):
        promises = []
        node_statistic = []

        for node in self.available_nodes.values():
            promises.append(StatisticTaskPutter(node['node_name']))

        for promise in promises:
            promise.put_task(statistics_request)

        for promise in promises:
            node_statistic.append(promise.return_response())

        merged_statistic = self.merge_statistic(node_statistic)

        return merged_statistic

    def run_statistics_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                return_address, statistics_request = self.statistic.get_task()
                statistics_request = {
                    "key": "done_percent",
                    "taskId": "",  # task id
                    "system": True
                }
                logger.info(f'got statistic request {statistics_request}')
                if statistics_request['system']:
                    result = self.handle_system_statistics(statistics_request)
                else:
                    result = self.handle_user_statistics(statistics_request)

                self.statistic.respond_to_task(return_address, result)

    def merge_statistic(self, node_statistic):
        merged_statistic = []
        result = {'key': ''}
        for statistic in node_statistic:
            merged_statistic.append(statistic['key'])

        result['key'] = json.dumps({
            'merged_statistic': merged_statistic
        })
        return statistic

    def run_task_accept_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                _, task = self.tasks.get_task()
                task: dict
                task['taskId'] = str(uuid.uuid4())  # temp, remove when Egor finish it
                self.pending_tasks[task['taskId']] = task
                balancer = self.algorithm_getter.get_balancer(task["dataSet"]['dataSplitter']['fileName'])
                _, result = TaskBalancer.balance_task(task, balancer)
                task['total_number_of_tasks'] = task['number_of_tasks'] = len(result)
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
                        self.pending_tasks.pop(done_task['taskId'])

                        self.tasks.respond_to_task(None, result)
