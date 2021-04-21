# -*- coding: utf-8 -*-
import os
import json
import uuid
from settings_loader.settings_object import SettingsObject
from typing import Optional, Any, Dict, Union, Callable

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

	def __init__(self):
		if SettingsLoader.__instance is not None:
			raise ValueError("Use get_instance class methode to get SettingsLoader")
		self._service_id = str(uuid.uuid4())
		self._default_settings = None
		self.reload_settings()

	@classmethod
	def get_instance(cls) -> 'SettingsLoader':
		if not cls.__instance:
			cls.__instance = SettingsLoader()
		return cls.__instance

	def reload_settings(self):
		source_file = os.environ.get('SETTINGS', DEFAULT_CONFIG_FILE_PATH)
		config_json = self.read_json_file(source_file)
		default_settings = config_json
		self._default_settings = default_settings or {}

	def get_attribute_value(self, settings_attribute_name, default_value=None):
		value = None
		if self._default_settings:
			value = self._default_settings.get(settings_attribute_name, None)
		if not value:
			value = default_value
		return value

	def read_json_file(self, path):
		with open(path) as json_file:
			data = json.load(json_file)
		return data

	@property
	def service_id(self) -> str:
		return self._service_id

	logs: Dict[str, Union[Dict[str, Union[Dict[str, Any], Any]], int]] = \
		SettingsAttribute(default_value={}, map_function=None)

	rabbitmq: Any = SettingsAttribute(default_value=initialize_settings_object({}))

	error_policy: Any = SettingsAttribute(default_value=initialize_settings_object({"ignore_all": True}))

	algorithm_storage_backend: Any = SettingsAttribute(
		default_value=initialize_settings_object({"type": "temporary_storage", "config": {}})
	)
