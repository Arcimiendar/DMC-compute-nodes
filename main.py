import logging

from settings import settings

from data_source.data_source import DataSource
from executors.executor_manager import ExecutorManager

logger = logging.getLogger(__name__)


def main():
    logger.info(f"hello world, {settings.WORKERS_NUMBER}")

    with DataSource() as data_source:
        executor_manager = ExecutorManager()
        while True:
            task = data_source.get_task()
            executor_manager.execute_task(task)


if __name__ == '__main__':
    main()
