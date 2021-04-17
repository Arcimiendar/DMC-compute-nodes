from abc import ABCMeta, abstractmethod
from typing import Type, Tuple
from remote_procedure_call.base_remote_procedure_call import RPCFunctionListenerInterface


class BaseAccepter(metaclass=ABCMeta):
    FUNCTION_NAME: str = None
    NAMESPACE: str = None

    RPC_LISTENER_CLASS: Type[RPCFunctionListenerInterface] = None

    def __init__(self):
        assert self.FUNCTION_NAME, "function name is not provided"
        assert self.RPC_LISTENER_CLASS, "rpc listener class is not provided"

        self.function_listener = self.RPC_LISTENER_CLASS(self.FUNCTION_NAME, self.NAMESPACE)

    def get_task(self) -> Tuple[object, object]:
        call_info, task = self.function_listener.receive_call()

        task = self.parse_task(task)

        return call_info, task

    @abstractmethod
    def parse_task(self, task: bytes) -> object:
        raise NotImplemented

    def respond_to_task(self, call_info: object, response: object) -> None:
        incapsulated_response = self.incapsulate_response(response)
        self.function_listener.send_return(call_info, incapsulated_response)

    @abstractmethod
    def incapsulate_response(self, response: object) -> bytes:
        raise NotImplemented
