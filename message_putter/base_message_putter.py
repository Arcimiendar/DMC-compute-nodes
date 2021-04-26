from abc import ABCMeta, abstractmethod
from typing import Type
from remote_procedure_call.base_remote_procedure_call import RPCFunctionCallerInterface


class BaseMessagePutter(metaclass=ABCMeta):
    FUNCTION_NAME: str = None
    NAMESPACE: str = None
    NEED_ACK: bool = False

    RPC_CALLER_CLASS: Type[RPCFunctionCallerInterface] = None

    def __init__(self):
        assert self.FUNCTION_NAME, 'function name is not provided'
        assert self.RPC_CALLER_CLASS, 'rpc caller is not provided'

        self.caller = self.RPC_CALLER_CLASS(self.FUNCTION_NAME, self.NAMESPACE)

    def return_response(self):
        response = self.caller.fetch_response()
        response = self.parse_reponse(response)
        return response

    def put_task(self, task):
        raw_task = self.incapsulate_task(task)
        self.caller.call(raw_task)

    @abstractmethod
    def incapsulate_task(self, task: object) -> bytes:
        raise NotImplemented

    @abstractmethod
    def parse_response(self, response: bytes):
        raise NotImplemented
