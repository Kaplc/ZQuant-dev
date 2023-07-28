"""
Basic data structure used for general trading function in the trading platform.
"""

from dataclasses import dataclass, field
from datetime import datetime
from logging import INFO

from .constant import Direction, Exchange, Interval, Offset, Status, Product, OptionType, OrderType

ACTIVE_STATUSES = set([Status.SUBMITTING, Status.NOTTRADED, Status.PARTTRADED])


@dataclass
class BaseData:
    """
    Any data object needs a gateway_name as source
    and should inherit base data.
    任何数据对象都需要gateway_name作为源，并且应该继承基本数据
    """
    # 属于哪个交易接口的名称
    gateway_name: str
    # 给extra属性设置默认值default=None， 不参与初始化init=False
    extra: dict = field(default=None, init=False)


@dataclass
class TickData(BaseData):
    """
    Tick data contains information about:
        * last trade in market
        * orderbook snapshot
        * intraday market statistics.

    Tick数据包含以下信息：
        *上次市场交易
        *订单快照
        *盘中市场统计数据
    """

    symbol: str  # 品种代码
    exchange: Exchange
    datetime: datetime

    name: str = ""
    volume: float = 0
    turnover: float = 0
    open_interest: float = 0
    last_price: float = 0
    last_volume: float = 0
    limit_up: float = 0
    limit_down: float = 0

    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    pre_close: float = 0

    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0

    localtime: datetime = None

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"  # 品种代码和交易所名称


@dataclass
class BarData(BaseData):
    """
    Candlestick bar data of a certain trading period.
    """

    symbol: str
    exchange: Exchange
    datetime: datetime

    interval: Interval = None
    volume: float = 0
    turnover: float = 0
    open_interest: float = 0
    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    close_price: float = 0

    # zq
    # local_datetime: datetime = None
    # bar_range: float = None

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"

    def __str__(self):
        return f'日期: {self.datetime}  高: {self.high_price}  开: {self.open_price}  低: {self.low_price}  收: {self.close_price}'


@dataclass
class OrderData(BaseData):
    """
    Order data contains information for tracking lastest status
    of a specific order.
    订单状态信息
    """

    symbol: str
    exchange: Exchange
    orderid: str

    type: OrderType = OrderType.LIMIT
    direction: Direction = None
    offset: Offset = Offset.NONE
    price: float = 0
    volume: float = 0
    traded: float = 0
    status: Status = Status.SUBMITTING
    datetime: datetime = None
    reference: str = ""

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_orderid: str = f"{self.gateway_name}.{self.orderid}"

    def is_active(self) -> bool:
        """
        Check if the order is active.
        """
        return self.status in ACTIVE_STATUSES

    def create_cancel_request(self) -> "CancelRequest":
        """
        Create cancel request object from order.
        """
        req: CancelRequest = CancelRequest(
            orderid=self.orderid, symbol=self.symbol, exchange=self.exchange
        )
        return req

    def get_vt_orderid(self):
        return self.vt_orderid

    def setting_order_type(self, zq_type):
        self.zq_type = zq_type

    def __str__(self):
        return f'订单id:{self.vt_orderid}' \
               f'  类型: {self.type.value}' \
               f'  日期: {self.datetime}' \
               f'  方向: {self.direction.value}' \
               f'  价格: {self.price}' \
               f'  状态: {self.status.value}' \



@dataclass
class TradeData(BaseData):
    """
        Trade data contains information of a fill of an order. One order
        can have several trade fills.
        单笔交易信息，一个订单可以有多笔交易
    """

    symbol: str
    exchange: Exchange
    orderid: str
    tradeid: str
    direction: Direction = None  # 方向

    offset: Offset = Offset.NONE  # 开平标志
    price: float = 0  # 成交价格
    volume: float = 0  # 成交数额
    datetime: datetime = None

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_orderid: str = f"{self.gateway_name}.{self.orderid}"
        self.vt_tradeid: str = f"{self.gateway_name}.{self.tradeid}"

    def __str__(self):
        return f"订单id: {self.vt_orderid}  成交时间: {self.datetime} 方向: {self.direction.value} {self.offset.value} 成交价: {self.price}"


@dataclass
class PositionData(BaseData):
    """
        Position data is used for tracking each individual position holding.
        仓位数据
    """

    symbol: str
    exchange: Exchange
    direction: Direction  # 多空方向

    volume: float = 0
    frozen: float = 0
    price: float = 0
    pnl: float = 0
    yd_volume: float = 0

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_positionid: str = f"{self.gateway_name}.{self.vt_symbol}.{self.direction.value}"


@dataclass
class AccountData(BaseData):
    """
        Account data contains information about balance, frozen and
        available.
        帐户数据包含有关余额、冻结和可用的信息
    """

    accountid: str

    balance: float = 0
    frozen: float = 0

    def __post_init__(self) -> None:
        """"""
        self.available: float = self.balance - self.frozen
        self.vt_accountid: str = f"{self.gateway_name}.{self.accountid}"


@dataclass
# 自动生成下面方法
# 初始化方法（init）：自动生成初始化方法，可以根据类中定义的属性来初始化对象。
# 字符串表示方法（repr）：自动生成字符串表示方法，可以让我们方便地查看和调试对象的值。
#
# 相等性比较方法（eq）：自动生成相等性比较方法，可以用来比较两个对象是否相等。
#
# 哈希方法（hash）：自动生成哈希方法，可以让对象被用作字典的键。
#
# 读取和修改属性的方法（getattr、setattr、delattr）：自动生成这些方法，可以方便地读取、修改和删除对象的属性
class LogData(BaseData):
    """
        Log data is used for recording log messages on GUI or in log files.
        日志数据用于在GUI或日志文件中记录日志消息。
    """

    msg: str
    level: int = INFO

    def __post_init__(self) -> None:
        """"""
        self.time: datetime = datetime.now()  # 获取当前时间


@dataclass
class ContractData(BaseData):
    """
        Contract data contains basic information about each contract traded.
        合约数据包含每个交易合约的基本信息
    """

    symbol: str
    exchange: Exchange
    name: str
    product: Product
    size: float
    pricetick: float

    min_volume: float = 1  # minimum trading volume of the contract
    stop_supported: bool = False  # whether server supports stop order
    net_position: bool = False  # whether gateway uses net position volume 净头寸：多空头寸差额
    history_data: bool = False  # whether gateway provides bar history data

    option_strike: float = 0
    option_underlying: str = ""  # vt_symbol of underlying contract
    option_type: OptionType = None
    option_listed: datetime = None
    option_expiry: datetime = None
    option_portfolio: str = ""
    option_index: str = ""  # for identifying options with same strike price

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"  # 合约唯一标识标的物代码和交易所名称组合


@dataclass
class QuoteData(BaseData):
    """
        Quote data contains information for tracking lastest status
        of a specific quote.
        报价数据对象
    """

    symbol: str
    exchange: Exchange
    quoteid: str

    bid_price: float = 0.0
    bid_volume: int = 0
    ask_price: float = 0.0
    ask_volume: int = 0
    bid_offset: Offset = Offset.NONE
    ask_offset: Offset = Offset.NONE
    status: Status = Status.SUBMITTING
    datetime: datetime = None
    reference: str = ""

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_quoteid: str = f"{self.gateway_name}.{self.quoteid}"

    def is_active(self) -> bool:
        """
            Check if the quote is active.
            检查报价是否处于活动状态
        """
        return self.status in ACTIVE_STATUSES

    def create_cancel_request(self) -> "CancelRequest":
        """
            Create cancel request object from quote.
        """
        req: CancelRequest = CancelRequest(
            orderid=self.quoteid, symbol=self.symbol, exchange=self.exchange
        )
        return req


@dataclass
class SubscribeRequest:
    """
        Request sending to specific gateway for subscribing tick data update.

    """

    symbol: str
    exchange: Exchange

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass
class OrderRequest:
    """
        Request sending to specific gateway for creating a new order.
        向交易接口发送新订单请求
    """

    symbol: str
    exchange: Exchange
    direction: Direction
    type: OrderType
    volume: float
    price: float = 0
    offset: Offset = Offset.NONE
    reference: str = ""

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"

    def create_order_data(self, orderid: str, gateway_name: str) -> OrderData:
        """
            Create order data from request.
        """
        order: OrderData = OrderData(
            symbol=self.symbol,
            exchange=self.exchange,
            orderid=orderid,
            type=self.type,
            direction=self.direction,
            offset=self.offset,
            price=self.price,
            volume=self.volume,
            reference=self.reference,
            gateway_name=gateway_name,
        )
        return order


@dataclass
class CancelRequest:
    """
        Request sending to specific gateway for canceling an existing order.
        取消订单请求
    """

    orderid: str
    symbol: str
    exchange: Exchange

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass
class HistoryRequest:
    """
        Request sending to specific gateway for querying history data.
        请求发送到服务器api以查询历史数据
    """

    symbol: str
    exchange: Exchange
    start: datetime
    end: datetime = None
    interval: Interval = None

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"


@dataclass
class QuoteRequest:
    """
        Request sending to specific gateway for creating a new quote.
        获取报价请求
    """

    symbol: str
    exchange: Exchange
    bid_price: float
    bid_volume: int
    ask_price: float
    ask_volume: int
    bid_offset: Offset = Offset.NONE
    ask_offset: Offset = Offset.NONE
    reference: str = ""

    def __post_init__(self) -> None:
        """"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"

    def create_quote_data(self, quoteid: str, gateway_name: str) -> QuoteData:
        """
            Create quote data from request.
        """
        quote: QuoteData = QuoteData(
            symbol=self.symbol,
            exchange=self.exchange,
            quoteid=quoteid,
            bid_price=self.bid_price,
            bid_volume=self.bid_volume,
            ask_price=self.ask_price,
            ask_volume=self.ask_volume,
            bid_offset=self.bid_offset,
            ask_offset=self.ask_offset,
            reference=self.reference,
            gateway_name=gateway_name,
        )
        return quote
