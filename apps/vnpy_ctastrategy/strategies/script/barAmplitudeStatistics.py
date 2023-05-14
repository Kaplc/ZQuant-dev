"""统计K线涨幅数量"""
import matplotlib.pyplot as plt
from typing import List
from datetime import datetime

from apps.vnpy_ctastrategy.backtesting import load_bar_data
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData

if __name__ == '__main__':
    start = datetime(2023, 5, 1)
    end = datetime(2023, 5, 12)
    print(f'读取数据{start}~{end}')
    # 获取历史数据
    bars: List[BarData] = load_bar_data(
        symbol='BTCUSDT',
        exchange=Exchange.BINANCE,
        interval=Interval.MINUTE,
        start=start,
        end=end,
    )

    resDict = {}

    for bar in bars:
        # 涨跌幅 = 涨跌额/开盘价
        barRange = ((bar.close_price - bar.open_price) / bar.open_price) * 100
        resDict[str(int(barRange))] += 1

    pass
