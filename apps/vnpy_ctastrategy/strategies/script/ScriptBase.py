import re
from abc import ABC
from datetime import datetime
from typing import List

from core.trader.constant import Exchange, Interval
from core.trader.database import BaseDatabase, get_database
from core.trader.object import BarData


class ScriptBase(ABC):
    """脚本的基类"""

    def __init__(self):
        pass

    def load_bars_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ):
        """数据库加载K线"""
        database: BaseDatabase = get_database()

        return database.load_bar_data(
            symbol, exchange, interval, start, end
        )


class ZQInterval:

    def __init__(self, interval):
        self.value = None
        self.unit = None
        self.vnInterval = None

        self.convert(interval)

    def convert(self, interval):

        self.value = int(re.search(r'\d+', interval).group())
        self.unit = re.search(r'[a-zA-Z]', interval).group()

        if self.unit == 'm':
            self.vnInterval = Interval.MINUTE
        elif self.unit == 'h':
            self.vnInterval = Interval.HOUR
        elif self.unit == 'd':
            self.vnInterval = Interval.DAILY
        else:
            self.vnInterval = Interval.TICK

    def __str__(self):
        return str(self.value) + self.unit
