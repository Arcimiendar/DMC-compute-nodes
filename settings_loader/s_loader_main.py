# -*- coding: utf-8 -*-
import sys
import os
import json
from Libs.settings_loader.settings_object import SettingsObject
from typing import Optional, Any, Dict, Union, Callable

class_name = "SettingsLoader"
DEFAULT_CONFIG_FILE_NAME = "settings.json"
DEFAULT_CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), DEFAULT_CONFIG_FILE_NAME)
DEFAULT_SETTINGS_LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'SETTINGS_WARNINGS.log')



def initialize_settings_object(setting_attr):
	if not isinstance(setting_attr, dict):
		return setting_attr

	settings_object = SettingsObject()
	for key, val in setting_attr.items():
		if isinstance(setting_attr[key], dict):
			val = initialize_settings_object(setting_attr[key])
		setattr(settings_object, key, val)
	
	return settings_object


class SettingsAttribute:
	def __init__(
		self, settings_attribute_name: Optional[str] = '', default_value: Optional[Any] = None,
		map_function: Optional[Callable[[Any], Any]] = initialize_settings_object
	):
		self.settings_attribute_name = settings_attribute_name
		self.default_value = default_value
		self._value = None
		self.map_function = map_function
	
	def get_getter(self):
		def getter(setting_loader: 'SettingsLoader'):
			if not self._value:
				value = setting_loader.get_attribute_value(self.settings_attribute_name, self.default_value)
				if self.map_function:
					value = self.map_function(value)
				self._value = value
			return self._value
		return getter

	def clear(self):
		self._value = None


class SettingsLoaderMetaClass(type):
	def __new__(mcs, name, bases, dct: dict):
		settings_attributes = []
		for key, item in dct.items():
			if isinstance(item, SettingsAttribute):
				if item.settings_attribute_name == '':
					item.settings_attribute_name = key
				settings_attributes.append(item)
				dct[key] = property(item.get_getter())
		
		def clean_out_class_attribute(self):
			for settings_attribute in settings_attributes:
				settings_attribute.clear()
		
		dct['clean_out_class_attribute'] = clean_out_class_attribute
		cls = super().__new__(mcs, name, bases, dct)
		return cls


class SettingsLoader(object, metaclass=SettingsLoaderMetaClass):
	__instance = None

	def __init__(self, service_name, service_number=None):
		if SettingsLoader.__instance is not None:
			raise ValueError("Use get_instance class methode to get SettingsLoader")

		self.python_version = sys.version_info.major
		self._service_name = service_name
		self._service_number = service_number
		self._default_settings = None
		self._service_settings = None
		# self.logs = logs
		self.reload_settings()

	@classmethod
	def get_instance(cls, service_name=None, service_number=None) -> 'SettingsLoader':
		if not cls.__instance:
			cls.__instance = SettingsLoader(service_name=service_name, service_number=None)
		if service_name is not None:
			cls.__instance._service_name = service_name
			cls.__instance._service_number = service_number
			cls.__instance.reload_settings()
		return cls.__instance

	def clean_out_class_attribute(self):
		pass

	def reload_settings(self, source_file=None):
		"""
		Reread settings. Clear entered param if it is, or all params if clear_param == None
		@return: NoReturn
		"""

		if source_file:
			config_json = self.read_json_file(source_file)
			default_settings = config_json['common']
			self._default_settings = default_settings or {}
		elif self._service_name:
			config_json = self.read_json_file(DEFAULT_CONFIG_FILE_PATH)
			default_settings = config_json['common']
			self._default_settings = default_settings or {}
			service_settings = config_json.get(self._service_name)
			self._service_settings = service_settings or {}
		else:
			config_json = self.read_json_file(DEFAULT_CONFIG_FILE_PATH)
			default_settings = config_json['common']
			self._default_settings = default_settings or {}

		self.clean_out_class_attribute()

	def read_json_file(self, path):
		with open(path) as json_file:
			data = json.load(json_file)
		return data

	def get_attribute_value(self, settings_attribute_name, default_value=None):
		"""
		:param settings_attribute_name:
		:param default_value:
		:return: value
		"""

		value = None
		if self._service_settings:
			value = self._service_settings.get(settings_attribute_name, None)
		if not value:
			value = self._default_settings.get(settings_attribute_name, None)
		if not value:
			# self.logs.trace(f"No {settings_attribute_name} attribute. Will use default value '{default_value}'")
			with open(DEFAULT_SETTINGS_LOG_FILE_PATH, 'a') as f:
				f.write(f"No {settings_attribute_name} attribute. Will use default value '{default_value}'\n\r")
			value = default_value
		return value

	@property
	def process_name(self):
		return self._service_name
	
	@property
	def service_number(self):
		return self._service_number

	@property
	def service_name(self):
		return self._service_name

	@property
	def service_name_full(self):
		return f"{self._service_name}_{self._service_number}" \
			if isinstance(self._service_number, int) else self._service_name
	
	project_name: str = SettingsAttribute(default_value='gelios')
	service_settings = SettingsAttribute(default_value=initialize_settings_object({}))
	logs: Dict[str, Union[Dict[str, Union[Dict[str, Any], Any]], int]] = \
		SettingsAttribute(default_value={}, map_function=None)
	
	db_reconnections_count: int = SettingsAttribute(default_value=5)
	db_reconnection_time: int = SettingsAttribute(default_value=5)
	pg_system_db = SettingsAttribute(
		default_value=initialize_settings_object({
			"conn1": {},
			"reconnection_count": 3,
			"reconnection_time": 1,
			"conn_order_for_write": ["conn1"],
			"conn_order_for_read": ["conn1"],
		})
	)
	pg_online_db = SettingsAttribute(default_value=initialize_settings_object({}))
	pg_storage_db = SettingsAttribute(
		default_value=initialize_settings_object({
			"master": {},
			"slave1": {},
			"max_objects_in_storage": 400,
			"partitions_range": 14,  # month count
			"reconnection_count": 5,
			"reconnection_time": 5
		})
	)

	# --- for MongoDB ---
	reports_db: Dict[str, Any] = SettingsAttribute(default_value={})
	# --- for MongoDB --
	
	redis_cache_for_transfer: dict = SettingsAttribute(default_value={})

	# ----- for reports module ---------------------
	clear_unfinished_reports: bool = SettingsAttribute(default_value=True)
	split_periods_by_time_duration: int = SettingsAttribute(default_value=3600 * 24 * 7)  # one week
	# ----- end settings for reports module ---------------------

	rabbitmq = SettingsAttribute(
		default_value=initialize_settings_object({
			"master": {},
			"reconnections_count": 5,
			"reconnections_time": 5
		})
	)
	
	redis = SettingsAttribute(default_value=initialize_settings_object({}))

	sensors = SettingsAttribute(
		default_value=initialize_settings_object({
			"count_process_limit": 2,
			"min_msgs_count_for_process": 30000,
		})
	)

	# ----- DataTransfer service ---------------------
	clickhouse_storage_db = SettingsAttribute(
		default_value=initialize_settings_object({
			"master": {},
			"slave1": {},
			"reconnection_count": 5,
			"reconnection_time": 5,
			"cluster_name": None,
		})
	)
	clickhouse_storage_db_test = SettingsAttribute(default_value=initialize_settings_object({}))

	# ----- next service ---------------------
