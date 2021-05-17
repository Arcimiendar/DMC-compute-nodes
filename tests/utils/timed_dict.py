import unittest
import time
from utils.timed_dict import TimedDict


class TestTimedDict(unittest.TestCase):
    def setUp(self) -> None:
        self.dict = TimedDict(1)

    def test_item_is_not_deleted(self):
        self.dict['test'] = 1
        self.assertIn('test', self.dict)
        self.dict.clear()

    def test_item_is_deleted(self):
        self.dict['test'] = 1
        time.sleep(2)
        self.assertNotIn('test', self.dict)
