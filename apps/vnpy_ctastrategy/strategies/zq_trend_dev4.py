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
    bars: List[BarData] = None

    is_long = None
    open_price = 0
    stop_loss_price = 0
    stop_surplus_price = 0

    count_loss = 0
    count_surplus = 0
    total_count = 0
    winning_total_profit_loss_ratio = 0
    total_profit_loss_ratio = 0
    avg_profit_loss_ratio = 0

    def reset(self):
        """重置"""
        self.is_long = None
        self.open_price = 0
        self.stop_loss_price = 0
        self.stop_surplus_price = 0
        self.profit_loss_ratio = 0

    def cal(self):
        """计算"""
        self.total_count = self.count_loss + self.count_surplus
        self.avg_profit_loss_ratio = round(self.total_profit_loss_ratio / self.total_count, 2)

    def buy(self, buy_bar: BarData, last_bar: BarData, is_long: bool):
        """开仓"""
        self.open_price = buy_bar.open_price
        print(f"开仓: {buy_bar.open_price}, 日期:{buy_bar.local_datetime}")
        if is_long:
            # 做多
            self.is_long = True

            self.stop_loss_price = last_bar.low_price
            print(f"止损: {round(self.stop_loss_price, 2)}")

            self.stop_surplus_price = buy_bar.open_price + (buy_bar.open_price - last_bar.low_price)
            print(f"止盈: {round(self.stop_surplus_price, 2)}")
        else:
            # 做空
            self.is_long = False

            self.stop_loss_price = last_bar.high_price
            print(f"止损: {round(self.stop_loss_price, 2)}")

            self.stop_surplus_price = buy_bar.open_price + (buy_bar.open_price - last_bar.high_price)
            print(f"止盈: {round(self.stop_surplus_price, 2)}")
        pass

    def holding(self, curr_bar: BarData):
        """持仓"""

        if self.is_long and curr_bar.close_price <= self.stop_loss_price:
            # 做多止损
            self.stop_loss(curr_bar)
            return False

        if not self.is_long and curr_bar.close_price >= self.stop_loss_price:
            # 做空止损
            self.stop_loss(curr_bar)
            return False

        if self.is_long and curr_bar.close_price >= self.stop_surplus_price:
            # 做多止盈
            self.stop_surplus(curr_bar)
            return False

        if not self.is_long and curr_bar.close_price <= self.stop_surplus_price:
            # 做空止盈
            self.stop_surplus(curr_bar)
            return False

        return True

    def stop_loss(self, curr_bar: BarData):
        """止损"""
        profit_loss_ratio = -1
        self.total_profit_loss_ratio += self.profit_loss_ratio
        print(f"持仓结果: 止损于{curr_bar.close_price}, 盈亏比: {profit_loss_ratio} 日期:{curr_bar.local_datetime}")
        self.reset()
        self.count_loss += 1

    def stop_surplus(self, curr_bar: BarData):
        """止盈"""
        profit_loss_ratio = round(abs(curr_bar.close_price - self.open_price) / abs(self.stop_loss_price - self.open_price), 2)
        self.total_profit_loss_ratio += profit_loss_ratio
        self.winning_total_profit_loss_ratio += profit_loss_ratio
        print(f"持仓结果: 止盈于{curr_bar.close_price}, 盈亏比: {profit_loss_ratio} 日期:{curr_bar.local_datetime}")
        self.reset()
        self.count_surplus += 1

    def check_tar_bar(self, bar: BarData):
        if bar.close_price - bar.open_price >= 0:
            # 阳线
            # 上影线
            upper_hatch_length = bar.high_price - bar.close_price
            upper_hatch_range = (upper_hatch_length / bar.open_price) * 100
            # 下影线
            lower_hatch_length = bar.open_price - bar.low_price
            lower_hatch_range = (lower_hatch_length / bar.open_price) * 100

        else:
            # 阴线
            upper_hatch_length = bar.high_price - bar.open_price
            upper_hatch_range = (upper_hatch_length / bar.open_price) * 100
            lower_hatch_length = bar.close_price - bar.low_price
            lower_hatch_range = (lower_hatch_length / bar.open_price) * 100

        bar_entity_length = abs(bar.close_price - bar.open_price)

        if abs(upper_hatch_range) > 0.6:
            # 做空
            if bar_entity_length >= abs(upper_hatch_length):  # 影线小于实体, 排除
                return False
            print("=======================================================================")
            print(f"发现做空交易机会 日期: {bar.local_datetime}, 上影线幅度{round(upper_hatch_range, 2)}%")

            # holding_bars = ZQLoadBars(
            #     symbol="BTCUSDT",
            #     exchange=Exchange.BINANCE,
            #     zq_interval="15m",
            #     start=bar.datetime + timedelta(minutes=15),
            #     end=datetime(2023, 7, 18)
            # ).load()

            bar_index = bar.index + 1
            holding_bars = self.bars[bar_index: -1]

            is_buy = False
            for holding_bar in holding_bars:

                if not is_buy:
                    # 第一根K线开仓
                    self.buy(holding_bar, bar, is_long=False)
                    is_buy = True
                    print("...持仓中...")
                else:
                    # 其余是持仓
                    if not self.holding(holding_bar):
                        return

        if abs(lower_hatch_range) > 0.6:
            # 做多
            if bar_entity_length >= abs(lower_hatch_length):
                return False
            print("=======================================================================")
            print(f"发现做多交易机会 日期: {bar.local_datetime}, 下影线幅度{round(lower_hatch_range, 2)}%")

            # holding_bars = ZQLoadBars(
            #     symbol="BTCUSDT",
            #     exchange=Exchange.BINANCE,
            #     zq_interval="15m",
            #     start=bar.datetime + timedelta(minutes=15),
            #     end=datetime(2023, 7, 18)
            # ).load()

            bar_index = bar.index + 1
            holding_bars = self.bars[bar_index: -1]

            is_buy = False
            for holding_bar in holding_bars:

                if not is_buy:
                    # 第一根K线开仓
                    self.buy(holding_bar, bar, is_long=True)
                    is_buy = True
                    print("...持仓中...")
                else:
                    # 其余是持仓
                    if not self.holding(holding_bar):
                        return

            return True
        pass


if __name__ == '__main__':
    bars: List[BarData] = ZQLoadBars(
        symbol="BTCUSDT",
        exchange=Exchange.BINANCE,
        zq_interval="15m",
        start=datetime(2022, 1, 1),
        end=datetime(2023, 7, 18)
    ).load()

    srg4 = ZQTrendStrategy4()
    srg4.bars = bars

    index = 0
    for bar in bars:

        bar.index = index
        index += 1
        if srg4.check_tar_bar(bar):
            pass

    srg4.cal()

    print()
    print("+++++++++++++++++++++++++++++")
    print(f"止盈笔数: {srg4.count_surplus}")
    print(f"止损笔数: {srg4.count_loss}")
    winning_probability = round(srg4.count_surplus / srg4.total_count, 2)
    print(f"胜率: {winning_probability}")
    winning_total_avg_profit_loss_ratio = round(srg4.winning_total_profit_loss_ratio / srg4.count_surplus, 2)
    print(f"盈利平均盈亏比: {winning_total_avg_profit_loss_ratio}")
    print(f"期望: {round(winning_probability * winning_total_avg_profit_loss_ratio + (1 - winning_probability) * -1, 3)}")
