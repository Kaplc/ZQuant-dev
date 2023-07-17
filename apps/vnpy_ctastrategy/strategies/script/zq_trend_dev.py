from datetime import datetime, timedelta
from typing import List
import numpy as np
import matplotlib.pyplot as plt

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData
from ScriptBase import ScriptBase


def generator_localtime(bar):
    # 生成本地时间
    y = bar.datetime.year
    m = bar.datetime.month
    d = bar.datetime.day

    h = bar.datetime.hour
    return datetime(y, m, d, h) + timedelta(hours=8)


class ZQTrendStrategy1(ScriptBase):
    """zq趋势策略dev"""

    def __init__(self, zq_interval: str, tar_range, hor_range):
        super().__init__()
        self.tar_range = tar_range
        self.hor_range = hor_range
        self.tar_bar: BarData = None
        self.symbol = 'BTCUSDT',
        self.exchange = Exchange.BINANCE

        self.bars: List[BarData] = self.zq_load_bars(
            symbol=self.symbol,
            exchange=self.exchange,
            zq_interval=zq_interval,
            start=datetime(2023, 1, 1),
            end=datetime(2023, 6, 1)
        )
        self.hor_bars: List[BarData] = []

    def get_horizontal(self, tar_bar, tar_range):
        """获取横盘区间"""
        start_date = datetime(
            tar_bar.datetime.year,
            tar_bar.datetime.month,
            tar_bar.datetime.day
        ) - timedelta(days=1)

        end_date = datetime(
            tar_bar.datetime.year,
            tar_bar.datetime.month,
            tar_bar.datetime.day,
            tar_bar.datetime.hour
        )

        # 获取横盘区间
        while 1:
            # 获取横盘区间数据
            hor_bars: List[BarData] = self.zq_load_bars(
                symbol=self.symbol,
                exchange=self.exchange,
                zq_interval='1h',
                start=start_date,
                end=end_date
            )
            # 判断当前数据是否是横盘
            open_price = hor_bars[0].open_price
            close_price = hor_bars[-1].close_price
            hor_range = abs(close_price - open_price) / open_price * 100

            # print(f'{generator_localtime(hor_bars[0])} ~ {generator_localtime(hor_bars[-1])} 幅度为{hor_range}')
            if hor_range >= tar_range:
                break
            # 是横盘就继续+时间步长继续判断
            start_date -= timedelta(hours=1)  # 每次循环步长

        return hor_bars

    def check_horizontal(self, hor_bars: List[BarData], tar_range):
        """反向校验横盘"""
        # print('开始校验横盘区间')
        end_date = datetime(
            self.tar_bar.datetime.year,
            self.tar_bar.datetime.month,
            self.tar_bar.datetime.day,
            self.tar_bar.datetime.hour
        )

        check_start_date = datetime(
            hor_bars[0].datetime.year,
            hor_bars[0].datetime.month,
            hor_bars[0].datetime.day,
            hor_bars[0].datetime.hour
        )

        check_end_date = check_start_date + timedelta(hours=1)

        # 反向获取横盘区间数据并校验
        while 1:
            check_hor_bars: List[BarData] = self.zq_load_bars(
                symbol=self.symbol,
                exchange=self.exchange,
                zq_interval='1h',
                start=check_start_date,
                end=check_end_date
            )

            # 判断当前数据是否是横盘
            open_price = check_hor_bars[0].open_price
            close_price = check_hor_bars[-1].close_price
            hor_range = abs(close_price - open_price) / open_price * 100

            # print(
            #     f'{generator_localtime(check_hor_bars[0])} ~ {generator_localtime(check_hor_bars[-1])} 幅度为{hor_range}')

            if hor_range >= tar_range:
                # print('去除校验失败部分')
                check_start_date = check_end_date
                if end_date == check_start_date:
                    end_date += timedelta(hours=1)
                # print('校验完成')
                return self.zq_load_bars(
                    symbol=self.symbol,
                    exchange=self.exchange,
                    zq_interval='1h',
                    start=check_start_date,
                    end=end_date
                )

            # 是横盘就继续+时间步长继续判断
            check_end_date += timedelta(hours=1)  # 每次循环步长

    def check_target_KLine(self, tar_range: float):
        """监测特殊K线"""

        for bar in self.bars:
            K_range = abs(bar.close_price - bar.open_price) / bar.open_price * 100
            if K_range >= tar_range:
                bar.local_datetime = generator_localtime(bar)

                print(f'检测到目标K线{bar.local_datetime} 幅度: {round(K_range,2)}%')
                self.tar_bar = bar
                # if not self.exist_horizontal():
                # print('未监测到横盘')
                # print('===================================================')
                # print()
                # pass
                # return bar

    def exist_horizontal(self):
        """判断存在横盘"""
        tar_range = self.tar_range
        # 获取横盘区间
        self.hor_bars = self.get_horizontal(self.tar_bar, tar_range)
        # 校验横盘区间
        self.hor_bars = self.check_horizontal(self.hor_bars, tar_range)

        if self.hor_bars[-1].datetime - self.hor_bars[0].datetime <= timedelta(days=3):
            return False

        #
        max_price = self.hor_bars[0].high_price
        min_price = self.hor_bars[0].close_price
        for bar in self.hor_bars:
            max_price = bar.high_price if bar.high_price > max_price else max_price
            min_price = bar.low_price if bar.low_price < min_price else min_price

        # print('↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓')
        # print(f'检测到目标K线{generator_localtime(self.tar_bar)}')
        print(f'横盘区间为; {generator_localtime(self.hor_bars[0])} ~ {generator_localtime(self.hor_bars[-1])}')
        print(f'区间最高点为: {max_price} 最低点为: {min_price}')
        print('===================================================')
        # print()

        return True

    def run(self):
        # 监测目标K线
        # self.tar_bar = self.check_target_KLine(tar_range=2.2)
        self.check_target_KLine(tar_range=self.tar_range)
        # 判断是否存在横盘
        # if not self.exist_horizontal():
        #     print('未监测到横盘')


if __name__ == '__main__':
    strategy = ZQTrendStrategy('1h', 1, 4)
    strategy.run()
    input()
