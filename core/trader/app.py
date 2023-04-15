from abc import ABC
from pathlib import Path
from typing import Type, TYPE_CHECKING


if TYPE_CHECKING:
    from .engine import BaseEngine


class BaseApp(ABC):
    """
    Absstract class for app.
    app类
    """

    app_name: str = ""                          # Unique name used for creating engine and widget 用于创建引擎和小部件的唯一名称
    app_module: str = ""                        # App module string used in import_module import_module中使用的应用程序模块字符串
    app_path: Path = ""                         # Absolute path of app folder 应用程序文件夹的绝对路径
    display_name: str = ""                      # Name for display on the menu. 显示在菜单上的名称
    engine_class: Type["BaseEngine"] = None     # App engine class 应用程序引擎类
    widget_name: str = ""                       # Class name of app widget 应用程序小部件的类名
    icon_name: str = ""                         # Icon file name of app widget 应用程序小部件的图标文件名
