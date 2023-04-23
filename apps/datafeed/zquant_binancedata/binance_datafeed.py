import os
from typing import Dict, List, Set, Optional, Callable
from numpy import ndarray

from core.trader.setting import SETTINGS
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, HistoryRequest
from core.trader.utility import round_to, ZoneInfo
from core.trader.datafeed import BaseDatafeed

from sdk.binance_sdk.binance.download.download_kline import download_daily_klines

from .utility import req_converter


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
        req = req_converter(req)
        save_path = os.path.dirname(os.path.abspath(__file__))
        download_daily_klines(
            trading_type=req.trading_type,
            symbols=req.symbols,
            intervals=req.intervals,
            start_date=req.start_date,
            end_date=req.end_date,
            folder=save_path
        )  # binanceSDK下载历史行情

        pass

    def query_tick_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[TickData]]:
        """查询Tick数据"""
        pass
