# class rabbitmq
import sys
import pika
import settings
from traceback import format_exc as tb
import time
from logs import get_logger

from typing import Tuple, Iterable, Union
from pika.adapters.blocking_connection import BlockingChannel


logger = get_logger(__name__)


class Rabbitmq:
	channel = None  # type: BlockingChannel
	
	def __init__(self):
		self.connection = None
		self.channel = None

	def connect(self):
		if hasattr(settings, "rabbitmq"):
			try:
				logger.info("Try connect to the RabbitMq %s:%s" % (settings.rabbitmq["ip"], settings.rabbitmq["port"]))
				credentials = pika.PlainCredentials(settings.rabbitmq["login"], settings.rabbitmq["pass"])
				parameters = pika.ConnectionParameters(
					host=settings.rabbitmq["ip"],
					port=settings.rabbitmq["port"],
					virtual_host='/',
					credentials=credentials,
					heartbeat=0
				)

				self.connection = pika.BlockingConnection(parameters)
				self.channel = self.connection.channel()
				logger.info("Success...")
			except Exception as e:
				logger.info("Connection Error to the rabbitmq %s" % e)
		else:
			logger.info("Error connection: unknown settings param 'rabbitmq'")

	def check_connect(self, reconnect=True):
		if (
			not self.connection or not self.channel or self.connection.is_closed or self.channel.is_closed
		) and reconnect:
			self.connect()
		if not self.connection or not self.channel or self.connection.is_closed or self.channel.is_closed:
			return False
		return True

	def send_msg(
		self, exchange, routing_key, message, expiration=60000 * 60 * 3,
		durable_msg=None, custom_properties=None, ignore_routing_key_project_autofill=False
	):
		status = False
		if self.check_connect():
			try:
				self.channel.basic_publish(
					exchange='%s' %  exchange,
					routing_key=routing_key if ignore_routing_key_project_autofill else
					"%s" % routing_key,
					body=message,
					properties=custom_properties or pika.BasicProperties(
						expiration=str(expiration),
						delivery_mode=2 if durable_msg else None,  # make message persistent
					)
				)
				status = True
			except Exception:
				logger.exception(
					"Error send to rabbitmq exchange '%s' message '%s' key '%s'" % (exchange, message, routing_key)
				)

		else:
			logger.warning("Error send to rabbitmq exchange '%s' message '%s' key '%s' from no connect rabbitmq" % (
				exchange, message, routing_key
			))
		return status

	def init_queue(self, queue, arguments=None, durable=False, auto_delete=False, exclusive=None):
		try:
			if self.check_connect():
				if not arguments:
					arguments = {
						"x-expires": 60 * 60 * 1000,  # - queue live-time in milliseconds (60 min) without consumers
						"x-message-ttl": 20 * 60 * 1000  # - message live-time in milliseconds (20 min)
					}
				self.channel.queue_declare(
					queue="%s" % queue, durable=durable,
					arguments=arguments, auto_delete=auto_delete, exclusive=exclusive
				)
				logger.info("Create queue %s" % queue)
		except Exception:
			logger.exception("Error in initQueue:")

	def delete_queue(self, queue):
		try:
			self.channel.queue_delete(queue="%s" % queue)
			logger.info("Delete queue %s " % queue)
		except Exception:
			logger.error("Error: Cant delete queue %s" % queue)

	def binding_to_the_exchange(self, exchange, queue, routing_key):
		try:
			self.channel.queue_bind(
				exchange='%s' % exchange,
				queue="%s" % queue,
				routing_key="%s" % routing_key
			)
			logger.info("Good add bind %s to the rabbitmq queue" % routing_key)
		except Exception:
			logger.info("Cant adding bind %s routing key to rabbit queue: %s" % (routing_key, tb()))

	def start_consuming(self, queue, consumer_tag, callback_function, prefetch_count=20):
		consumption_flag = False
		try:
			self.channel.basic_qos(prefetch_count=prefetch_count)
			self.channel.basic_consume(
				queue="%s" % queue,
				on_message_callback=callback_function,
				# exclusive=True,
				consumer_tag=consumer_tag
			)
			consumption_flag = True
			logger.info("rabbitmq consumer worker %s start listen %s" % (consumer_tag, queue))
		except Exception as e:
			logger.info("Error: rabbitmq consumer workers %s cant start listen %s: %s" % (consumer_tag, queue, e))
		return consumption_flag

	def stop_consuming(self, consumer_tag):
		consumption_flag = False
		try:
			self.channel.basic_cancel(consumer_tag=consumer_tag)
			consumption_flag = True
			logger.info("Rabbitmq consumer worker %s stop listen queue" % consumer_tag)
		except Exception as e:
			logger.info("Error: Rabbitmq consumer worker %s cant stop: %s" % (consumer_tag, e))
		return consumption_flag

	def disconnect(self):
		try:
			self.connection.close()
		except Exception as e:
			logger.info("Error disconnect to rabbitmq: %s" % e)
		logger.info("Close connection to %s: %s" % (settings.rabbitmq["ip"], settings.rabbitmq["port"]))

	def process_one_message(self):
		"""
		process only one message
		:return: is message proceed or not
		"""
		process_flag = False
		try:
			self.channel.basic_qos(prefetch_count=1)
			self.channel.connection.process_data_events(None)
			process_flag = True
		except Exception as e:
			logger.info("Error: Rabbitmq consumer can't process data event: %s" % e)

		return process_flag

	def declare_rpc_exchange(self, exchange_name):
		"""
		declares common rpc exchange
		:param exchange_name: name of exchange (project name will be added by this method)
		:return: NoReturn
		"""

		if self.check_connect():
			exchange_name = '{}'.format(exchange_name)
			self.channel.exchange_declare(
				exchange=exchange_name,
				exchange_type='topic',
				durable=True
			)
			logger.info('DECLARED RPC EXCHANGE "{}"'.format(exchange_name))

	def declare_rpc_function_queue(self, function_queue_name, function_routing_key, rpc_exchange_name):
		"""
		declares queue through which RPC will receive function call and to which routing key this queue will be bound
		:param rpc_exchange_name: rpc exchange name (name of project will be added automatically)
		:param function_queue_name: function name (name project will be added automatically)
		:param function_routing_key: routing key to which to bind (name of project will be added auto)
		:return: NoReturn
		"""
		if self.check_connect():
			self.declare_rpc_exchange(rpc_exchange_name)
			rpc_exchange_name = '{}'.format(rpc_exchange_name)
			function_queue_name = '{}'.format(function_queue_name)
			function_routing_key = '{}'.format(function_routing_key)
			self.channel.queue_declare(function_queue_name)
			self.channel.queue_bind(
				exchange=rpc_exchange_name,
				queue=function_queue_name,
				routing_key=function_routing_key
			)
