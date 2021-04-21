#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# python modules
import os
from typing import Union, Optional

# custom common modules
import logging
import logging.config
import logging.handlers

# current package modules
from settings_loader import SettingsLoader

get_logger_name_func = "get_logger"

previous_settings = {}


def init_logs_settings(log_settings):
    logging.config.dictConfig(log_settings)


class AutoCreateLogDirMixin(logging.Handler):
    def __init__(self, filename, *args, **kwargs):
        self._create_dirs(filename)
        super().__init__(filename, *args, **kwargs)

    def _create_dirs(self, filename):
        dirs = os.path.dirname(filename)
        os.makedirs(dirs, exist_ok=True)


class AutoCreateLogDirHandler(AutoCreateLogDirMixin, logging.FileHandler):
    pass


class CheckLogFileHandlerMixin(logging.Handler):
    def __init__(self, filename, *args, **kwargs):
        service_number = SettingsLoader.get_instance().service_number
        if isinstance(service_number, int):
            filename_tmp = filename.split(".")
            filename_tmp[-2] += f"_{service_number}"
            self._filename = ".".join(filename_tmp)
        else:
            self._filename = filename

        super().__init__(self._filename, *args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        if not os.path.exists(self._filename):
            self.close()
        super().emit(record)


class FolderCreatorFileCheckerRotatingFileHandler(
    AutoCreateLogDirMixin,
    CheckLogFileHandlerMixin,
    logging.handlers.RotatingFileHandler
):
    pass


class LoggerProxy:
    def __init__(self, name: str):
        if previous_settings == {}:
            self._logger = None
            self._name = name
        else:
            self._name = name
            self._logger = logging.getLogger(name)
        
    def __getattribute__(self, item):
        global previous_settings
        logs_settings = SettingsLoader.get_instance().logs
        if previous_settings != logs_settings:
            previous_settings = logs_settings
            init_logs_settings(previous_settings)
        if item in ["_logger", '_name']:
            return super().__getattribute__(item)
        
        if self._logger is None:
            self._logger = logging.getLogger(self._name)
        
        return self._logger.__getattribute__(item)


def get_logger(name: Optional[str] = None) -> Union[logging.Logger, LoggerProxy]:
    return LoggerProxy(name)
