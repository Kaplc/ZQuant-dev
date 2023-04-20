from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Callable

from numpy import ndarray
from pandas import DataFrame
from rqdatac import init
from rqdatac.services.get_price import get_price
from rqdatac.services.future import get_dominant_price
from rqdatac.services.basic import all_instruments
from rqdatac.share.errors import RQDataError

from core.trader.setting import SETTINGS
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, HistoryRequest
from core.trader.utility import round_to, ZoneInfo
from core.trader.datafeed import BaseDatafeed


class BinanceDatafeed(BaseDatafeed):
    """binance数据服务接口"""

    def __init__(self):
        """"""
        self.username: str = SETTINGS["datafeed.username"]
        self.password: str = SETTINGS["datafeed.password"]

        self.inited: bool = False
        self.symbols: ndarray = None

    def init(self, output: Callable = print) -> bool:
        """初始化"""
        pass

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """查询K线数据"""
        pass

    def _query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """查询K线数据"""
        pass

    def query_tick_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[TickData]]:
        """查询Tick数据"""
        pass

    def _query_dominant_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[BarData]]:
        """查询期货主力K线数据"""
        pass
