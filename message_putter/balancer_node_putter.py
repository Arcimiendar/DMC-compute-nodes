from message_putter.base_message_putter import BaseMessagePutter
from remote_procedure_call.rabbit_remote_procedure_call import (
    RabbitRPCFunctionCaller, RabbitNoReturnRPCFunctionCaller
)

import json


class BalancedTaskPutter(BaseMessagePutter):
    FUNCTION_NAME = 'put_task'
    NAMESPACE = 'computing_node'
    NEED_ACK = False
    RPC_CALLER_CLASS = RabbitNoReturnRPCFunctionCaller

    def incapsulate_task(self, task: object) -> bytes:
        return json.dumps(task)

    def parse_response(self, response: bytes):
        raise NotImplemented


class StatisticTaskPutter(BaseMessagePutter):
    FUNCTION_NAME = 'get_statistic'
    NAMESPACE = 'computing_node'
    NEED_ACK = True
    RPC_CALLER_CLASS = RabbitRPCFunctionCaller

    def __init__(self, node_name):
        self.FUNCTION_NAME += f'_node_{node_name}'
        super(StatisticTaskPutter, self).__init__()

    def incapsulate_task(self, task: object) -> bytes:
        return json.dumps(task)

    def parse_response(self, response: bytes):
        return json.loads(response)
