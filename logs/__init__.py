from typing import Type, Callable, Optional
from logging import Logger
import Libs.logs.log_main as logs
Logs: Type[logs.class_name] = getattr(logs, logs.class_name)
get_logger: Callable[[Optional[str]], Logger] = getattr(logs, logs.get_logger_name_func)
