import re
from datetime import datetime
from enum import Enum
from typing import List

from apps.vnpy_ctastrategy.backtesting import load_bar_data
from apps.vnpy_ctastrategy.strategies.script.ScriptBase import ZQInterval
from core.trader.constant import Interval, Exchange
from core.trader.object import BarData
from core.trader.utility import BarGenerator

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
