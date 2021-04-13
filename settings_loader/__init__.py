from typing import Type
import Libs.settings_loader.s_loader_main as s_loader_main
from Libs.settings_loader.s_loader_main import initialize_settings_object

SettingsLoader: Type[s_loader_main.class_name] = getattr(s_loader_main, s_loader_main.class_name)
