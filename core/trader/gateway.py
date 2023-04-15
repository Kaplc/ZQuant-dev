from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from copy import copy

from core.event import Event, EventEngine
from .event import (
    EVENT_TICK,
    EVENT_ORDER,
    EVENT_TRADE,
    EVENT_POSITION,
    EVENT_ACCOUNT,
    EVENT_CONTRACT,
    EVENT_LOG,
    EVENT_QUOTE,
)
from .object import (
    TickData,
    OrderData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    LogData,
    QuoteData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest,
    QuoteRequest,
    Exchange,
    BarData
)


class BaseGateway(ABC):
    """
    Abstract gateway class for creating gateways connection
    to different trading systems.

    # How to implement a gateway:

    ---
    ## Basics
    A gateway should satisfies: 应满足
    * this class should be thread-safe:
        * all methods should be thread-safe 线程安全
        * no mutable shared properties between objects. 不共享资源
    * all methods should be non-blocked 非阻塞方法
    * satisfies all requirements written in docstring for every method and callbacks. 任何回调都有处理函数
    * automatically reconnect if connection lost. 链接丢失自动重连

    ---
    ## methods must implements:
    all @abstractmethod

    ---
    ## callbacks must response manually: 回调必须手动响应
    * on_tick 报价
    * on_trade 交易
    * on_order 订单
    * on_position 仓位
    * on_account 账户
    * on_contract 合约

    All the XxxData passed to callback should be constant, which means that
        the object should not be modified after passing to on_xxxx.
    So if you use a cache to store reference of data, use copy.copy to create a new object
    before passing that data into on_xxxx



    """

    # Default name for the gateway. 交易接口默认名字
    default_name: str = ""

    # Fields required in setting dict for connect function. 默认配置
    default_setting: Dict[str, Any] = {}

    # Exchanges supported in the gateway. 交易接口所支持的交易所列表
    exchanges: List[Exchange] = []

    def __init__(self, event_engine: EventEngine, gateway_name: str) -> None:
        """定义事件引擎，交易接口名称"""
        self.event_engine: EventEngine = event_engine
        self.gateway_name: str = gateway_name

    def on_event(self, type: str, data: Any = None) -> None:
        """
        General event push.
        添加事件处理
        """
        event: Event = Event(type, data)  # 创建事件对象
        self.event_engine.put(event)  # 推送处理队列

    def on_tick(self, tick: TickData) -> None:
        """
        Tick event push.
        Tick event of a specific vt_symbol is also pushed.
        创建tick事件并推送
        创建（tick+tick唯一标识）事件并推送
        """
        self.on_event(EVENT_TICK, tick)
        self.on_event(EVENT_TICK + tick.vt_symbol, tick)

    def on_trade(self, trade: TradeData) -> None:
        """
        Trade event push.
        Trade event of a specific vt_symbol is also pushed.
        创建推送trade事件对象
        """
        self.on_event(EVENT_TRADE, trade)
        self.on_event(EVENT_TRADE + trade.vt_symbol, trade)

    def on_order(self, order: OrderData) -> None:
        """
        Order event push.
        Order event of a specific vt_orderid is also pushed.
        创建推送order事件对象
        """
        self.on_event(EVENT_ORDER, order)
        self.on_event(EVENT_ORDER + order.vt_orderid, order)

    def on_position(self, position: PositionData) -> None:
        """
        Position event push.
        Position event of a specific vt_symbol is also pushed.
        创建推送position事件对象
        """
        self.on_event(EVENT_POSITION, position)
        self.on_event(EVENT_POSITION + position.vt_symbol, position)

    def on_account(self, account: AccountData) -> None:
        """
        Account event push.
        Account event of a specific vt_accountid is also pushed.
        推送account事件对象
        """
        self.on_event(EVENT_ACCOUNT, account)
        self.on_event(EVENT_ACCOUNT + account.vt_accountid, account)

    def on_quote(self, quote: QuoteData) -> None:
        """
        Quote event push.
        Quote event of a specific vt_symbol is also pushed.
        推送盘口数据事件对象
        """
        self.on_event(EVENT_QUOTE, quote)
        self.on_event(EVENT_QUOTE + quote.vt_symbol, quote)

    def on_log(self, log: LogData) -> None:
        """
        Log event push.
        推送log事件对象
        """
        self.on_event(EVENT_LOG, log)

    def on_contract(self, contract: ContractData) -> None:
        """
        Contract event push.
        推送合约事件对象
        """
        self.on_event(EVENT_CONTRACT, contract)

    def write_log(self, msg: str) -> None:
        """
        Write a log event from gateway.
        写入log并推送
        """
        log: LogData = LogData(msg=msg, gateway_name=self.gateway_name)
        self.on_log(log)

    @abstractmethod
    def connect(self, setting: dict) -> None:
        """
        Start gateway connection. 启动交易接口连接

        to implement this method, you must:
        * connect to server if necessary
        * log connected if all necessary connection is established
        * do the following query and response corresponding on_xxxx and write_log
            * contracts : on_contract
            * account asset : on_account
            * account holding: on_position
            * orders of account: on_order
            * trades of account: on_trade
        * if any of query above is failed,  write log.

        future plan:
        response callback/change status instead of write_log

        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close gateway connection.
        关闭接口链接
        """
        pass

    @abstractmethod
    def subscribe(self, req: SubscribeRequest) -> None:
        """
        Subscribe tick data update.
        订阅tick数据
        """
        pass

    @abstractmethod
    def send_order(self, req: OrderRequest) -> str:
        """
        Send a new order to server.
        向服务器发送订单
        implementation should finish the tasks blow:
        * create an OrderData from req using OrderRequest.create_order_data
        * assign a unique(gateway instance scope) id to OrderData.orderid
        * send request to server
            * if request is sent, OrderData.status should be set to Status.SUBMITTING
            * if request is failed to sent, OrderData.status should be set to Status.REJECTED
        * response on_order:
        * return vt_orderid

        :return str vt_orderid for created OrderData
        """
        pass

    @abstractmethod
    def cancel_order(self, req: CancelRequest) -> None:
        """
        Cancel an existing order.
        implementation should finish the tasks blow:
        * send request to server
        取消订单
        """
        pass

    def send_quote(self, req: QuoteRequest) -> str:
        """
        Send a new two-sided quote to server.

        implementation should finish the tasks blow:
        * create an QuoteData from req using QuoteRequest.create_quote_data
        * assign a unique(gateway instance scope) id to QuoteData.quoteid
        * send request to server
            * if request is sent, QuoteData.status should be set to Status.SUBMITTING
            * if request is failed to sent, QuoteData.status should be set to Status.REJECTED
        * response on_quote:
        * return vt_quoteid

        :return str vt_quoteid for created QuoteData
        发送报价
        """
        return ""

    def cancel_quote(self, req: CancelRequest) -> None:
        """
        Cancel an existing quote.
        implementation should finish the tasks blow:
        * send request to server
        取消报价
        """
        pass

    @abstractmethod
    def query_account(self) -> None:
        """
        Query account balance.
        查询账户
        """
        pass

    @abstractmethod
    def query_position(self) -> None:
        """
        Query holding positions.
        查询持仓
        """
        pass

    def query_history(self, req: HistoryRequest) -> List[BarData]:
        """
        Query bar history data.
        查询K线历史事件
        """
        pass

    def get_default_setting(self) -> Dict[str, Any]:
        """
        Return default setting dict.
        获取接口配置
        """
        return self.default_setting


class LocalOrderManager:
    """
        Management tool to support use local order id for trading.
        本地订单管理
    """

    def __init__(self, gateway: BaseGateway, order_prefix: str = "") -> None:
        """"""
        self.gateway: BaseGateway = gateway

        # For generating local orderid 生成本地订单id
        self.order_prefix: str = order_prefix  # 订单前缀
        self.order_count: int = 0  # 订单数额
        self.orders: Dict[str, OrderData] = {}  # local_orderid: order 订单对象

        # Map between local and system orderid 本地订单和服务器订单的映射
        self.local_sys_orderid_map: Dict[str, str] = {}  # 本地订单映射表
        self.sys_local_orderid_map: Dict[str, str] = {}  # 服务器订单映射表

        # Push order data buf 推送数据缓冲器
        self.push_data_buf: Dict[str, Dict] = {}  # sys_orderid: data

        # Callback for processing push order data 推送订单回调数据处理函数
        self.push_data_callback: Callable = None

        # Cancel request buf 取消请求缓冲器
        self.cancel_request_buf: Dict[str, CancelRequest] = {}  # local_orderid: req

        # Hook cancel order function 定义gateway直接调用cancel_order
        self._cancel_order: Callable = gateway.cancel_order
        gateway.cancel_order = self.cancel_order

    def new_local_orderid(self) -> str:
        """
        Generate a new local orderid.
        生成新的本地订单ID
        """
        self.order_count += 1
        local_orderid: str = self.order_prefix + str(self.order_count).rjust(8, "0")
        return local_orderid

    def get_local_orderid(self, sys_orderid: str) -> str:
        """
        Get local orderid with sys orderid.
        服务器订单id->本地订单id
        """
        # 如果查找字典未找到订单赋值""
        local_orderid: str = self.sys_local_orderid_map.get(sys_orderid, "")

        if not local_orderid:  # 没有就创建并更新到两个映射表
            local_orderid = self.new_local_orderid()
            self.update_orderid_map(local_orderid, sys_orderid)

        return local_orderid

    def get_sys_orderid(self, local_orderid: str) -> str:
        """
        Get sys orderid with local orderid.
        本地订单id->服务器订单id
        """
        sys_orderid: str = self.local_sys_orderid_map.get(local_orderid, "")
        return sys_orderid

    def update_orderid_map(self, local_orderid: str, sys_orderid: str) -> None:
        """
        Update orderid map.
        更新订单ID映射
        """

        self.sys_local_orderid_map[sys_orderid] = local_orderid
        self.local_sys_orderid_map[local_orderid] = sys_orderid

        self.check_cancel_request(local_orderid)
        self.check_push_data(sys_orderid)  # 检查订单是否在缓冲器

    def check_push_data(self, sys_orderid: str) -> None:
        """
        Check if any order push data waiting.
        检查是否有服务器订单在缓冲器等待
        """
        # 服务器订单不在推送缓冲器
        if sys_orderid not in self.push_data_buf:
            return

        # 推送缓冲器删除服务器订单
        data: dict = self.push_data_buf.pop(sys_orderid)
        if self.push_data_callback:  # 调用回调函数处理删除的订单
            self.push_data_callback(data)

    def add_push_data(self, sys_orderid: str, data: dict) -> None:
        """
        Add push data into buf
        添加服务器订单进缓冲器
        """
        self.push_data_buf[sys_orderid] = data

    def get_order_with_sys_orderid(self, sys_orderid: str) -> Optional[OrderData]:
        """服务器订单id->本地订单id->订单对象"""
        local_orderid: str = self.sys_local_orderid_map.get(sys_orderid, None)
        if not local_orderid:  # 找不到本地订单返回None
            return None
        else:
            return self.get_order_with_local_orderid(local_orderid)  # 返回订单对象

    def get_order_with_local_orderid(self, local_orderid: str) -> OrderData:
        """本地订单id->order对象"""
        order: OrderData = self.orders[local_orderid]
        return copy(order)  # 复制订单对象返回

    def on_order(self, order: OrderData) -> None:
        """
        Keep an order buf before pushing it to gateway.
        推送到接口前保存
        """
        self.orders[order.orderid] = copy(order)  # 保存
        self.gateway.on_order(order)  # 推送

    def cancel_order(self, req: CancelRequest) -> None:
        """调用接口取消订单"""
        sys_orderid: str = self.get_sys_orderid(req.orderid)
        if not sys_orderid:  # 无法找到订单请求->添加进取消请求缓冲器
            self.cancel_request_buf[req.orderid] = req
            return

        self._cancel_order(req)  # 调用接口取消订单

    def check_cancel_request(self, local_orderid: str) -> None:
        """取消缓冲器更新订单"""
        if local_orderid not in self.cancel_request_buf:
            return

        req: CancelRequest = self.cancel_request_buf.pop(local_orderid)  # 缓冲器内删除订单
        self.gateway.cancel_order(req)  # 调用接口取消订单
