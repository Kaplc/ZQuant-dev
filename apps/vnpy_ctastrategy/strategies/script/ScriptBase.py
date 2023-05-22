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

    def run(self):
        pass

    def load_bars_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ) -> List[BarData]:
        """数据库加载K线"""
        database: BaseDatabase = get_database()

        return database.load_bar_data(
            symbol, exchange, interval, start, end
        )
