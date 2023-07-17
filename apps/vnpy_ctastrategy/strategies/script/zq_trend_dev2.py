from datetime import datetime, timedelta
from typing import List
import numpy as np
import matplotlib.pyplot as plt

from apps.vnpy_ctastrategy import CtaTemplate

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, TradeData
from ScriptBase import ZQLoadBars, ZQIntervalConvert, generator_localtime


class ZQTrendStrategy2(CtaTemplate):
    """zq趋势策略dev"""
    #
    zq_interval: ZQIntervalConvert = None

    # K线参数信息
    tar_bar_range: float = None  # 目标波幅
    tar_bar: BarData = None  # 目标波幅K线
    tar_bar_count: int = 0

    # 横盘参数信息
    upper_rail: float = 0
    lower_rail: float = 0
    hor_bars: List[BarData] = []
    tar_hor_size = None
    tar_hor_range: float = None

    #
    curr_bar: BarData = None
    exist_hor = False

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """
        初始化目标幅度和横盘周期
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

        self.put_event()

    def on_bar(self, bar: BarData) -> None:
        """交易主逻辑"""

        self.get_target_kline(bar)
        if self.exist_hor:
            if bar.close_price - bar.open_price >= 0:
                # 多
                if bar.close_price <= self.upper_rail:
                    if self.pos == 0:
                        self.buy(bar.close_price, 1)
                    elif self.pos < 0:
                        self.cover(bar.close_price, 1)
                        self.buy(bar.close_price, 1)

                    self.exist_hor = False
            else:
                # 空
                if bar.close_price >= self.lower_rail:
                    if self.pos == 0:
                        self.short(bar.close_price, 1)
                    elif self.pos > 0:
                        self.sell(bar.close_price, 1)
                        self.short(bar.close_price, 1)

                    self.exist_hor = False
                pass

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    # ==================zq=====================
    def get_horizontal(self):
        """获取横盘区间"""

        # 取指定区间K线
        self.hor_bars: List[BarData] = ZQLoadBars(
            symbol="BTCUSDT",
            exchange=Exchange.BINANCE,
            zq_interval="4h",
            start=self.curr_bar.datetime - timedelta(hours=self.tar_hor_size),
            end=self.curr_bar.datetime
        ).load()

        copy_hor_bars = self.hor_bars  # 缓存

        # 多头目标K线的最高价作为上轨初始值, 空头则最低价作为下轨
        if self.tar_bar.close_price - self.tar_bar.open_price > 0:
            # 多头

            self.upper_rail = self.tar_bar.high_price
            self.lower_rail = self.upper_rail - self.upper_rail * 0.5  # 50%作为另一个轨的初始值

            # 上轨先开始逼近
            upper_intersect_max_count = 2  # 隐线穿过次数
            lower_intersect_max_count = 2
            step = 10  # 步进

            while 1:

                for hor_bar in copy_hor_bars:
                    if hor_bar.high_price >= self.upper_rail:
                        upper_intersect_max_count -= 1
                        copy_hor_bars.remove(hor_bar)  # 剔除已经判断过的K线

                    if upper_intersect_max_count <= 0:
                        self.upper_rail = hor_bar.high_price
                        break

                if upper_intersect_max_count <= 0:
                    break
                self.upper_rail -= step
            # 再下轨
            copy_hor_bars = self.hor_bars  # 重置
            while 1:
                for hor_bar in copy_hor_bars:
                    if hor_bar.low_price <= self.lower_rail:
                        lower_intersect_max_count -= 1
                        copy_hor_bars.remove(hor_bar)

                    if lower_intersect_max_count <= 0:
                        self.lower_rail = hor_bar.low_price
                        break

                if lower_intersect_max_count <= 0:
                    break
                self.lower_rail += step

            pass
        else:
            # 空头
            self.lower_rail = self.tar_bar.low_price
            self.upper_rail = self.lower_rail + self.lower_rail * 0.5

            upper_intersect_max_count = 2
            lower_intersect_max_count = 2
            step = 10  # 步进

            # 下轨
            copy_hor_bars = self.hor_bars
            while 1:

                for hor_bar in copy_hor_bars:
                    if hor_bar.low_price <= self.lower_rail:
                        lower_intersect_max_count -= 1
                        copy_hor_bars.remove(hor_bar)  # 剔除已经判断过的K线

                    if lower_intersect_max_count <= 0:
                        self.lower_rail = hor_bar.low_price
                        break

                if lower_intersect_max_count <= 0:
                    break
                self.lower_rail += step

            # 上轨
            copy_hor_bars = self.hor_bars
            while 1:

                for hor_bar in copy_hor_bars:
                    if hor_bar.high_price >= self.upper_rail:
                        upper_intersect_max_count -= 1
                        copy_hor_bars.remove(hor_bar)

                    if upper_intersect_max_count <= 0:
                        self.upper_rail = hor_bar.high_price
                        break

                if upper_intersect_max_count <= 0:
                    break
                self.upper_rail -= step

        # =================判断横盘区间是否符合=======================
        hor_range = (self.upper_rail - self.lower_rail) / ((self.upper_rail + self.lower_rail) / 2) * 100
        if hor_range > self.tar_hor_range:
            self.exist_hor = False
            return

        self.tar_bar_count += 1
        print("===========================================================")
        print(f'检测到目标K线{self.tar_bar.local_datetime} 幅度: {round(self.tar_bar.bar_range, 2)}%')
        print(f'区间开始时间:{self.hor_bars[-1].local_datetime}, 上轨: {self.upper_rail}, 下轨: {self.lower_rail}, 幅度: {round(hor_range, 3)}%')

        self.exist_hor = True
        return

    def get_target_kline(self, curr_bar: BarData):
        """监测目标波幅K线"""
        self.curr_bar = curr_bar

        self.curr_bar.bar_range = (self.curr_bar.close_price - self.curr_bar.open_price) / self.curr_bar.open_price * 100  # 添加幅度

        if abs(self.curr_bar.bar_range) >= self.tar_bar_range:
            self.tar_bar = self.curr_bar

            self.get_horizontal()  # 判断横盘


if __name__ == '__main__':

    # 加载数据
    bars: List[BarData] = ZQLoadBars(
        symbol="BTCUSDT",
        exchange=Exchange.BINANCE,
        zq_interval="4h",
        start=datetime(2023, 1, 1),
        end=datetime(2023, 7, 13)
    ).load()

    strategy = ZQTrendStrategy2(
        None, None, None, None
    )

    strategy.tar_hor_range = 3.5
    strategy.tar_hor_size = 3 * 24
    strategy.tar_bar_range = 1.7

    for bar in bars:
        strategy.get_target_kline(bar)  # 判断是否是目标K线

    print(f'总计:{strategy.tar_bar_count}')
    # input()
