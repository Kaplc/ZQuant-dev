"""
Defines constants and objects used in CtaStrategy App.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict

from core.trader.constant import Direction, Offset, Interval

APP_NAME = "CtaStrategy"
STOPORDER_PREFIX = "STOP"


class StopOrderStatus(Enum):
    WAITING = "等待中"
    CANCELLED = "已撤销"
    TRIGGERED = "已触发"


class EngineType(Enum):
    LIVE = "实盘"
    BACKTESTING = "回测"


class BacktestingMode(Enum):
    BAR = 1
    TICK = 2


@dataclass
class StopOrder:
    vt_symbol: str
    direction: Direction
    offset: Offset
    price: float
    volume: float
    stop_orderid: str
    strategy_name: str
    datetime: datetime
    lock: bool = False
    net: bool = False
    vt_orderids: list = field(default_factory=list)
    status: StopOrderStatus = StopOrderStatus.WAITING

    def get_vt_orderid(self):
        if self.vt_orderids:
            return self.vt_orderids[0]
        else:
            return self.stop_orderid

    def __str__(self):
        return f'订单id: {self.stop_orderid}  日期: {self.datetime}  方向: {self.direction}  价格: {self.price}  状态: {self.status.value}'


EVENT_CTA_LOG = "eCtaLog"
EVENT_CTA_STRATEGY = "eCtaStrategy"
EVENT_CTA_STOPORDER = "eCtaStopOrder"

INTERVAL_DELTA_MAP: Dict[Interval, timedelta] = {
    Interval.TICK: timedelta(milliseconds=1),
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta(days=1),
    # ==============zq=================
    Interval.MINUTE_15: timedelta(minutes=15)
}
