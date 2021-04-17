from message_putter.base_message_putter import BaseMessagePutter
from remote_procedure_call.rabbit_remote_procedure_call import RabbitRPCFunctionCaller


class BalancedTaskPutter(BaseMessagePutter):
    FUNCTION_NAME = 'put_task'
    NAMESPACE = 'computer_node'
    NEED_ACK = False
    RPC_CALLER_CLASS = RabbitRPCFunctionCaller

    def incapsulate_task(self, task: object) -> bytes:
        pass

    def parse_reponse(self, response: bytes):
        pass


class StatisticTaskPutter(BaseMessagePutter):
    FUNCTION_NAME = 'get_statistic'
    NAMESPACE = 'computer_node'
    NEED_ACK = True
    RPC_CALLER_CLASS = RabbitRPCFunctionCaller

    def incapsulate_task(self, task: object) -> bytes:
        pass

    def parse_reponse(self, response: bytes):
        pass
