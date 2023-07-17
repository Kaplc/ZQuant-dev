import re
from abc import ABC
from datetime import datetime, timedelta
from typing import List

from core.trader.constant import Exchange, Interval
from core.trader.database import BaseDatabase, get_database
from core.trader.object import BarData
from core.trader.utility import BarGenerator


class ZQIntervalConvert:
    """zq to vnpy 周期转换器"""

    value = None  # 值
    unit = None  # 周期单位
    vnInterval = None  # vnpy格式周期

    def __init__(self, interval: str):
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


class ZQKLineGenerator:
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
        for bar in self.src_bars:  # 开始合成
            bar_gnr.update_bar(bar)

        return self.res_bars

    def add_in_res(self, new_bar: BarData):
        new_bar.local_datetime = generator_localtime(new_bar)  # 添加北京时间
        self.res_bars.append(new_bar)


def load_bars_data(
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
):
    """数据库加载K线"""
    # print('正在加载历史数据')
    database: BaseDatabase = get_database()

    return database.load_bar_data(
        symbol, exchange, interval, start, end
    )


class ZQLoadBars:
    """zq加载行情"""

    symbol: str = None
    exchange: Exchange = None
    zq_interval: ZQIntervalConvert = None
    start: datetime = None
    end: datetime = None
    bars = []

    def __init__(self, symbol: str, exchange: Exchange, zq_interval: str, start: datetime, end: datetime):
        # 初始化行情信息
        self.symbol = symbol
        self.exchange = exchange
        self.zq_interval = ZQIntervalConvert(zq_interval)
        self.start = start
        self.end = end

    def load(self):
        # 获取K线原始数据
        src_bars = load_bars_data(
            symbol=self.symbol,
            exchange=self.exchange,
            interval=self.zq_interval.vnInterval,
            start=self.start,
            end=self.end,
        )
        # ZQ K线合成器合成K线
        bar_generator = ZQKLineGenerator(src_bars, self.zq_interval.vnInterval)
        self.bars = bar_generator.start(self.zq_interval.value)  # 开始合成新K线列表
        return self.bars


def generator_localtime(bar):
    # 生成本地时间
    year = bar.datetime.year
    month = bar.datetime.month
    day = bar.datetime.day
    hour = bar.datetime.hour
    minute = bar.datetime.minute

    local_date = datetime(year, month, day, hour, minute) + timedelta(hours=8)
    return local_date


if __name__ == '__main__':
    interval = ZQIntervalConvert("4h")
    pass
