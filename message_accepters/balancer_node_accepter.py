from message_accepters.base_accepter import BaseAccepter
from remote_procedure_call.rabbit_http_remote_procedure_call import RabbitHttpFunctionListener
from remote_procedure_call.rabbit_remote_procedure_call import RabbitRPCFunctionListener

import json


class TaskAccepter(BaseAccepter):
    FUNCTION_NAME = 'put_task'
    NAMESPACE = 'balancer'

    RPC_LISTENER_CLASS = RabbitHttpFunctionListener

    def parse_task(self, task: bytes) -> object:
        return json.loads(task)

    def incapsulate_response(self, response: object) -> bytes:
        return json.dumps(response)


class StatisticAccepter(BaseAccepter):
    FUNCTION_NAME = 'get_statistic'
    NAMESPACE = 'balancer'
    RPC_LISTENER_CLASS = RabbitHttpFunctionListener

    def parse_task(self, task: bytes) -> object:
        return json.loads(task)

    def incapsulate_response(self, response: object) -> bytes:
        return json.dumps(response)


class PingAccepter(BaseAccepter):
    FUNCTION_NAME = 'ping'
    NAMESPACE = 'balancer'

    RPC_LISTENER_CLASS = RabbitHttpFunctionListener

    def parse_task(self, task: bytes) -> object:
        return json.loads(task)

    def incapsulate_response(self, response: object) -> bytes:
        return json.dumps(response)


class DoneTaskAccepter(BaseAccepter):
    FUNCTION_NAME = 'task_done'
    NAMESPACE = 'balancer'

    RPC_LISTENER_CLASS = RabbitRPCFunctionListener

    def parse_task(self, task: bytes) -> object:
        return json.loads(task)

    def incapsulate_response(self, response: object) -> bytes:
        return json.dumps(response)
