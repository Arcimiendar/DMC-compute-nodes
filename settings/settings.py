import logging

PROJECT_NAME = 'name'
# DEBUG = False
DEBUG = True

WORKERS_NUMBER = 1


LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": '%(asctime)s %(name)s %(levelname)s: %(message)s',
    "datefmt": "%m/%d/%Y %H:%M:%S"
}
logging.basicConfig(**LOGGING_CONFIG)


RABBIT_SETTINGS = {
    "host": "rabbit",
}
LISTENING_QUEUE = "sample_queue"
RESPONSE_URL = "http://192.168.43.100:8090/response_from_node"
