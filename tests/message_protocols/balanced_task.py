import unittest

from tests.message_protocols.base_protocol_test_case import BaseProtocolTestCase
from message_putter.balancer_node_putter import BalancedTaskPutter
from message_accepters.computing_node_accepter import BalancedTaskAccepter


class TestBalancedTask(BaseProtocolTestCase, unittest.TestCase):
    PUTTER_CLASS = BalancedTaskPutter
    ACCEPTER_CLASS = BalancedTaskAccepter

    def generate_task(self):
        return {
            "taskId": "asdf",
            "algorithm": {
                "tasks": [
                    {"fileName": "to_uppercase.py"},
                    {"fileName": "reversed.py"}
                ],
                "name": "algorithm"
            },
            "dataSet": {
                "link": "example/of/possible/link",
                "dataGetter": {
                    "fileName": "dataGettter.py"
                },
                "dataSplitter": {
                    "fileName": "dataSplitter.py"
                },
                "dataSaver": {
                    "fileName": "dataSaver.py"
                }
            }
        }
