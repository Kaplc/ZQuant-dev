"""统计竖向成交量分布"""
import os
import subprocess

import matplotlib.pyplot as plt
from typing import List
from datetime import datetime

from apps.vnpy_ctastrategy.backtesting import load_bar_data
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData

if __name__ == '__main__':
    start = datetime(2021, 11, 1)
    end = datetime(2022, 12, 1)
    print(f'读取数据{start}~{end}')
    # 获取历史数据
    bars: List[BarData] = load_bar_data(
        symbol='BTCUSDT',
        exchange=Exchange.BINANCE,
        interval=Interval.MINUTE,
        start=start,
        end=end,
    )
    print('计算数据.')
    # 生成区间字典
    price_region_dict = {}
    total_region_start = 0
    total_region_end = 100000
    step = 99
    current_price = 0
    last_price = 0
    while current_price <= 100000:
        current_price += step
        key = str(last_price) + '-' + str(current_price)
        price_region_dict[key] = 0

        current_price += 1
        last_price = current_price

    # 遍历K线
    for bar in bars:

        bar_price_region = bar.high_price - bar.low_price
        price_region_start = (bar.low_price // 100) * 100
        price_region_end = (bar.high_price // 100) * 100
        if price_region_start == price_region_end:
            price_region_dict[str(int(price_region_start)) + '-' + str(int(price_region_start + step))] += bar.volume
        else:
            # 两头未填满价格区间的价格范围
            start_rest = bar.low_price % 100
            end_rest = bar.high_price % 100
            # 两头区间占价格区间的百分比
            pct_start_rest = start_rest / bar_price_region / 100
            pct_end_rest = end_rest / bar_price_region / 100
            # 按百分比分配交易量
            start_region_vol = bar.volume * pct_start_rest
            end_region_vol = bar.volume * pct_end_rest
            blocks_num = (bar_price_region - (step + 1 - start_rest) - end_rest) // (step + 1)  # 中间块数
            if blocks_num > 0:
                each_block_vol = (bar.volume - start_region_vol - end_region_vol) / blocks_num
                current_price = price_region_start + step + 1
                last_price = price_region_start + step + 1
                current_block = 1
                while current_block <= blocks_num:
                    current_price += step
                    price_region_dict[str(int(last_price)) + '-' + str(int(current_price))] += each_block_vol

                    current_price += 1
                    last_price = current_price

                    current_block += 1

            price_region_dict[
                str(int(price_region_start)) + '-' + str(int(price_region_start + step))] += start_region_vol
            price_region_dict[str(int(price_region_end)) + '-' + str(int(price_region_end + step))] += end_region_vol

    print('生成柱状图.')
    price_dict = {k: v for k, v in price_region_dict.items() if v != 0}

    plt.figure(figsize=(10, len(price_dict)//5))
    plt.barh(list(price_dict.keys()), list(price_dict.values()))
    plt.xticks(range(len(price_dict)), [str(key) + ' ' for key in price_dict.keys()], rotation=90)
    save_path = f"/home/kaplc/Desktop/price_vol_picture/{start.strftime('%Y-%m-%d')}~{end.strftime('%Y-%m-%d')}.png"
    plt.savefig(save_path, dpi=100)
    print('生成完毕.')
    pass
