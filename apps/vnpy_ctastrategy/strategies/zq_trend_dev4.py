from datetime import datetime, timedelta
from typing import List
import numpy as np
import matplotlib.pyplot as plt

from apps.vnpy_ctastrategy import CtaTemplate

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, TradeData
from apps.vnpy_ctastrategy.strategies.script.ScriptBase import ZQLoadBars, ZQIntervalConvert, generator_localtime


# class ZQTrendStrategy3:
class ZQTrendStrategy4:

    def check_tar_bar(self, bar: BarData):
        if bar.close_price - bar.open_price >= 0:
            # 阳线
            # 上影线
            upper_hatch_range = ((bar.high_price - bar.close_price) / bar.open_price) * 100
            # 下影线
            lower_hatch_range = ((bar.open_price - bar.low_price) / bar.open_price) * 100
            pass
        else:
            # 阴线
            upper_hatch_range = ((bar.high_price - bar.open_price) / bar.open_price) * 100
            lower_hatch_range = ((bar.close_price - bar.low_price) / bar.open_price) * 100

        if abs(upper_hatch_range) > 0.6:
            print(f"检测到K线, 日期: {bar.local_datetime}, 上影线幅度{upper_hatch_range}")
            pass
        if abs(lower_hatch_range) > 0.6:
            print(f"检测到K线, 日期: {bar.local_datetime}, 下影线幅度{lower_hatch_range}")

            pass
        pass


if __name__ == '__main__':
    bars: List[BarData] = ZQLoadBars(
        symbol="BTCUSDT",
        exchange=Exchange.BINANCE,
        zq_interval="15m",
        start=datetime(2023, 5, 1),
        end=datetime(2023, 7, 15)
    ).load()

    srg4 = ZQTrendStrategy4()

    for bar in bars:
        srg4.check_tar_bar(bar)
