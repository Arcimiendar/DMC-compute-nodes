# -*- coding: utf-8 -*-
import time
import uuid
from logs import get_logger
from rabbitmq.rabbitmq import Rabbitmq
from remote_procedure_call.base_remote_procedure_call import (
	RPCFunctionListenerInterface, RPCFunctionCallerInterface
)

from typing import Dict, NoReturn, Tuple, Optional
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties


RPC_EXCHANGE_NAME = 'exchange'
RPC_REQUEST_ROUTING_KEY_PATTERN = 'rpc.request.'


logger = get_logger(__name__)


class RabbitRPCFunctionListener(RPCFunctionListenerInterface):
	AUTO_DELETE_QUEUE = False
	QUEUE_TTL = None

	def __init__(self, *args, **kwargs):
		super(RabbitRPCFunctionListener, self).__init__(*args, **kwargs)
		if self.namespace:
			self.name_of_function = '{}.{}'.format(self.namespace, self.name_of_function)
		self.queue_name = RPC_REQUEST_ROUTING_KEY_PATTERN + self.name_of_function
		self.request_rabbit = Rabbitmq()
		self.response_rabbit = Rabbitmq()
		self.consumer_tag = self.name_of_function + '.' + str(uuid.uuid4())
		self._init_rabbit()
		self.message_is_requested = False
		self.gotten_data = None
	
	def _init_rabbit(self):
		self.request_rabbit.check_connect()
		self.request_rabbit.declare_rpc_exchange(RPC_EXCHANGE_NAME)
		self.request_rabbit.declare_rpc_function_queue(
			self.queue_name, self.queue_name, RPC_EXCHANGE_NAME,
			auto_delete=self.AUTO_DELETE_QUEUE, expires_at=self.QUEUE_TTL
		)
	
	def _rabbit_consumer(self, channel, method, properties, body):
		# type: (BlockingChannel, Basic.Deliver, BasicProperties, bytes) -> None
		if not self.message_is_requested:  # protecting of processing multiple message per one time
			channel.basic_nack(method.delivery_tag)
			return
		
		channel.basic_ack(method.delivery_tag)
		self.message_is_requested = False
		reply_to = properties.reply_to
		correlation_id = properties.correlation_id
		
		self.gotten_data = ({'reply_to': reply_to, 'correlation_id': correlation_id}, body)
		
	def receive_call(self):
		# type: () -> Tuple[Dict[str, str], bytes]
		# important to be 1 to prevent consumer work under multiple messages
		if not self.request_rabbit.check_connect(reconnect=False):
			self._init_rabbit()
		self.request_rabbit.start_consuming(self.queue_name, self.consumer_tag, self._rabbit_consumer, prefetch_count=1)
		self.message_is_requested = True
		flag = self.request_rabbit.process_one_message()
		if not flag:
			logger.info('ERROR while process one message, try to reconnect to rabbit')
			while not self.request_rabbit.check_connect():
				logger.info('connect to rabbit failed. try again in 5 second')
				time.sleep(5)
			self._init_rabbit()
		self.request_rabbit.stop_consuming(self.consumer_tag)
		self.request_rabbit.process_one_message()
		gotten_data = self.gotten_data
		self.gotten_data = None
		return gotten_data

	def send_return(self, call_properties, return_data, content_type=None):
		# type: (Dict[str, str], bytes, Optional[str]) -> None
		self.response_rabbit.send_msg(
			RPC_EXCHANGE_NAME, call_properties.get('reply_to'),
			return_data, custom_properties=BasicProperties(
				correlation_id=call_properties.get('correlation_id'),
				content_type=content_type,
			), ignore_routing_key_project_autofill=True
		)


class TemporaryRabbitRPCFunctionListener(RabbitRPCFunctionListener):
	QUEUE_TTL = 60 * 1000


class RabbitRPCFunctionCaller(RPCFunctionCallerInterface):
	RPC_QUEUE_RETURN_NAME_PATTERN = 'rpc.'
	RPC_RESPONSE_BIND_PATTERN = 'rpc.response.{}.'

	def __init__(self, *args, **kwargs):
		super(RabbitRPCFunctionCaller, self).__init__(*args, **kwargs)
		if self.namespace:
			self.name_of_function = '{}.{}'.format(self.namespace, self.name_of_function)
		self.response_bind_pattern = self.RPC_RESPONSE_BIND_PATTERN.format(self.name_of_function)

		self.rabbit = Rabbitmq()
		self._init_rabbit()
		self.gotten_message = None
		self.id_of_call = None
		self.name_of_queue = None
		
	def _init_rabbit(self):
		self.rabbit.declare_rpc_exchange(RPC_EXCHANGE_NAME)
	
	def _rabbit_consumer(self, channel, method, properties, body):
		# type: (BlockingChannel, Basic.Deliver, BasicProperties, bytes) -> NoReturn
		self.gotten_message = body
		channel.basic_ack(method.delivery_tag)
	
	def call(self, params, content_type=None):
		# type: (bytes, Optional[str]) -> NoReturn
		self.rabbit.check_connect()
		self.id_of_call = str(uuid.uuid4())
		self.name_of_queue = self.RPC_QUEUE_RETURN_NAME_PATTERN + self.name_of_function + '.' + self.id_of_call
		self.rabbit.init_queue(self.name_of_queue, auto_delete=True, exclusive=True)
		self.rabbit.binding_to_the_exchange(
			RPC_EXCHANGE_NAME, self.name_of_queue, self.response_bind_pattern + self.id_of_call
		)
		self.rabbit.start_consuming(self.name_of_queue, self.name_of_queue, self._rabbit_consumer, 1)
		self.rabbit.send_msg(
			RPC_EXCHANGE_NAME, RPC_REQUEST_ROUTING_KEY_PATTERN + self.name_of_function, params,
			custom_properties=BasicProperties(
				reply_to=self.response_bind_pattern + self.id_of_call,
				correlation_id=self.id_of_call, content_type=content_type
			)
		)
		
	def fetch_response(self):
		# type: () -> bytes
		self.rabbit.process_one_message()
		self.rabbit.stop_consuming(self.name_of_queue)
		self.rabbit.disconnect()
		gotten_message, self.gotten_message = self.gotten_message, None  # clear variable and assign to new one
		return gotten_message


class RabbitNoReturnRPCFunctionCaller(RPCFunctionCallerInterface):

	def __init__(self, *args, **kwargs):
		super(RabbitNoReturnRPCFunctionCaller, self).__init__(*args, **kwargs)
		if self.namespace:
			self.name_of_function = '{}.{}'.format(self.namespace, self.name_of_function)

		self.rabbit = Rabbitmq()
		self._init_rabbit()

	def _init_rabbit(self):
		self.rabbit.declare_rpc_exchange(RPC_EXCHANGE_NAME)

	def call(self, params, content_type=None):
		# type: (bytes, Optional[str]) -> NoReturn
		self.rabbit.check_connect()
		self.rabbit.send_msg(
			RPC_EXCHANGE_NAME, RPC_REQUEST_ROUTING_KEY_PATTERN + self.name_of_function, params,
			custom_properties=BasicProperties(
				reply_to=None,
				correlation_id=None, content_type=content_type
			)
		)

	def fetch_response(self):
		# type: () -> bytes
		raise NotImplemented
