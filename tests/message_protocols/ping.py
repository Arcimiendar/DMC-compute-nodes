import unittest

from tests.message_protocols.base_protocol_test_case import BaseProtocolTestCase
from message_putter.computing_node_putter import PingPutter
from message_accepters.balancer_node_accepter import PingAccepter
from computing_nodes.computing_node import NodeInfo


class TestPings(BaseProtocolTestCase, unittest.TestCase):
    ACCEPTER_CLASS = PingAccepter
    PUTTER_CLASS = PingPutter

    def generate_task(self):
        return NodeInfo(status='working')
