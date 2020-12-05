import json
import logging

logger = logging.getLogger(__name__)


class Task:
    class TaskTypes:
        CALCULATOR = "calculator"
        CONVOLUTION = "convolution"

        @classmethod
        def check_type(cls, type_of_task: str) -> bool:
            if type_of_task == cls.CALCULATOR:
                return True
            elif type_of_task == cls.CONVOLUTION:
                return True
            return False

        class UnsupportedTaskType(Exception):
            def __init__(self, unsupported_type: str):
                self.message = f'unsupported task type: {unsupported_type}'
                self.type = unsupported_type
                super().__init__()

    def __init__(self, request: str):
        self.raw_request = json.loads(request)
        self.type = self.raw_request['request']['type']
        if not self.TaskTypes.check_type(self.type):
            raise Task.TaskTypes.UnsupportedTaskType(self.type)
        self.data = self.raw_request['request']['data']
        self.request_id = self.raw_request['id']

    def __str__(self):
        return f'Task<{{"type": "{self.type}", "data": "{self.data}", "request_id": "{self.request_id}"}}>'

    def __repr__(self):
        return f'Task instance for {{"type": "{self.type}", "data": "{self.data}", "request_id": "{self.request_id}"}}'
