from typing import Type
from abc import abstractmethod, ABCMeta

from message_putter.base_message_putter import BaseMessagePutter
from message_accepters.base_accepter import BaseAccepter


class BaseProtocolTestCase(metaclass=ABCMeta):
    PUTTER_CLASS: Type[BaseMessagePutter] = None
    ACCEPTER_CLASS: Type[BaseAccepter] = None

    def setUp(self) -> None:
        self.accepter = self.ACCEPTER_CLASS()
        self.putter = self.PUTTER_CLASS()
        self.task = self.generate_task()

    @abstractmethod
    def generate_task(self):
        raise NotImplemented

    def test_ping(self):
        self.putter.put_task(self.task)
        _, task = self.accepter.get_task()
        self.assertEqual(task, self.accepter.parse_task(self.putter.incapsulate_task(self.task)))
