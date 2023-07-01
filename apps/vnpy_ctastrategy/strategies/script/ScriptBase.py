import re
from abc import ABC
from datetime import datetime
from typing import List

from core.trader.constant import Exchange, Interval
from core.trader.database import BaseDatabase, get_database
from core.trader.object import BarData
from core.trader.utility import BarGenerator


class KLineGenerator:
    """zq框架K线合成器"""

    def __init__(self, bars: list[BarData], vn_interval):
        self.vn_interval = vn_interval  # vnpy的时间周期
        self.res_bars = []  # 合成结果
        self.src_bars = bars  # 源数据

    def start(self, bar_units):
        bar_gnr = BarGenerator(
            on_bar=None,  # 处理新的K线数据的回调函数
            window=bar_units,  # 要用多少根K线合成
            on_window_bar=self.add_in_res,  # 处理窗口K线数据的回调函数
            interval=self.vn_interval  # K线数据的时间间隔
        )
        for bar in self.src_bars:
            bar_gnr.update_bar(bar)

        return self.res_bars

    def add_in_res(self, new_bar):
        self.res_bars.append(new_bar)


class ScriptBase(ABC):
    """脚本的基类"""

    bars = []

    def __init__(self, symbol: str, exchange: Exchange, zq_interval: str, start: datetime, end: datetime):
        # 初始化行情数据
        self.bars = self.zq_load_bars(
            symbol,
            exchange,
            zq_interval,
            start,
            end
        )
        pass

    def zq_load_bars(self, symbol: str, exchange: Exchange, zq_interval: str, start: datetime, end: datetime) -> list:
        zq_interval = ZQInterval(zq_interval)

        # 获取K线原始数据
        bars = self.load_bars_data(
            symbol=symbol,
            exchange=exchange,
            interval=zq_interval.vnInterval,
            start=start,
            end=end,
        )
        # ZQ K线合成器合成K线
        bar_generator = KLineGenerator(bars, zq_interval.vnInterval)
        bars = bar_generator.start(zq_interval.value)  # 合成新K线列表
        return bars

    def load_bars_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ):
        """数据库加载K线"""
        print('正在加载历史数据')
        database: BaseDatabase = get_database()

        return database.load_bar_data(
            symbol, exchange, interval, start, end
        )


class ZQInterval:

    def __init__(self, interval: str):
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
