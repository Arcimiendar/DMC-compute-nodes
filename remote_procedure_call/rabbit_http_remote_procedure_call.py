from remote_procedure_call.rabbit_remote_procedure_call import RabbitRPCFunctionListener
from typing import Optional, Dict
from settings_loader import SettingsLoader
from logs import get_logger
import requests

logger = get_logger(__name__)
settings = SettingsLoader.get_instance()


class RabbitHttpFunctionListener(RabbitRPCFunctionListener):
    def send_return(self, call_properties: Dict[str, str], return_data: bytes, content_type: Optional[str]=None):
        requests.post(settings.web_server.url + settings.web_server.result, return_data)
