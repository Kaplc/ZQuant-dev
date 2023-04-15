from abc import ABC, abstractmethod
from datetime import datetime
from types import ModuleType
from typing import List
from dataclasses import dataclass
from importlib import import_module

from .constant import Interval, Exchange
from .object import BarData, TickData
from .setting import SETTINGS
from .utility import ZoneInfo


DB_TZ = ZoneInfo(SETTINGS["database.timezone"])


def convert_tz(dt: datetime) -> datetime:
    """
    Convert timezone of datetime object to DB_TZ.
    转换时区
    """
    dt: datetime = dt.astimezone(DB_TZ)
    return dt.replace(tzinfo=None)


@dataclass
class BarOverview:
    """
    Overview of bar data stored in database.
    K线数据总览对象
    """

    symbol: str = ""
    exchange: Exchange = None
    interval: Interval = None
    count: int = 0
    start: datetime = None
    end: datetime = None


@dataclass
class TickOverview:
    """
    Overview of tick data stored in database.
    Tick数据总览对象
    """

    symbol: str = ""
    exchange: Exchange = None
    count: int = 0
    start: datetime = None
    end: datetime = None


class BaseDatabase(ABC):
    """
    Abstract database class for connecting to different database.
    基础数据库对象
    """

    @abstractmethod
    def save_bar_data(self, bars: List[BarData], stream: bool = False) -> bool:
        """
        Save bar data into database.
        保存K线到数据库
        """
        pass

    @abstractmethod
    def save_tick_data(self, ticks: List[TickData], stream: bool = False) -> bool:
        """
        Save tick data into database.
        保存tick
        """
        pass

    @abstractmethod
    def load_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ) -> List[BarData]:
        """
        Load bar data from database.
        加载K线
        """
        pass

    @abstractmethod
    def load_tick_data(
            self,
            symbol: str,
            exchange: Exchange,
            start: datetime,
            end: datetime
    ) -> List[TickData]:
        """
        Load tick data from database.
        加载tick
        """
        pass

    @abstractmethod
    def delete_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval
    ) -> int:
        """
        Delete all bar data with given symbol + exchange + interval.
        删除K线
        """
        pass

    @abstractmethod
    def delete_tick_data(
            self,
            symbol: str,
            exchange: Exchange
    ) -> int:
        """
        Delete all tick data with given symbol + exchange.
        删除tick
        """
        pass

    @abstractmethod
    def get_bar_overview(self) -> List[BarOverview]:
        """
        Return bar data avaible in database.
        
        """
        pass

    @abstractmethod
    def get_tick_overview(self) -> List[TickOverview]:
        """
        Return tick data avaible in database.
        """
        pass


# 初始化database
database: BaseDatabase = None


def get_database() -> BaseDatabase:
    """获取数据库对象"""
    # Return database object if already inited
    global database
    if database:
        return database

    # Read database related global setting 从配置文件读取数据库配置
    database_name: str = SETTINGS["database.name"]
    module_name: str = f"apps.database.vnpy_{database_name}"

    # Try to import database module 导入数据库模块
    try:
        module: ModuleType = import_module(module_name)
    except ModuleNotFoundError:
        print(f"找不到数据库驱动{module_name}，使用默认的SQLite数据库")
        module: ModuleType = import_module("vnpy_sqlite")

    # Create database object from module 创建数据库对象并返回
    database = module.Database()
    return database
