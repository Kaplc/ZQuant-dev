from datetime import datetime, timedelta
from time import sleep
from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt

from apps.vnpy_ctastrategy import CtaTemplate, StopOrder

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, TradeData, OrderData
from apps.vnpy_ctastrategy.strategies.script.ZQTools import *


class ZQTrendStrategy4(CtaTemplate):
    author = "用Python的交易员"

    debug = False

    # 参数
    tar_range = 6  # 影线幅度x0.1
    i = 10  # 止盈倍数x0.1
    each_amount = 20  # 每笔风险

    #
    ss_sl_dict = {}
    is_long = None
    active_orders: List[ZQOrder] = []
    achievement_orders: List[ZQOrder] = []

    parameters = ["tar_range", "i"]
    variables = ["tar_range", "i"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")
        self.load_bar(5)

        self.tar_range /= 10
        self.i /= 10
        self.ss_sl_dict = {}
        self.active_orders = []
        self.achievement_orders = []

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

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        if self.debug:
            print(bar)

        # 识别关键K线
        direction = self.check_tar_bar(bar)

        # 开仓
        self.open_pos(direction, bar)

        # 初始止盈止损
        for zq_order in self.active_orders:
            if zq_order.order.status == Status.ALLTRADED and zq_order.stop_surplus_order is None and zq_order.stop_loss_order is None:
                # 订单全部成交和没有止盈止损单才进行止盈止损
                self.start_stop_surplus_or_loss(zq_order)

        # 移动止损
        for zq_order in self.active_orders:
            if zq_order.state == ZQOrderState.Trading and zq_order.stop_surplus_order is not None and zq_order.stop_loss_order is not None:
                # 订单状态为持仓中且有止盈止损单才进行止盈止损
                self.move_stop_loss(bar, zq_order)

        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        订单状态更新回调
        """
        # print(f'委托==> {order}')
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        订单成交回调
        """
        # print(self.cta_engine.limit_orders[trade.vt_orderid])
        if self.debug:
            print(f'成交==> {trade}')

        self.update_zqorder_state(trade)  # zq_order的stop单成交, 则改变zq订单状态
        self.cancel_relative_surplus_or_loss_order(trade)  # 取消止盈止损相对的挂单
        self.update_active_orders()  # 更新活跃订单列表
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass

    # =====================zq=======================
    def check_tar_bar(self, bar: BarData):
        """识别关键K线"""
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

        if abs(upper_hatch_range) > self.tar_range:
            # 做空
            if bar_entity_length >= abs(upper_hatch_length):  # 影线小于实体, 排除
                return "none"
            # print(f'short: {bar.datetime}')
            return "short"

        if abs(lower_hatch_range) > self.tar_range:
            # 做多
            if bar_entity_length >= abs(lower_hatch_length):
                return False
            # print(f'long: {bar.datetime}')
            return "long"

    def open_pos(self, direction, bar):
        """开仓"""
        if direction == "long":
            # 多
            if self.debug:
                print("==========long==========")
            # 计算止盈止损
            stop_loss_price = bar.low_price
            stop_surplus_price = bar.close_price + abs(bar.close_price - bar.low_price) * self.i
            # 计算数量
            volume = int((self.each_amount / abs(bar.close_price - stop_loss_price)) * 1000) / 1000
            # 下单
            order = self.buy(price=bar.close_price, volume=volume)
            if self.trading:
                # 生成zq_order对象
                zq_order = ZQOrder(
                    order=self.cta_engine.limit_orders[order[0]],
                    stop_surplus_order=None,
                    stop_loss_order=None,
                    direction=ZQOrderDirection.Long,
                    stop_surplus_price=stop_surplus_price,
                    stop_loss_price=stop_loss_price,
                    volume=volume
                )
                self.active_orders.append(zq_order)

                return zq_order

        elif direction == "short":
            # 空
            if self.debug:
                print("========short============")
            stop_loss_price = bar.high_price
            stop_surplus_price = bar.close_price - abs(bar.high_price - bar.close_price) * self.i
            volume = int((self.each_amount / abs(bar.close_price - stop_loss_price)) * 1000) / 1000
            order = self.short(price=bar.close_price, volume=volume)
            if self.trading:
                # 生成zq_order对象
                zq_order = ZQOrder(
                    order=self.cta_engine.limit_orders[order[0]],
                    stop_surplus_order=None,
                    stop_loss_order=None,
                    direction=ZQOrderDirection.Short,
                    stop_surplus_price=stop_surplus_price,
                    stop_loss_price=stop_loss_price,
                    volume=volume
                )
                self.active_orders.append(zq_order)

                return zq_order

    def start_stop_surplus_or_loss(self, zq_order):
        """开始挂单止盈止损"""
        # 活跃订单已成交且无止盈止损单
        if zq_order.direction == ZQOrderDirection.Long:
            stop_surplus_orderid = self.sell(zq_order.stop_surplus_price, zq_order.volume)[0]
            stop_loss_orderid = self.sell(zq_order.stop_loss_price, zq_order.volume, stop=True)[0]  # 止损stop

            zq_order.stop_surplus_order = self.cta_engine.limit_orders[stop_surplus_orderid]
            zq_order.stop_loss_order = self.cta_engine.stop_orders[stop_loss_orderid]

        elif zq_order.direction == ZQOrderDirection.Short:
            stop_surplus_orderid = self.cover(zq_order.stop_surplus_price, zq_order.volume)[0]
            stop_loss_orderid = self.cover(zq_order.stop_loss_price, zq_order.volume, stop=True)[0]

            zq_order.stop_surplus_order = self.cta_engine.limit_orders[stop_surplus_orderid]
            zq_order.stop_loss_order = self.cta_engine.stop_orders[stop_loss_orderid]

    def move_stop_loss(self, bar, zq_order):
        """移动止损"""
        if zq_order.direction == ZQOrderDirection.Long and zq_order.state == ZQOrderState.Trading:  # 多单
            stop_loss_distance = abs(zq_order.stop_loss_order.price - zq_order.order.price)  # 止损距离

            if bar.low_price - stop_loss_distance > zq_order.stop_loss_order.price:
                # 修改止损
                if type(zq_order.stop_loss_order) == OrderData:
                    # limit
                    self.cancel_order(zq_order.stop_loss_order.vt_orderid)  # 取消当前止损单
                    new_stop_loss_order = self.sell(bar.close_price - stop_loss_distance, zq_order.stop_loss_order.volume, stop=True)  # 重新挂单

                    zq_order.stop_loss_order = self.cta_engine.stop_orders[new_stop_loss_order[0]]  # 修改最新的止损单
                    if self.debug:
                        print(f'最新移动止损 {self.cta_engine.stop_orders[new_stop_loss_order[0]]}')

                else:
                    # stop
                    self.cancel_order(zq_order.stop_loss_order.stop_orderid)
                    new_stop_loss_order = self.sell(bar.close_price - stop_loss_distance, zq_order.stop_loss_order.volume, stop=True)  # 重新挂单

                    zq_order.stop_loss_order = self.cta_engine.stop_orders[new_stop_loss_order[0]]
                    if self.debug:
                        print(f'最新移动止损 {self.cta_engine.stop_orders[new_stop_loss_order[0]]}')

        elif zq_order.direction == ZQOrderDirection.Short and zq_order.state == ZQOrderState.Trading:  # 空单
            stop_loss_distance = abs(zq_order.stop_loss_order.price - zq_order.order.price)

            if bar.high_price + stop_loss_distance < zq_order.stop_loss_order.price:
                if type(zq_order.stop_loss_order) == OrderData:
                    # limit
                    self.cancel_order(zq_order.stop_loss_order.vt_orderid)
                    new_stop_loss_order = self.cover(bar.close_price + stop_loss_distance, zq_order.stop_loss_order.volume, stop=True)

                    zq_order.stop_loss_order = self.cta_engine.stop_orders[new_stop_loss_order[0]]
                    if self.debug:
                        print(f'最新移动止损 {self.cta_engine.stop_orders[new_stop_loss_order[0]]}')

                else:
                    # stop
                    self.cancel_order(zq_order.stop_loss_order.stop_orderid)
                    new_stop_loss_order = self.cover(bar.close_price + stop_loss_distance, zq_order.stop_loss_order.volume, stop=True)

                    zq_order.stop_loss_order = self.cta_engine.stop_orders[new_stop_loss_order[0]]
                    if self.debug:
                        print(f'最新移动止损 {self.cta_engine.stop_orders[new_stop_loss_order[0]]}')

    def cancel_relative_surplus_or_loss_order(self, trade):
        """取消对应的止盈或止损单"""
        for zq_order in self.active_orders:
            if zq_order.stop_loss_order is not None and zq_order.stop_surplus_order is not None:
                if zq_order.stop_surplus_order.status == Status.ALLTRADED or zq_order.stop_surplus_order.status == StopOrderStatus.TRIGGERED:
                    self.cancel_order(zq_order.stop_loss_order.get_vt_orderid())
                elif zq_order.stop_loss_order.status == Status.ALLTRADED or zq_order.stop_loss_order.status == StopOrderStatus.TRIGGERED:
                    self.cancel_order(zq_order.stop_surplus_order.get_vt_orderid())

    def update_active_orders(self):
        """更新活跃订单"""
        for zq_order in self.active_orders:
            zq_order.update_order_state()  # 有成交就更新订单状态
            # 移除已经止盈止损的
            if zq_order.state == ZQOrderState.Stop_Loss or zq_order.state == ZQOrderState.Stop_Surplus:
                self.achievement_orders.append(zq_order)
                self.active_orders.remove(zq_order)

    def update_zqorder_state(self, trade):
        """更新zq订单状态"""
        # 更新订单stop=>limit
        for zq_order in self.active_orders:
            if zq_order.order.get_vt_orderid() == trade.vt_orderid:
                # zq_order.order = self.cta_engine.limit_orders[trade.vt_orderid]  # 修改order
                zq_order.state = ZQOrderState.Trading  # 修改状态

    def vt_orderid_to_stop_orderid(self, vt_orderid):
        for stop_order in self.cta_engine.stop_orders:
            if stop_order.get_vt_orderid() == vt_orderid:
                return stop_order.stop_orderid


# class ZQTrendStrategy4
class TESTZQTrendStrategy4:
    # 参数
    tar_range = 0.6

    #
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
        print(f"开仓: {buy_bar.open_price}, 日期:{buy_bar.datetime}")
        if is_long:
            # 做多
            self.is_long = True

            self.stop_loss_price = last_bar.low_price
            # print(f"止损: {round(self.stop_loss_price, 2)}")

            self.stop_surplus_price = buy_bar.open_price + abs(buy_bar.open_price - last_bar.low_price)
            # print(f"止盈: {round(self.stop_surplus_price, 2)}")
        else:
            # 做空
            self.is_long = False

            self.stop_loss_price = last_bar.high_price
            # print(f"止损: {round(self.stop_loss_price, 2)}")

            self.stop_surplus_price = buy_bar.open_price - abs(last_bar.high_price - buy_bar.open_price)
            # print(f"止盈: {round(self.stop_surplus_price, 2)}")
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
        self.total_profit_loss_ratio += profit_loss_ratio
        print(f"持仓结果: 止损于{curr_bar.close_price}, 盈亏比: {profit_loss_ratio} 日期:{curr_bar.datetime}")
        self.reset()
        self.count_loss += 1

    def stop_surplus(self, curr_bar: BarData):
        """止盈"""
        profit_loss_ratio = round(abs(curr_bar.close_price - self.open_price) / abs(self.stop_loss_price - self.open_price), 2)
        self.total_profit_loss_ratio += profit_loss_ratio
        self.winning_total_profit_loss_ratio += profit_loss_ratio
        print(f"持仓结果: 止盈于{curr_bar.close_price}, 盈亏比: {profit_loss_ratio} 日期:{curr_bar.datetime}")
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

        if abs(upper_hatch_range) > self.tar_range:
            # 做空
            if bar_entity_length >= abs(upper_hatch_length):  # 影线小于实体, 排除
                return False
            print("=======================================================================")

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
                    print(f"做空 日期: {holding_bar.datetime}, 上影线幅度{round(upper_hatch_range, 2)}%")
                    self.buy(holding_bar, bar, is_long=False)
                    is_buy = True
                    print("...持仓中...")
                else:
                    # 其余是持仓
                    if not self.holding(holding_bar):
                        return

        if abs(lower_hatch_range) > self.tar_range:
            return
            # 做多
            if bar_entity_length >= abs(lower_hatch_length):
                return False
            print("=======================================================================")
            print(f"发现做多交易机会 日期: {bar.datetime}, 下影线幅度{round(lower_hatch_range, 2)}%")

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
        start=datetime(2023, 5, 1),
        end=datetime(2023, 7, 20)
    ).load()

    srg4 = TESTZQTrendStrategy4()
    srg4.bars = bars

    srg4.tar_range = 0.6
    srg4.i = 1.0

    index = 0
    for bar in bars:

        bar.index = index
        index += 1
        if srg4.check_tar_bar(bar):
            pass

    srg4.cal()

    print()
    print("+++++++++++++++++++++++++++++")
    # print("初始资金100000")
    print(f"止盈笔数: {srg4.count_surplus}")
    print(f"止损笔数: {srg4.count_loss}")
    winning_probability = round(srg4.count_surplus / srg4.total_count, 2)
    print(f"胜率: {winning_probability}")
    winning_total_avg_profit_loss_ratio = round(srg4.winning_total_profit_loss_ratio / srg4.count_surplus, 2)
    print(f"盈利平均盈亏比: {winning_total_avg_profit_loss_ratio}")
    print(f"期望: {round(winning_probability * winning_total_avg_profit_loss_ratio + (1 - winning_probability) * -1, 3)}")
    print(f"手续费{srg4.total_count * 30000 * 0.0004}")
