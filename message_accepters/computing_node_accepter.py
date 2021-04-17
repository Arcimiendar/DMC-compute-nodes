from remote_procedure_call.rabbit_remote_procedure_call import RabbitRPCFunctionListener
from message_accepters.base_accepter import BaseAccepter

import json


class BalancedTaskAccepter(BaseAccepter):
    FUNCTION_NAME = 'put_task'
    NAMESPACE = 'computing_node'

    RPC_LISTENER_CLASS = RabbitRPCFunctionListener

    def parse_task(self, task: bytes) -> object:
        return json.loads(task)

    def incapsulate_response(self, response: object) -> bytes:
        return json.dumps(response)


class StatisticTaskAccepter(BalancedTaskAccepter):
    FUNCTION_NAME = 'get_statistic'
    NAMESPACE = 'computing_node'

    RPC_LISTENER_CLASS = RabbitRPCFunctionListener

    def __init__(self, node_name: str):
        self.FUNCTION_NAME += f'_node_{node_name}'
        super(StatisticTaskAccepter, self).__init__()
