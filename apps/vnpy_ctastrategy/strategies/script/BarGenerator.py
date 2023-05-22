import re
from datetime import datetime
from enum import Enum
from typing import List

from apps.vnpy_ctastrategy.backtesting import load_bar_data
from core.trader.constant import Interval, Exchange
from core.trader.object import BarData
from core.trader.utility import BarGenerator


class KLineGenerator:
    """zq框架K线合成器"""

    def __init__(self, interval: str, bars: list[BarData]):
        self.vn_interval = None  # vnpy的时间周期
        self.bar_units = None  # 合成单位
        self.res_bars = []  # 合成结果

        self.cov_vn_interval(interval)

    def start(self, bars):
        bar_gnr = BarGenerator(
            on_bar=None,  # 处理新的K线数据的回调函数
            window=self.bar_units,  # 要用多少根K线合成
            on_window_bar=self.add_in_res,  # 处理窗口K线数据的回调函数
            interval=self.vn_interval  # K线数据的时间间隔
        )
        for bar in bars:
            bar_gnr.update_bar(bar)

        return self.res_bars

    def add_in_res(self, new_bar):
        self.res_bars.append(new_bar)

    def cov_vn_interval(self, interval: str):
        self.bar_units = int(re.search(r'\d+', interval).group())
        interval = re.search(r'[a-zA-Z]', interval).group()
        self.vn_interval = Interval.TICK
        if interval == 'm':
            self.vn_interval = Interval.MINUTE
        elif interval == 'h':
            self.vn_interval = Interval.HOUR


if __name__ == '__main__':
    start = datetime(2023, 5, 1)
    end = datetime(2023, 5, 20)
    interval = Interval.MINUTE
    print(f'\n开始读取数据--周期为{interval.value}，数据区间{start}~{end}')
    # 获取历史数据
    bars: List[BarData] = load_bar_data(
        symbol='BTCUSDT',
        exchange=Exchange.BINANCE,
        interval=interval,
        start=start,
        end=end,
    )

    pass
