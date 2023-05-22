"""统计K线涨幅数量"""
import re

import matplotlib.pyplot as plt
from typing import List
from datetime import datetime

from apps.vnpy_ctastrategy.backtesting import load_bar_data
from apps.vnpy_ctastrategy.strategies.script.BarGenerator import KLineGenerator
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData

parm = {
    '1m': 1000,
    '1h': 10,
    'd': 10
}


def deal_with_daily(bars: List[BarData]):
    init_dict = {}
    # 先初始化字典
    for num in range(0, 51):
        # key = num / 10
        # next_key = (num + 1) / 10
        key = num
        next_key = (num + 1)
        init_dict[str(key) + '%~' + str(next_key) + '%'] = 0

    for bar in bars:
        # barRangePercentile = (abs(bar.close_price - bar.open_price) / bar.open_price) * 100
        barRangePercentile = (abs(bar.high_price - bar.low_price) / bar.low_price) * 100
        # barRangePercentile = int(barRangePercentile * 10) / 10
        barRangePercentile = int(barRangePercentile)
        next_barRangePercentile = (int(barRangePercentile) + 1)
        key = str(barRangePercentile) + '%~' + str(next_barRangePercentile) + '%'

        if key not in init_dict:
            init_dict[key] = 1
        else:
            init_dict[key] += 1

    # 将字符串键转换为元组形式的键
    new_data = {}
    for k, v in init_dict.items():
        # match = re.match(r'(\d+\.\d+)%~(\d+\.\d+)%', k)
        match = re.match(r'(\d+)%~(\d+)%', k)
        if match:
            new_data[(float(match.group(1)), float(match.group(2)))] = v

    # 按照元组形式的键排序
    sorted_dict = dict(sorted(new_data.items()))

    return sorted_dict


def deal_with_hour(bars: List[BarData]):
    init_dict = {}
    # 先初始化字典
    for num in range(0, 501):
        key = num / 10
        next_key = (num + 1) / 10
        init_dict[str(key) + '%~' + str(next_key) + '%'] = 0

    for bar in bars:
        # barRangePercentile = (abs(bar.close_price - bar.open_price) / bar.open_price) * 100
        barRangePercentile = (abs(bar.high_price - bar.low_price) / bar.low_price) * 100
        barRangePercentile = int(barRangePercentile * 10) / 10
        next_barRangePercentile = (int(barRangePercentile * 10) + 1) / 10
        key = str(barRangePercentile) + '%~' + str(next_barRangePercentile) + '%'

        if key not in init_dict:
            init_dict[key] = 1
        else:
            init_dict[key] += 1

    # 将字符串键转换为元组形式的键
    new_data = {}
    for k, v in init_dict.items():
        match = re.match(r'(\d+\.\d+)%~(\d+\.\d+)%', k)
        if match:
            new_data[(float(match.group(1)), float(match.group(2)))] = v

    # 按照元组形式的键排序
    sorted_dict = dict(sorted(new_data.items()))

    return sorted_dict


def deal_with_minute(bars: List[BarData]):
    init_dict = {}
    for bar in bars:
        # 涨跌幅 = 涨跌额/开盘价
        # barRangePercentile = (abs(bar.close_price - bar.open_price) / bar.open_price) * 100
        barRangePercentile = (abs(bar.high_price - bar.low_price) / bar.low_price) * 100
        barRangePercentile = int(barRangePercentile * 100) / 100
        next_barRangePercentile = (int(barRangePercentile * 100) + 1) / 100
        key = str("{:.3f}".format(barRangePercentile)) + '%~' + str("{:.3f}".format(next_barRangePercentile)) + '%'

        if key not in init_dict:
            init_dict[key] = 1
        else:
            init_dict[key] += 1

    # # 将字典转换为元组列表
    # tuple_list = list(init_dict.items())
    # # 按值大小排序
    # sorted_tuple_list = sorted(tuple_list, key=lambda x: x[1], reverse=True)
    # # 将排序后的元组列表转换为字典
    # sorted_dict = dict(sorted_tuple_list)

    # 将字符串键转换为元组形式的键
    new_data = {}
    for k, v in init_dict.items():
        match = re.match(r'(\d+\.\d+)%~(\d+\.\d+)%', k)
        if match:
            new_data[(float(match.group(1)), float(match.group(2)))] = v

    # 按照元组形式的键排序
    sorted_dict = dict(sorted(new_data.items()))
    return sorted_dict


if __name__ == '__main__':

    start = datetime(2020, 1, 1)
    end = datetime(2023, 5, 20)
    interval = Interval.HOUR
    bar_units = '168h'

    print(f'\n开始读取数据--周期为{interval.value}，数据区间{start}~{end}')
    # 获取历史数据
    bars: List[BarData] = load_bar_data(
        symbol='BTCUSDT',
        exchange=Exchange.BINANCE,
        interval=interval,
        start=start,
        end=end,
    )
    kl_gnr = KLineGenerator(bar_units, bars)
    bars = kl_gnr.start(bars)

    sorted_dict = {}
    if interval.value == 'd':  # 处理日线
        sorted_dict = deal_with_daily(bars)
    elif interval.value == '1h':
        sorted_dict = deal_with_hour(bars)
    else:
        sorted_dict = deal_with_minute(bars)

    total_percent = 0
    percentDict = {}
    is80 = False
    is85 = False
    is90 = False
    is95 = False
    for key in sorted_dict:
        try:
            value = int((sorted_dict[key] / len(bars)) * 1000000) / 10000
        except Exception as e:
            print(e)
            continue
        total_percent += value
        percentDict[key] = str(sorted_dict[key]) + '根-占' + str(value) + '%'

        if total_percent >= 80 and is80 == False:
            is80 = True
            res_percent = str(key[0]) + '%'
            print(f'{bar_units}周期下，超过80%情况的K线幅度：>{res_percent}')
        if total_percent >= 85 and is85 == False:
            is85 = True
            res_percent = str(key[0]) + '%'
            print(f'{bar_units}周期下，超过85%情况的K线幅度：>{res_percent}')
        if total_percent >= 90 and is90 == False:
            is90 = True
            res_percent = str(key[0]) + '%'
            print(f'{bar_units}周期下，超过90%情况的K线幅度：>{res_percent}')
        if total_percent >= 95 and is95 == False:
            is95 = True
            res_percent = str(key[0]) + '%'
            print(f'{bar_units}周期下，超过95%情况的K线幅度：>{res_percent}')

    count = 0
    for res in sorted_dict:
        count += sorted_dict[res]
    barsCount = len(bars)
    pass
