from abc import abstractmethod, ABCMeta
from typing import Tuple


class RPCFunctionListenerInterface(object, metaclass=ABCMeta):
	
	def __init__(self, name_of_function, namespace=None):
		self.namespace = namespace
		self.name_of_function = name_of_function
	
	@abstractmethod
	def receive_call(self) -> Tuple[object, bytes]:
		pass

	@abstractmethod
	def send_return(self, call_properties: object, return_data: bytes) -> None:
		pass


class RPCFunctionCallerInterface(object, metaclass=ABCMeta):
	
	def __init__(self, name_of_function, namespace=None):
		self.name_of_function = name_of_function
		self.namespace = namespace
	
	@abstractmethod
	def call(self, params: bytes) -> None:
		pass
	
	@abstractmethod
	def fetch_response(self) -> bytes:
		return b''
