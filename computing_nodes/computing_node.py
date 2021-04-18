from dataclasses import dataclass
from logs import get_logger
from typing import NoReturn
from settings_loader.settings_loader import SettingsLoader
from message_putter.computing_node_putter import PingPutter
from message_accepters.computing_node_accepter import StatisticTaskAccepter, BalancedTaskAccepter
from contextlib import contextmanager
import threading

logger = get_logger(__name__)
settings = SettingsLoader.get_instance()


@dataclass
class NodeInfo:
    status: str
    node_name = settings.service_id


class ComputingNode:
    def __init__(self):
        self.stop_event = threading.Event()
        self.current_state = None
        self.ping = PingPutter()
        self.task_accepter = BalancedTaskAccepter()
        self.statistic_accepter = StatisticTaskAccepter(settings.service_id)
        self.node_info = NodeInfo(status='working')
        self.error_number = 0
        main = threading.Thread(target=self.run_main_logic)
        pings = threading.Thread(target=self.run_pings)
        statistic = threading.Thread(target=self.run_statistic_logic)

        main.start()
        pings.start()
        statistic.start()

        main.join()
        pings.join()
        statistic.join()

    @contextmanager
    def error_handler_context(self):
        try:
            yield None
        except Exception as e:
            self.error_number += 1
            logger.exception(e)
            if not settings.error_policy.ignore_all and settings.error_policy.tolerance_number < self.error_number:
                self.stop_event.set()

    def run_main_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                task = self.task_accepter.get_task()
                logger.info(f'got task: {task}')

    def run_statistic_logic(self) -> NoReturn:
        while not self.stop_event.is_set():
            with self.error_handler_context():
                statistic_request = self.statistic_accepter.get_task()
                logger.info(f'got statistic_request {statistic_request}')

    def run_pings(self) -> NoReturn:
        self.ping.put_task(self.node_info)
        while not self.stop_event.wait(60):
            self.ping.put_task(self.node_info)

        self.node_info.status = 'quit'
        self.ping.put_task(self.node_info)
