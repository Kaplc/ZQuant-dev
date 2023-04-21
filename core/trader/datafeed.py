from abc import ABC
from types import ModuleType
from typing import Optional, List, Callable
from importlib import import_module

from .object import HistoryRequest, TickData, BarData
from .setting import SETTINGS


class BaseDatafeed(ABC):
    """
    Abstract datafeed class for connecting to different datafeed.
    回测数据库抽象类
    """

    def init(self, output: Callable = print) -> bool:
        """
        Initialize datafeed service connection.
        """
        pass

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """
        Query history bar data.
        """
        pass

    def query_tick_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[TickData]]:
        """
        Query history tick data.
        """
        pass


datafeed: BaseDatafeed = None


def get_datafeed() -> BaseDatafeed:
    """服务器数据服务"""
    # Return datafeed object if already inited
    global datafeed
    if datafeed:
        return datafeed

    # Read datafeed related global setting
    datafeed_name: str = SETTINGS["datafeed.name"]
    module_name: str = f"apps.datafeed.{datafeed_name}"

    # Try to import datafeed module
    try:
        module: ModuleType = import_module(module_name)
        print(f"\n使用{datafeed_name}数据服务")
    except ModuleNotFoundError:
        print(f"找不到数据服务驱动{module_name}，使用默认的RQData数据服务")
        module: ModuleType = import_module("apps.datafeed.zquant_binancedata")

    # Create datafeed object from module
    datafeed = module.Datafeed()
    return datafeed
