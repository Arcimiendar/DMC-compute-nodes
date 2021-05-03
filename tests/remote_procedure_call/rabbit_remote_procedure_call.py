from remote_procedure_call.rabbit_remote_procedure_call import (
    RabbitRPCFunctionListener, RabbitRPCFunctionCaller
)
from random import shuffle
import unittest


class TestRabbitRPCFunction(unittest.TestCase):
    def setUp(self) -> None:
        self.listener = RabbitRPCFunctionListener(
            name_of_function='test_function',
            namespace='test_namespace'
        )
        self.rpc_function_caller = RabbitRPCFunctionCaller(name_of_function='test_function', namespace='test_namespace')
        self.caller = self.rpc_function_caller

    def test_one_time_conversation(self):
        test_params = b'test_params'
        test_response = b'test_response'
        self.caller.call(test_params)
        call_info, received_params = self.listener.receive_call()
        self.assertEqual(test_params, received_params)
        self.listener.send_return(call_info, test_response)
        response = self.caller.fetch_response()
        self.assertEqual(test_response, response)

    def test_multiple_conversations(self):
        iterations = 10
        test_params_pattern = b'%d'
        test_response_pattern = b'test_params_%s'

        callers = [
            RabbitRPCFunctionCaller(
                name_of_function='test_function',
                namespace='test_namespace'
            ) for _ in range(iterations)
        ]

        for index, caller in enumerate(callers):
            caller.call(test_params_pattern % index)

        calls = []
        for _ in range(iterations):
            calls.append(self.listener.receive_call())
        shuffle(calls)

        for call_info, params in calls:
            self.listener.send_return(call_info, test_response_pattern % params)

        for index, caller in enumerate(callers):
            returned_data = caller.fetch_response()
            self.assertEqual(returned_data, test_response_pattern % str(index).encode())
