import os
from typing import Dict, List, Set, Optional, Callable
from numpy import ndarray

from core.trader import setting
from core.trader.setting import SETTINGS
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, HistoryRequest
from core.trader.utility import round_to, ZoneInfo
from core.trader.datafeed import BaseDatafeed

from sdk.binance_sdk.binance.download.download_kline import download_daily_klines

from .utility import req_converter, unzip_to_csv, import_data_from_csv


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
        converted_req = req_converter(req)
        save_path = os.path.dirname(os.path.abspath(__file__))
        # binanceSDK下载历史行情
        unzip_path = download_daily_klines(
            trading_type=converted_req.trading_type,
            symbols=converted_req.symbols,
            intervals=converted_req.intervals,
            start_date=converted_req.start_date,
            end_date=converted_req.end_date,
            folder=save_path,
        )

        if unzip_path:
            output('网络可能出现异常!')
            return []
        # 批量解压zip成csv
        unzip_to_csv(unzip_path, output)
        # 批量加载csv
        data: List[BarData] = import_data_from_csv(
            folder_path=unzip_path,
            symbol=req.symbol,
            exchange=req.exchange,
            interval=req.interval,
            tz_name=SETTINGS['timezone'],
            datetime_head='open_time',
            open_head='open',
            high_head='high',
            low_head='low',
            close_head='close',
            volume_head='volume',
            turnover_head='quote_volume',
            open_interest_head='open_interest',
            datetime_format='%Y-%m-%d %H:%M:%S'
        )
        return data

    def query_tick_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[TickData]]:
        """查询Tick数据"""
        pass

    