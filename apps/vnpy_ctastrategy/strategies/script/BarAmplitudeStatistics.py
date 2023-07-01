"""统计K线涨幅数量"""
import re

import matplotlib.pyplot as plt
from typing import List
from datetime import datetime

from apps.vnpy_ctastrategy.strategies.script.ScriptBase import ScriptBase, ZQInterval, KLineGenerator
from apps.vnpy_ctastrategy.backtesting import load_bar_data
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData

parm = {
    '1m': 1000,
    '1h': 10,
    'd': 10
}


class BAS(ScriptBase):
    """统计K线涨幅数量"""

    def __init__(self, symbol: str, exchange: Exchange, start: datetime, end: datetime):
        super().__init__()

        self.symbol: str = symbol
        self.exchange: Exchange = exchange
        self.start: datetime = start
        self.end: datetime = end
        self.bars: List[BarData] = []
        self.zq_interval = None
        self.res_dict = None

    def run(self, interval):

        self.zq_interval = ZQInterval(interval)

        # 获取K线原始数据
        self.bars = self.load_bars_data(
            symbol=self.symbol,
            exchange=self.exchange,
            interval=self.zq_interval.vnInterval,
            start=self.start,
            end=self.end,
        )
        # 获取K线合成器
        self.get_generator(self.bars)
        self.bars = self.bar_generator.start(self.zq_interval.value)  # 合成新K线列表

        # 先初始化字典格式
        self.res_dict = self.init_resDict()

        for bar in self.bars:
            barRangePercentile = (abs(bar.close_price - bar.open_price) / bar.open_price) * 100
            # barRangePercentile = (abs(bar.high_price - bar.low_price) / bar.low_price) * 100
            barRangePercentile = int(barRangePercentile * 10) / 10
            next_barRangePercentile = (int(barRangePercentile * 10) + 1) / 10
            key = str(barRangePercentile) + '%~' + str(next_barRangePercentile) + '%'

            if key not in self.res_dict:
                self.res_dict[key] = 1
            else:
                self.res_dict[key] += 1

        # 将字符串键转换为元组形式的键
        new_data = {}
        for k, v in self.res_dict.items():
            match = re.match(r'(\d+\.\d+)%~(\d+\.\d+)%', k)
            if match:
                new_data[(float(match.group(1)), float(match.group(2)))] = v

        # 按照元组形式的键排序
        self.res_dict = dict(sorted(new_data.items()))

        self.print_res(self.res_dict)

    def print_res(self, sorted_dict):
        """打印结果"""
        total_percent = 0
        percentDict = {}
        is80 = False
        is85 = False
        is90 = False
        is95 = False
        for key in sorted_dict:
            try:
                value = int((sorted_dict[key] / len(self.bars)) * 1000000) / 10000
            except Exception as e:
                print(e)
                continue
            total_percent += value
            percentDict[key] = str(sorted_dict[key]) + '根-占' + str(value) + '%'

            if total_percent >= 80 and is80 == False:
                is80 = True
                res_percent = str(key[0]) + '%'
                print(f'{self.zq_interval}周期下，超过80%情况的K线幅度：>{res_percent}')
            if total_percent >= 85 and is85 == False:
                is85 = True
                res_percent = str(key[0]) + '%'
                print(f'{self.zq_interval}周期下，超过85%情况的K线幅度：>{res_percent}')
            if total_percent >= 90 and is90 == False:
                is90 = True
                res_percent = str(key[0]) + '%'
                print(f'{self.zq_interval}周期下，超过90%情况的K线幅度：>{res_percent}')
            if total_percent >= 95 and is95 == False:
                is95 = True
                res_percent = str(key[0]) + '%'
                print(f'{self.zq_interval}周期下，超过95%情况的K线幅度：>{res_percent}')
        print('==========================================')

    def init_resDict(self):

        init_dict = {}
        if self.zq_interval.unit == 'd':  # 处理日线
            for num in range(0, 51):
                # key = num / 10
                # next_key = (num + 1) / 10
                key = num
                next_key = (num + 1)
                init_dict[str(key) + '%~' + str(next_key) + '%'] = 0

        elif self.zq_interval.unit == 'h' or self.zq_interval.unit == 'm':
            for num in range(0, 501):
                key = num / 10
                next_key = (num + 1) / 10
                init_dict[str(key) + '%~' + str(next_key) + '%'] = 0
        return init_dict

    def get_generator(self, bars):
        """获取K线合成器"""
        self.bar_generator = KLineGenerator(bars=bars,  vn_interval=self.zq_interval.vnInterval)


if __name__ == '__main__':
    bas = BAS(
        symbol='BTCUSDT',
        exchange=Exchange.BINANCE,
        start=datetime(2020, 1, 1),
        end=datetime(2023, 6, 1)
    )
    bas.run('1h')
    bas.run('4h')
    bas.run('6h')
    bas.run('24h')
    pass

