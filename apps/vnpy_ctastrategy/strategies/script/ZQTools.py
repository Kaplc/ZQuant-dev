import re
import time
from abc import ABC
from datetime import datetime, timedelta
from enum import Enum
from typing import List
from tqdm import tqdm

from apps.vnpy_ctastrategy.base import STOPORDER_PREFIX, StopOrderStatus, StopOrder
from core.trader.constant import Exchange, Interval, Status
from core.trader.database import BaseDatabase, get_database
from core.trader.object import BarData, OrderData
from core.trader.utility import BarGenerator


class ZQIntervalConvert:
    """zq to vnpy 周期转换器"""

    value = None  # 值
    unit = None  # 周期单位
    vnInterval = None  # vnpy格式周期

    def __init__(self, interval: str):
        self.value = int(re.search(r'\d+', interval).group())
        self.unit = re.search(r'[a-zA-Z]', interval).group()

        if self.unit == 'm':
            self.vnInterval = Interval.MINUTE
        elif self.unit == 'h':
            self.vnInterval = Interval.HOUR
        elif self.unit == 'd':
            self.vnInterval = Interval.DAILY
        else:
            self.vnInterval = Interval.TICK

    def __str__(self):
        return str(self.value) + self.unit


class ZQKLineGenerator:
    """zq框架K线合成器"""

    def __init__(self, bars: list[BarData], vn_interval):
        self.vn_interval = vn_interval  # vnpy的时间周期
        self.res_bars = []  # 合成结果
        self.src_bars = bars  # 源数据

    def start(self, bar_units):
        bar_gnr = BarGenerator(
            on_bar=None,  # 处理新的K线数据的回调函数
            window=bar_units,  # 要用多少根K线合成
            on_window_bar=self.add_in_res,  # 处理窗口K线数据的回调函数
            interval=self.vn_interval  # K线数据的时间间隔
        )
        for bar in self.src_bars:  # 开始合成
            bar_gnr.update_bar(bar)

        return self.res_bars

    def add_in_res(self, new_bar: BarData):
        new_bar.local_datetime = generator_localtime(new_bar)  # 添加北京时间
        self.res_bars.append(new_bar)


class ZQLoadBars:
    """zq加载行情"""

    symbol: str = None
    exchange: Exchange = None
    zq_interval: ZQIntervalConvert = None
    start: datetime = None
    end: datetime = None
    bars = []

    def __init__(self, symbol: str, exchange: Exchange, zq_interval: str, start: datetime, end: datetime):
        # 初始化行情信息
        self.symbol = symbol
        self.exchange = exchange
        self.zq_interval = ZQIntervalConvert(zq_interval)
        self.start = start
        self.end = end

    def no_process_load(self, start, end):
        """无进度条加载"""
        # 获取K线原始数据
        src_bars = load_bars_data(
            symbol=self.symbol,
            exchange=self.exchange,
            interval=self.zq_interval.vnInterval,
            start=start,
            end=end,
        )

        # ZQ K线合成器合成K线
        bar_generator = ZQKLineGenerator(src_bars, self.zq_interval.vnInterval)
        bars = bar_generator.start(self.zq_interval.value)  # 开始合成新K线列表

        return bars

    def load(self):

        total_date = self.end - self.start

        weeks = total_date.days // 7
        days = total_date.days % 7

        item_end = self.start
        for i in tqdm(range(0, weeks)):
            item_start = item_end
            item_end = item_end + timedelta(days=7)
            self.bars.extend(self.no_process_load(item_start, item_end))

        if days > 0:
            item_start = item_end
            item_end += timedelta(days=days)
            self.bars.extend(self.no_process_load(item_start, item_end))
        # self.no_process_load(self.start, self.end)
        return self.bars


class ZQOrderDirection(Enum):
    Long = "long"
    Short = "short"


class ZQOrderState(Enum):
    Not_Closed = "未成交"
    Trading = "持仓中"
    Stop_Surplus = "已止盈"
    Stop_Loss = "已止损"
    Move_Stop_loss = "移动止损"


class ZQOrderType(Enum):
    Normal = "普通订单"
    Stop_Surplus = "止盈单"
    Stop_Loss = "止损单"


class ZQOrder:
    """zq订单"""
    order: StopOrder = None  # 订单
    stop_surplus_order = None  # 对应的止盈单
    stop_loss_order = None  # 对应的止损单
    direction = None  # 多空方向
    state = None  # 订单状态
    stop_loss_price = None
    stop_surplus_price = None
    volume = None  # 数量

    move_stop_loss = False  # 是否移动止损标识
    profit = 0

    def __init__(self, order, stop_surplus_order, stop_loss_order, direction: ZQOrderDirection, stop_surplus_price, stop_loss_price,
                 volume):
        self.order = order
        self.stop_surplus_order = stop_surplus_order
        self.stop_loss_order = stop_loss_order
        self.direction = direction
        self.state = ZQOrderState.Not_Closed
        self.stop_surplus_price = stop_surplus_price
        self.stop_loss_price = stop_loss_price
        self.volume = volume

    def update_order_state(self):
        """更新状态"""
        if self.stop_loss_order is None and self.stop_surplus_order is None:
            # 无止盈止损单不更新
            return

        if self.stop_surplus_order.status == Status.ALLTRADED or self.stop_surplus_order.status == StopOrderStatus.TRIGGERED:
            self.state = ZQOrderState.Stop_Surplus
        elif self.stop_loss_order.status == Status.ALLTRADED or self.stop_loss_order.status == StopOrderStatus.TRIGGERED:
            if self.move_stop_loss:
                self.state = ZQOrderState.Move_Stop_loss  # 移动止损
            else:
                self.state = ZQOrderState.Stop_Loss  # 普通止损

    def get_relative_order(self, order_id):
        """获取相对的止盈止损单"""

        if type(self.stop_surplus_order) == OrderData:
            # 止盈单limit
            if self.stop_surplus_order.vt_orderid == order_id:
                return self.stop_loss_order.stop_orderid
        else:
            # stop
            if self.stop_surplus_order.stop_orderid == order_id:
                return self.stop_loss_order.vt_orderid

        if type(self.stop_loss_order) == OrderData:
            # 止损单是limit
            if self.stop_loss_order.vt_orderid == order_id:
                return self.stop_surplus_order.stop_orderid
        else:
            # stop
            if self.stop_loss_order.stop_orderid == order_id:
                return self.stop_surplus_order.vt_orderid

    def cal(self):
        """计算"""
        if self.state == ZQOrderState.Stop_Loss:
            # 止损
            self.profit = -round(abs(self.order.price - self.stop_loss_order.price) * self.volume - (0.0004 * self.order.price * self.volume + 0.0004 * self.stop_loss_order.price * self.volume), 4)
        elif self.state == ZQOrderState.Stop_Surplus:
            # 止盈
            self.profit = +round(abs(self.order.price - self.stop_surplus_order.price) * self.volume - (0.0004 * self.order.price * self.volume + 0.0004 * self.stop_surplus_order.price * self.volume), 4)
        elif self.state == ZQOrderState.Move_Stop_loss:
            # 移动止损
            if self.direction == ZQOrderDirection.Long:
                if self.stop_loss_order.price - self.order.price > 0:
                    # 做多时移动止损已经超过开仓价
                    self.profit = +round(abs(self.order.price - self.stop_loss_order.price) * self.volume - (0.0004 * self.order.price * self.volume + 0.0004 * self.stop_loss_order.price * self.volume), 4)
                else:
                    self.profit = -round(abs(self.order.price - self.stop_loss_order.price) * self.volume - (0.0004 * self.order.price * self.volume + 0.0004 * self.stop_loss_order.price * self.volume), 4)
            elif self.direction == ZQOrderDirection.Short:
                if self.stop_loss_order.price - self.order.price < 0:
                    # 做空时移动止损已经低过开仓价
                    self.profit = +round(abs(self.order.price - self.stop_loss_order.price) * self.volume - (0.0004 * self.order.price * self.volume + 0.0004 * self.stop_loss_order.price * self.volume), 4)
                else:
                    self.profit = -round(abs(self.order.price - self.stop_loss_order.price) * self.volume - (0.0004 * self.order.price * self.volume + 0.0004 * self.stop_loss_order.price * self.volume), 4)

    def __str__(self):
        return f"{self.order} 方向: {self.direction.value}  状态: {self.state.value}"


class ZQOrderManager:
    """zq的订单管理类"""
    zq_orders: List[ZQOrder] = []


def load_bars_data(
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
):
    """数据库加载K线"""
    # print('正在加载历史数据')
    database: BaseDatabase = get_database()
    data = database.load_bar_data(
        symbol, exchange, interval, start, end
    )
    return data


def generator_localtime(bar):
    # 生成本地时间
    year = bar.datetime.year
    month = bar.datetime.month
    day = bar.datetime.day
    hour = bar.datetime.hour
    minute = bar.datetime.minute

    local_date = datetime(year, month, day, hour, minute) + timedelta(hours=8)
    return local_date


if __name__ == '__main__':
    interval = ZQIntervalConvert("4h")
    pass
