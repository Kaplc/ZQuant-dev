import re
from datetime import datetime
from enum import Enum
from typing import List

from apps.vnpy_ctastrategy.backtesting import load_bar_data
from apps.vnpy_ctastrategy.strategies.script.ScriptBase import ZQInterval
from core.trader.constant import Interval, Exchange
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
