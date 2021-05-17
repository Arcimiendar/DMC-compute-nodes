import unittest
from tests.message_protocols.base_protocol_test_case import BaseProtocolTestCase
from message_putter.computing_node_putter import DoneTaskPutter
from message_accepters.balancer_node_accepter import DoneTaskAccepter


class TestDoneTask(BaseProtocolTestCase, unittest.TestCase):
    ACCEPTER_CLASS = DoneTaskAccepter
    PUTTER_CLASS = DoneTaskPutter

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
