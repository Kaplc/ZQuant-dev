from datetime import datetime, timedelta
from typing import List
import numpy as np
import matplotlib.pyplot as plt

from apps.vnpy_ctastrategy import CtaTemplate

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, TradeData
from apps.vnpy_ctastrategy.strategies.script.ScriptBase import ZQLoadBars, ZQIntervalConvert, generator_localtime


# class ZQTrendStrategy3:
class ZQTrendStrategy3(CtaTemplate):
    """zq趋势策略dev"""
    #
    zq_interval: ZQIntervalConvert = None

    # K线参数信息
    tar_bar_range: float = 1.0  # 目标波幅
    tar_bar: BarData = None  # 目标波幅K线
    tar_bar_count: int = 0

    # 横盘参数信息
    upper_rail: float = 0
    lower_rail: float = 0
    hor_bars: List[BarData] = []
    tar_hor_size = 3 * 24
    tar_hor_range: float = 3.5

    #
    curr_bar: BarData = None
    exist_hor = False

    # 回测窗口参数
    parameters = ["tar_bar_range"]

    # variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """
        初始化目标幅度和横盘周期
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        pass

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

        if self.get_target_kline(bar):
            if self.curr_bar.bar_range >= 0:
                if self.pos == 0:
                    self.short(bar.close_price, 1)
                elif self.pos > 0:
                    self.sell(bar.close_price, 1)
                    self.short(bar.close_price, 1)
            else:
                if bar.close_price <= self.upper_rail:
                    if self.pos == 0:
                        self.buy(bar.close_price, 1)
                    elif self.pos < 0:
                        self.cover(bar.close_price, 1)
                        self.buy(bar.close_price, 1)

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    # ==================zq=====================

    def get_target_kline(self, curr_bar: BarData):
        """监测目标波幅K线"""
        self.curr_bar = curr_bar

        self.curr_bar.bar_range = (self.curr_bar.close_price - self.curr_bar.open_price) / self.curr_bar.open_price * 100  # 添加幅度

        if abs(self.curr_bar.bar_range) >= self.tar_bar_range:
            self.tar_bar = self.curr_bar
            print("===========================================================")
            print(f'检测到目标K线{self.tar_bar.local_datetime} 幅度: {round(self.tar_bar.bar_range, 2)}%')
            self.tar_bar_count += 1

            return True

        return False
            # self.get_horizontal()  # 判断横盘


if __name__ == '__main__':

    # 加载数据
    bars: List[BarData] = ZQLoadBars(
        symbol="BTCUSDT",
        exchange=Exchange.BINANCE,
        zq_interval="1h",
        start=datetime(2023, 1, 1),
        end=datetime(2023, 7, 13)
    ).load()

    strategy = ZQTrendStrategy3(
        None, None, None, None
    )

    strategy.tar_hor_range = 3
    strategy.tar_hor_size = 3 * 24
    strategy.tar_bar_range = 1.5

    for bar in bars:
        strategy.get_target_kline(bar)  # 判断是否是目标K线

    print(f'总计:{strategy.tar_bar_count}')
    # input()
