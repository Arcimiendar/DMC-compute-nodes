from termcolor import colored
import numexpr as ne
import logging
import requests
import settings

from models.task import Task

logger = logging.getLogger(__name__)


def calculator(task: Task):
    logger.info(
        f'EXPRESSION {colored(task.data, "blue")} '
        f'RESULT = {colored(ne.evaluate(task.data), "blue")}'
    )

    requests.post(
        settings.RESPONSE_URL,
        json={
            'id': task.request_id,
            'response': f'{ne.evaluate(task.data)}'
        }
    )
