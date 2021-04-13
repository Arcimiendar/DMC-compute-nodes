import sys
from abc import abstractmethod, ABCMeta


if sys.version_info.major > 2:
	from typing import Tuple, Dict, NoReturn


class RPCFunctionListenerInterface(object, metaclass=ABCMeta):
	
	def __init__(self, logs, name_of_function, namespace=None):
		self.logs = logs
		self.namespace = namespace
		self.name_of_function = name_of_function
	
	@abstractmethod
	def receive_call(self):
		# type: () -> Tuple[Dict[str, str], bytes]
		pass

	@abstractmethod
	def send_return(self, call_properties, return_data):
		# type: (Dict[str, str], bytes) -> NoReturn
		pass


class RPCFunctionCallerInterface(object, metaclass=ABCMeta):
	
	def __init__(self, logs, name_of_function, namespace=None):
		self.logs = logs
		self.name_of_function = name_of_function
		self.namespace = namespace
	
	@abstractmethod
	def call(self, params):
		# type: (bytes) -> None
		pass
	
	@abstractmethod
	def fetch_response(self):
		# type: () -> bytes
		return b''
