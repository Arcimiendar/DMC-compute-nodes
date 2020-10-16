from typing import Union

from settings import settings
from queue import Queue
import pika
import pika.exceptions
import logging
import time

from models.task import Task
from threading import Thread

logger = logging.getLogger(__name__)


class DataSource:
    def __init__(self):
        connection_is_good = False
        pika_connection_params = pika.ConnectionParameters(**settings.RABBIT_SETTINGS)

        while not connection_is_good:
            try:
                self.connection = pika.BlockingConnection(pika_connection_params)
                connection_is_good = True
            except pika.exceptions.AMQPConnectionError:
                logger.info("RABBIT IS NOT UP YET, SLEEP 5 SECOND")
                time.sleep(5)


        self.channel: pika.adapters.blocking_connection.BlockingChannel = self.connection.channel()

        self.queue = Queue()

        self.channel.queue_declare(settings.LISTENING_QUEUE)

        logger.info("Data source successfully init")

    def start_listenning(self):
        logger.info(f"start listenning to queue {settings.LISTENING_QUEUE}")
        self.channel.basic_consume(settings.LISTENING_QUEUE, auto_ack=True, on_message_callback=self.rabbit_callback)
        Thread(name="data_source_listenning_thread", target=self.channel.start_consuming).start()

    def stop_listenning(self):
        logger.info(f'stop listenning to queue {settings.LISTENING_QUEUE}')
        self.channel.stop_consuming()

    def __enter__(self):
        self.start_listenning()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_listenning()

    def get_message(self, timeout=None) -> Union[str, None]:
        return self.queue.get(timeout=timeout)

    def get_task(self, timeout=None) -> Union[Task, None]:
        message = self.get_message(timeout)
        return Task(message) if message is not None else None

    def rabbit_callback(self, ch, method, properties, body: bytes):
        logger.info("GOT REQUEST FROM RABBIT")
        self.queue.put(body.decode("utf-8"))
