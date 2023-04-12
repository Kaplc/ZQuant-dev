from copy import copy
from typing import Dict, List, Set, TYPE_CHECKING

from .object import (
    ContractData,
    OrderData,
    TradeData,
    PositionData,
    OrderRequest
)
from .constant import Direction, Offset, Exchange

if TYPE_CHECKING:
    from .engine import MainEngine


class OffsetConverter:
    """开平仓调整"""

    def __init__(self, main_engine: "MainEngine") -> None:
        """"""
        self.holdings: Dict[str, "PositionHolding"] = {}

        self.get_contract = main_engine.get_contrac  # 调用主引擎的订单引擎中的方法获取合约对象

    def update_position(self, position: PositionData) -> None:
        """更新持仓"""
        if not self.is_convert_required(position.vt_symbol):  # 是否可以调整持仓
            return

        holding: PositionHolding = self.get_position_holding(position.vt_symbol)  # 获取持仓对象
        holding.update_position(position)  # 更新持仓

    def update_trade(self, trade: TradeData) -> None:
        """更新交易数据到"""
        if not self.is_convert_required(trade.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(trade.vt_symbol)
        holding.update_trade(trade)

    def update_order(self, order: OrderData) -> None:
        """更新订单信息"""
        if not self.is_convert_required(order.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(order.vt_symbol)
        holding.update_order(order)

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """更新订单请求"""
        if not self.is_convert_required(req.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(req.vt_symbol)
        holding.update_order_request(req, vt_orderid)

    def get_position_holding(self, vt_symbol: str) -> "PositionHolding":
        """获取持仓对象"""
        holding: PositionHolding = self.holdings.get(vt_symbol, None)
        if not holding:  # 没有持仓信息对象
            contract: ContractData = self.get_contract(vt_symbol)  # 获取合约对象
            holding = PositionHolding(contract)  # 传入合约对象生成持仓信息对象
            self.holdings[vt_symbol] = holding  # 添加进持仓对象字典
        return holding

    def convert_order_request(
            self,
            req: OrderRequest,
            lock: bool,
            net: bool = False
    ) -> List[OrderRequest]:
        """转换订单请求成框架可识别的请求"""
        if not self.is_convert_required(req.vt_symbol):
            return [req]

        holding: PositionHolding = self.get_position_holding(req.vt_symbol)

        if lock:
            return holding.convert_order_request_lock(req)
        elif net:
            return holding.convert_order_request_net(req)
        elif req.exchange in [Exchange.SHFE, Exchange.INE]:
            return holding.convert_order_request_shfe(req)
        else:
            return [req]

    def is_convert_required(self, vt_symbol: str) -> bool:
        """
        Check if the contract needs offset convert.
        检查合约是否可以调整持仓
        """
        contract: ContractData = self.get_contract(vt_symbol)  # 获取合约对象

        # Only contracts with long-short position mode requires convert
        if not contract:  # 无合约对象返回false
            return False
        elif contract.net_position:  # 有净头寸返回false
            return False
        else:  # 有合约对象返回true
            return True


class PositionHolding:
    """持仓信息"""

    def __init__(self, contract: ContractData) -> None:
        """通过合约对象生成持仓信息对象"""
        self.vt_symbol: str = contract.vt_symbol  # 合约的唯一标识符
        self.exchange: Exchange = contract.exchange

        self.active_orders: Dict[str, OrderData] = {}  # 活跃的委托单（订单）字典，订单数据对象 OrderData 为值

        self.long_pos: float = 0  # 合约上累计的未平多仓合约数量
        self.long_yd: float = 0  # 该合约多头的昨仓数量 昨日累计的未平多仓合约数量
        self.long_td: float = 0  # 该合约多头的今仓数量 当日累计的未平多仓合约数量

        self.short_pos: float = 0  # 该合约累计空头持仓数量
        self.short_yd: float = 0  # 空头的昨仓数量
        self.short_td: float = 0  # 空头的今仓数量

        self.long_pos_frozen: float = 0  # 多头持仓的冻结数量，无法交易和调整的仓位
        self.long_yd_frozen: float = 0  # 多头昨仓的冻结数量
        self.long_td_frozen: float = 0  # 多头今仓的冻结数量

        self.short_pos_frozen: float = 0  # 空头持仓的冻结数量
        self.short_yd_frozen: float = 0  # 空头昨仓的冻结数量
        self.short_td_frozen: float = 0  # 空头今仓的冻结数量

    def update_position(self, position: PositionData) -> None:
        """更新持仓，昨仓，今仓"""
        if position.direction == Direction.LONG:  # 做多
            self.long_pos = position.volume  # 当前仓位
            self.long_yd = position.yd_volume  # 昨天仓位
            self.long_td = self.long_pos - self.long_yd  # 今天仓位
        else:  # 做空
            self.short_pos = position.volume
            self.short_yd = position.yd_volume
            self.short_td = self.short_pos - self.short_yd

    def update_order(self, order: OrderData) -> None:
        """更新活跃订单，删除过期订单"""
        if order.is_active():
            self.active_orders[order.vt_orderid] = order
        else:
            if order.vt_orderid in self.active_orders:
                self.active_orders.pop(order.vt_orderid)

        self.calculate_frozen()

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """处理更新订单请求"""
        gateway_name, orderid = vt_orderid.split(".")

        order: OrderData = req.create_order_data(orderid, gateway_name)
        self.update_order(order)  # 更新活跃订单，删除过期订单

    def update_trade(self, trade: TradeData) -> None:
        """更新单笔交易信息"""
        if trade.direction == Direction.LONG:  # 更新做多仓位信息
            if trade.offset == Offset.OPEN:  # 开仓标志
                self.long_td += trade.volume  # 成交数额累加进多头的今仓数量
            elif trade.offset == Offset.CLOSETODAY:  # 平今标志
                self.short_td -= trade.volume  # 累减空头今天仓位数量
            elif trade.offset == Offset.CLOSEYESTERDAY:  # 平昨标志
                self.short_yd -= trade.volume  # 累减空头昨天仓位数量
            elif trade.offset == Offset.CLOSE:  # 平仓标志
                if trade.exchange in [Exchange.SHFE, Exchange.INE]:  # 判断不同交易所额外情况
                    self.short_yd -= trade.volume  # 昨空
                else:
                    self.short_td -= trade.volume  # 今空

                    if self.short_td < 0:  # 今空
                        self.short_yd += self.short_td
                        self.short_td = 0  # 归零今空
        else:  # 做空
            if trade.offset == Offset.OPEN:
                self.short_td += trade.volume  # 今空
            elif trade.offset == Offset.CLOSETODAY:
                self.long_td -= trade.volume  # 今多
            elif trade.offset == Offset.CLOSEYESTERDAY:
                self.long_yd -= trade.volume  # 昨多
            elif trade.offset == Offset.CLOSE:
                if trade.exchange in [Exchange.SHFE, Exchange.INE]:
                    self.long_yd -= trade.volume
                else:
                    self.long_td -= trade.volume

                    if self.long_td < 0:
                        self.long_yd += self.long_td
                        self.long_td = 0

        self.long_pos = self.long_td + self.long_yd  # 当前多仓总和
        self.short_pos = self.short_td + self.short_yd  # 当前空仓总和

        # Update frozen volume to ensure no more than total volume # 更新冻结仓位
        self.sum_pos_frozen()

    def calculate_frozen(self) -> None:
        """计算冻结仓位"""
        self.long_pos_frozen = 0
        self.long_yd_frozen = 0
        self.long_td_frozen = 0

        self.short_pos_frozen = 0
        self.short_yd_frozen = 0
        self.short_td_frozen = 0

        for order in self.active_orders.values():
            # Ignore position open orders
            if order.offset == Offset.OPEN:  # 忽视开仓订单
                continue

            frozen: float = order.volume - order.traded  # 未成交额

            if order.direction == Direction.LONG:  # 做多冻结仓位
                if order.offset == Offset.CLOSETODAY:
                    self.short_td_frozen += frozen
                elif order.offset == Offset.CLOSEYESTERDAY:
                    self.short_yd_frozen += frozen
                elif order.offset == Offset.CLOSE:
                    self.short_td_frozen += frozen

                    if self.short_td_frozen > self.short_td:
                        self.short_yd_frozen += (self.short_td_frozen
                                                 - self.short_td)
                        self.short_td_frozen = self.short_td
            elif order.direction == Direction.SHORT:  # 做空冻结仓位
                if order.offset == Offset.CLOSETODAY:
                    self.long_td_frozen += frozen
                elif order.offset == Offset.CLOSEYESTERDAY:
                    self.long_yd_frozen += frozen
                elif order.offset == Offset.CLOSE:
                    self.long_td_frozen += frozen

                    if self.long_td_frozen > self.long_td:
                        self.long_yd_frozen += (self.long_td_frozen
                                                - self.long_td)
                        self.long_td_frozen = self.long_td

        self.sum_pos_frozen()  # 计算总和

    def sum_pos_frozen(self) -> None:
        """验证并求总冻结仓位"""
        # Frozen volume should be no more than total volume
        self.long_td_frozen = min(self.long_td_frozen, self.long_td)
        self.long_yd_frozen = min(self.long_yd_frozen, self.long_yd)

        self.short_td_frozen = min(self.short_td_frozen, self.short_td)
        self.short_yd_frozen = min(self.short_yd_frozen, self.short_yd)

        self.long_pos_frozen = self.long_td_frozen + self.long_yd_frozen
        self.short_pos_frozen = self.short_td_frozen + self.short_yd_frozen

    def convert_order_request_shfe(self, req: OrderRequest) -> List[OrderRequest]:
        """额外情况：转换SHFE订单请求"""
        if req.offset == Offset.OPEN:  # 忽略开仓订单
            return [req]

        # 获取可更改仓位
        if req.direction == Direction.LONG:
            pos_available: int = self.short_pos - self.short_pos_frozen
            td_available: int = self.short_td - self.short_td_frozen
        else:
            pos_available: int = self.long_pos - self.long_pos_frozen
            td_available: int = self.long_td - self.long_td_frozen

        # 根据请求数额执行仓位调整
        if req.volume > pos_available:
            return []
        elif req.volume <= td_available:
            req_td: OrderRequest = copy(req)
            req_td.offset = Offset.CLOSETODAY
            return [req_td]
        else:
            req_list: List[OrderRequest] = []

            if td_available > 0:
                req_td: OrderRequest = copy(req)
                req_td.offset = Offset.CLOSETODAY
                req_td.volume = td_available
                req_list.append(req_td)

            req_yd: OrderRequest = copy(req)
            req_yd.offset = Offset.CLOSEYESTERDAY
            req_yd.volume = req.volume - td_available
            req_list.append(req_yd)

            return req_list

    def convert_order_request_lock(self, req: OrderRequest) -> List[OrderRequest]:
        """转换锁仓订单请求"""
        if req.direction == Direction.LONG:
            td_volume: int = self.short_td
            yd_available: int = self.short_yd - self.short_yd_frozen
        else:
            td_volume: int = self.long_td
            yd_available: int = self.long_yd - self.long_yd_frozen

        close_yd_exchanges: Set[Exchange] = {Exchange.SHFE, Exchange.INE}

        # If there is td_volume, we can only lock position
        if td_volume and self.exchange not in close_yd_exchanges:
            req_open: OrderRequest = copy(req)
            req_open.offset = Offset.OPEN
            return [req_open]
        # If no td_volume, we close opposite yd position first
        # then open new position
        else:
            close_volume: int = min(req.volume, yd_available)
            open_volume: int = max(0, req.volume - yd_available)
            req_list: List[OrderRequest] = []

            if yd_available:
                req_yd: OrderRequest = copy(req)
                if self.exchange in close_yd_exchanges:
                    req_yd.offset = Offset.CLOSEYESTERDAY
                else:
                    req_yd.offset = Offset.CLOSE
                req_yd.volume = close_volume
                req_list.append(req_yd)

            if open_volume:
                req_open: OrderRequest = copy(req)
                req_open.offset = Offset.OPEN
                req_open.volume = open_volume
                req_list.append(req_open)

            return req_list

    def convert_order_request_net(self, req: OrderRequest) -> List[OrderRequest]:
        """转换订单请求"""
        if req.direction == Direction.LONG:
            pos_available: int = self.short_pos - self.short_pos_frozen
            td_available: int = self.short_td - self.short_td_frozen
            yd_available: int = self.short_yd - self.short_yd_frozen
        else:
            pos_available: int = self.long_pos - self.long_pos_frozen
            td_available: int = self.long_td - self.long_td_frozen
            yd_available: int = self.long_yd - self.long_yd_frozen

        # Split close order to close today/yesterday for SHFE/INE exchange
        if req.exchange in {Exchange.SHFE, Exchange.INE}:
            reqs: List[OrderRequest] = []
            volume_left: float = req.volume

            if td_available:
                td_volume: int = min(td_available, volume_left)
                volume_left -= td_volume

                td_req: OrderRequest = copy(req)
                td_req.offset = Offset.CLOSETODAY
                td_req.volume = td_volume
                reqs.append(td_req)

            if volume_left and yd_available:
                yd_volume: int = min(yd_available, volume_left)
                volume_left -= yd_volume

                yd_req: OrderRequest = copy(req)
                yd_req.offset = Offset.CLOSEYESTERDAY
                yd_req.volume = yd_volume
                reqs.append(yd_req)

            if volume_left > 0:
                open_volume: int = volume_left

                open_req: OrderRequest = copy(req)
                open_req.offset = Offset.OPEN
                open_req.volume = open_volume
                reqs.append(open_req)

            return reqs
        # Just use close for other exchanges
        else:
            reqs: List[OrderRequest] = []
            volume_left: float = req.volume

            if pos_available:
                close_volume: int = min(pos_available, volume_left)
                volume_left -= pos_available

                close_req: OrderRequest = copy(req)
                close_req.offset = Offset.CLOSE
                close_req.volume = close_volume
                reqs.append(close_req)

            if volume_left > 0:
                open_volume: int = volume_left

                open_req: OrderRequest = copy(req)
                open_req.offset = Offset.OPEN
                open_req.volume = open_volume
                reqs.append(open_req)

            return reqs
