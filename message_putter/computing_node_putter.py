from message_putter.base_message_putter import BaseMessagePutter
from remote_procedure_call.rabbit_remote_procedure_call import (
    RabbitNoReturnRPCFunctionCaller, RabbitRPCFunctionCaller
)
from typing import TypeVar

import json

NodeInfo = TypeVar('NodeInfo')
TaskInfo = TypeVar('TaskInfo')


class PingPutter(BaseMessagePutter):
    FUNCTION_NAME = 'ping'
    NAMESPACE = 'balancer'
    NEED_ACK = False
    RPC_CALLER_CLASS = RabbitNoReturnRPCFunctionCaller

    def incapsulate_task(self, task: NodeInfo) -> bytes:
        return json.dumps({'node_name': task.node_name, 'status': task.status}).encode()

    def parse_reponse(self, response: bytes):
        pass


class DoneTaskPutter(BaseMessagePutter):
    FUNCTION_NAME = 'task_done'
    NAMESPACE = 'balancer'
    NEED_ACK = True
    RPC_CALLER_CLASS = RabbitRPCFunctionCaller

    def incapsulate_task(self, task: TaskInfo) -> bytes:
        return json.dumps({
            'status': task.status, 'time_spent': task.time_spent,
            'message': task.message, 'user_id': task.user_id
        })

    def parse_reponse(self, response: bytes):
        return json.loads(response)
