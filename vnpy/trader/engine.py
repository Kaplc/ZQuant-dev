import logging
from logging import Logger
import smtplib
import os
from abc import ABC
from pathlib import Path
from datetime import datetime
from email.message import EmailMessage
from queue import Empty, Queue
from threading import Thread
from typing import Any, Type, Dict, List, Optional

from vnpy.event import Event, EventEngine
from .app import BaseApp
from .event import (
    EVENT_TICK,
    EVENT_ORDER,
    EVENT_TRADE,
    EVENT_POSITION,
    EVENT_ACCOUNT,
    EVENT_CONTRACT,
    EVENT_LOG,
    EVENT_QUOTE
)
from .gateway import BaseGateway
from .object import (
    CancelRequest,
    LogData,
    OrderRequest,
    QuoteData,
    QuoteRequest,
    SubscribeRequest,
    HistoryRequest,
    OrderData,
    BarData,
    TickData,
    TradeData,
    PositionData,
    AccountData,
    ContractData,
    Exchange
)
from .setting import SETTINGS
from .utility import get_folder_path, TRADER_DIR
from .converter import OffsetConverter


class MainEngine:
    """
    Acts as the core of the trading platform.
    """

    def __init__(self, event_engine: EventEngine = None) -> None:
        """
        主引擎初始化

        :param event_engine: # 获取事件引擎， 没有默认设置空
        """
        if event_engine:  # 判断有无事件引擎
            self.event_engine: EventEngine = event_engine
        else:
            # 没有事件引擎就创建
            self.event_engine = EventEngine()
        # 启动事件引擎
        self.event_engine.start()

        # 空字典存储配置
        self.gateways: Dict[str, BaseGateway] = {}  # 交易所接口字典
        self.engines: Dict[str, BaseEngine] = {}  # 引擎字典
        self.apps: Dict[str, BaseApp] = {}  # 子应用字典
        self.exchanges: List[Exchange] = []  # 交易所字典

        # os.chdir() 函数会将当前工作目录更改为这个路径
        os.chdir(TRADER_DIR)  # Change working directory 更改工作目录
        self.init_engines()  # Initialize function engines 初始化功能引擎

    def add_engine(self, engine_class: Any) -> "BaseEngine":  # 参数:引擎类
        """
        Add function engine.
        添加引擎
        在该方法中，首先使用 engine_class 创建一个新的引擎对象 engine，该引擎对象需要两个参数：
        一个是引擎管理器对象本身，一个是事件引擎（event engine）对象。
        然后将新创建的引擎对象添加到引擎管理器的 engines 字典中，字典的键是引擎的名称，值是引擎对象。最后，返回新添加的引擎对象 engine
        """
        engine: BaseEngine = engine_class(self, self.event_engine)  # 创建新的引擎实例对象
        self.engines[engine.engine_name] = engine  # 添加新引擎对象进字典
        return engine

    def add_gateway(self, gateway_class: Type[BaseGateway], gateway_name: str = "") -> BaseGateway:
        """
        Add gateway.
        添加与交易所对接网关

        """
        # Use default name if gateway_name not passed 如果没有gateway_name，则使用gateway_class的默认名称
        if not gateway_name:
            gateway_name: str = gateway_class.default_name

        gateway: BaseGateway = gateway_class(self.event_engine, gateway_name)
        self.gateways[gateway_name] = gateway  # 新交易所接口实例添加进字典

        # Add gateway supported exchanges into engine
        for exchange in gateway.exchanges:
            if exchange not in self.exchanges:
                self.exchanges.append(exchange)  # 交易所添加进字典

        return gateway

    def add_app(self, app_class: Type[BaseApp]) -> "BaseEngine":
        """
        Add app.
        子应用
        """
        app: BaseApp = app_class()  # 创建app实例
        self.apps[app.app_name] = app  # 添加 'app.name':app对象 -> self.apps字典

        engine: BaseEngine = self.add_engine(app.engine_class)  # 添加app引擎 -> self.add_engine字典
        return engine

    def init_engines(self) -> None:
        """
        Init all engines.
        初始化所有引擎。
        """
        self.add_engine(LogEngine)  # 添加日志引擎
        self.add_engine(OmsEngine)  # 订单管理引擎
        self.add_engine(EmailEngine)  # 添加邮箱引擎

    def write_log(self, msg: str, source: str = "") -> None:
        """
        Put log event with specific message.
        将日志事件与特定消息一起放入
        """
        log: LogData = LogData(msg=msg, gateway_name=source)  # 创建日志数据实例
        event: Event = Event(EVENT_LOG, log)  # 生成日志事件
        self.event_engine.put(event)  # 加入事件处理队列

    def get_gateway(self, gateway_name: str) -> BaseGateway:
        """
        Return gateway object by name.
        获取交易接口名称
        """
        gateway: BaseGateway = self.gateways.get(gateway_name, None)
        if not gateway:
            self.write_log(f"找不到底层接口：{gateway_name}")
        return gateway

    def get_engine(self, engine_name: str) -> "BaseEngine":
        """
        Return engine object by name.
        获取引擎名字
        """
        engine: BaseEngine = self.engines.get(engine_name, None)
        if not engine:
            self.write_log(f"找不到引擎：{engine_name}")
        return engine

    def get_default_setting(self, gateway_name: str) -> Optional[Dict[str, Any]]:
        """
        Get default setting dict of a specific gateway.
        获取交易接口配置信息
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            return gateway.get_default_setting()
        return None

    def get_all_gateway_names(self) -> List[str]:
        """
        Get all names of gateway added in main engine.
        获取所有交易接口名字
        """
        return list(self.gateways.keys())

    def get_all_apps(self) -> List[BaseApp]:
        """
        Get all app objects.
        获取所有子应用对象
        """
        return list(self.apps.values())

    def get_all_exchanges(self) -> List[Exchange]:
        """
        Get all exchanges.
        获取所有交易所
        """
        return self.exchanges

    def connect(self, setting: dict, gateway_name: str) -> None:
        """
        Start connection of a specific gateway.
        交易接口开启链接
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.connect(setting)  # 载入配置信息并链接

    def subscribe(self, req: SubscribeRequest, gateway_name: str) -> None:
        """
        Subscribe tick data update of a specific gateway.
        订阅交易所数据更新
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.subscribe(req)

    def send_order(self, req: OrderRequest, gateway_name: str) -> str:
        """
        Send new order request to a specific gateway.
        通过交易接口向交易所发送新订单请求
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            return gateway.send_order(req)
        else:
            return ""

    def cancel_order(self, req: CancelRequest, gateway_name: str) -> None:
        """
        Send cancel order request to a specific gateway.
        取消订单
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.cancel_order(req)

    def send_quote(self, req: QuoteRequest, gateway_name: str) -> str:
        """
        Send new quote request to a specific gateway.
        发送新委托
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            return gateway.send_quote(req)
        else:
            return ""

    def cancel_quote(self, req: CancelRequest, gateway_name: str) -> None:
        """
        Send cancel quote request to a specific gateway.
        取消委托
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            gateway.cancel_quote(req)

    def query_history(self, req: HistoryRequest, gateway_name: str) -> Optional[List[BarData]]:
        """
        Query bar history data from a specific gateway.
        查询历史数据
        """
        gateway: BaseGateway = self.get_gateway(gateway_name)
        if gateway:
            return gateway.query_history(req)
        else:
            return None

    def close(self) -> None:
        """
        Make sure every gateway and app is closed properly before
        programme exit.
        关闭主引擎
        """
        # Stop event engine first to prevent new timer event.
        self.event_engine.stop()  # 停止事件引擎

        for engine in self.engines.values():  # 遍历所有引擎对象并关闭
            engine.close()

        for gateway in self.gateways.values():  # 遍历所有交易接口对象并关闭
            gateway.close()


class BaseEngine(ABC):
    """
    Abstract class for implementing a function engine.
    用于实现函数引擎的抽象类。

    采用了抽象基类（ABC）的方式，表示这是一个抽象类。抽象类是指不能被直接实例化的类，
    它的主要作用是提供一组接口定义，让子类实现这些接口来完成具体的功能
    """

    def __init__(
            self,
            main_engine: MainEngine,
            event_engine: EventEngine,
            engine_name: str,
    ) -> None:
        """"""
        self.main_engine: MainEngine = main_engine  # 定义主引擎
        self.event_engine: EventEngine = event_engine  # 定义事件引擎
        self.engine_name: str = engine_name  # 定义引擎名字

    def close(self) -> None:
        """"""
        pass


class LogEngine(BaseEngine):
    """
    Processes log event and output with logging module.
    使用日志模块处理日志事件和输出
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        # super(LogEngine, self)-获取 "LogEngine" 类的父类对象，返回一个父类的对象，该对象允许我们调用父类的方法
        super(LogEngine, self).__init__(main_engine, event_engine, "log")  # 调用BaseEngine的init方法

        if not SETTINGS["log.active"]:  # 判断从配置文件日志是否需要启动
            return

        self.level: int = SETTINGS["log.level"]  # 日志等级

        self.logger: Logger = logging.getLogger("veighna")  # 以"veighna"命名生成日志器对象
        self.logger.setLevel(self.level)  # 设置日志器输出日志等级

        self.formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s  %(levelname)s: %(message)s"
        )  # 日志输出格式

        self.add_null_handler()

        if SETTINGS["log.console"]:
            self.add_console_handler()

        if SETTINGS["log.file"]:
            self.add_file_handler()

        self.register_event()

    def add_null_handler(self) -> None:
        """
        Add null handler for logger.
        临时输出日志不保存
        """
        null_handler: logging.NullHandler = logging.NullHandler()
        self.logger.addHandler(null_handler)

    def add_console_handler(self) -> None:
        """
        Add console output of log.
        控制台输出日志记录
        """
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def add_file_handler(self) -> None:
        """
        Add file output of log.
        文件保存日志
        """
        today_date: str = datetime.now().strftime("%Y%m%d")
        filename: str = f"vt_{today_date}.log"
        log_path: Path = get_folder_path("log")
        file_path: Path = log_path.joinpath(filename)

        file_handler: logging.FileHandler = logging.FileHandler(
            file_path, mode="a", encoding="utf8"
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def register_event(self) -> None:
        """"""
        self.event_engine.register(EVENT_LOG, self.process_log_event)  # 将事件类型和处理函数穿入事件引擎注册

    def process_log_event(self, event: Event) -> None:
        """
        Process log event.
        """
        log: LogData = event.data
        self.logger.log(log.level, log.msg)  # 记录日志信息


class OmsEngine(BaseEngine):
    """
    Provides order management system function.
    提供订单管理系统功能。
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super(OmsEngine, self).__init__(main_engine, event_engine, "oms")  # 调用BaseEngine的init方法

        self.ticks: Dict[str, TickData] = {}  # 键-交易品种的代码， 值-TickData对象
        self.orders: Dict[str, OrderData] = {}  # 订单的唯一标识符 - 订单对象
        self.trades: Dict[str, TradeData] = {}  # 交易的唯一标识符 - 交易的成交信息
        self.positions: Dict[str, PositionData] = {}  # 交易品种 - 持仓信息
        self.accounts: Dict[str, AccountData] = {}  # 交易账户 - 资金信息
        self.contracts: Dict[str, ContractData] = {}  # 交易品种 - 合约信息
        self.quotes: Dict[str, QuoteData] = {}  # 交易品种 - 报价数据

        self.active_orders: Dict[str, OrderData] = {}  # 活动订单(未成交或部分成交): 订单的唯一标识符 - 订单对象
        self.active_quotes: Dict[str, QuoteData] = {}  # 活动Quote(未成交或部分成交): 交易品种 - 报价数据

        self.offset_converters: Dict[str, OffsetConverter] = {}  # 交易时区转换器

        self.add_function()
        self.register_event()

    def add_function(self) -> None:
        """Add query function to main engine."""
        self.main_engine.get_tick = self.get_tick
        self.main_engine.get_order = self.get_order
        self.main_engine.get_trade = self.get_trade
        self.main_engine.get_position = self.get_position
        self.main_engine.get_account = self.get_account
        self.main_engine.get_contract = self.get_contract
        self.main_engine.get_quote = self.get_quote

        self.main_engine.get_all_ticks = self.get_all_ticks
        self.main_engine.get_all_orders = self.get_all_orders
        self.main_engine.get_all_trades = self.get_all_trades
        self.main_engine.get_all_positions = self.get_all_positions
        self.main_engine.get_all_accounts = self.get_all_accounts
        self.main_engine.get_all_contracts = self.get_all_contracts
        self.main_engine.get_all_quotes = self.get_all_quotes
        self.main_engine.get_all_active_orders = self.get_all_active_orders
        self.main_engine.get_all_active_quotes = self.get_all_active_quotes

        self.main_engine.update_order_request = self.update_order_request
        self.main_engine.convert_order_request = self.convert_order_request
        self.main_engine.get_converter = self.get_converter

    def register_event(self) -> None:
        """注册事件"""
        self.event_engine.register(EVENT_TICK, self.process_tick_event)
        self.event_engine.register(EVENT_ORDER, self.process_order_event)
        self.event_engine.register(EVENT_TRADE, self.process_trade_event)
        self.event_engine.register(EVENT_POSITION, self.process_position_event)
        self.event_engine.register(EVENT_ACCOUNT, self.process_account_event)
        self.event_engine.register(EVENT_CONTRACT, self.process_contract_event)
        self.event_engine.register(EVENT_QUOTE, self.process_quote_event)

    def process_tick_event(self, event: Event) -> None:
        """处理tick事件"""
        tick: TickData = event.data
        self.ticks[tick.vt_symbol] = tick  # # 品种.交易所名称 - tick信息对象

    def process_order_event(self, event: Event) -> None:
        """处理订单委托"""
        order: OrderData = event.data
        self.orders[order.vt_orderid] = order  # 添加订单信息对象

        # If order is active, then update data in dict.
        if order.is_active():  # 更新委托
            self.active_orders[order.vt_orderid] = order
        # Otherwise, pop inactive order from in dict
        elif order.vt_orderid in self.active_orders:  # 删除过期委托
            self.active_orders.pop(order.vt_orderid)

        # Update to offset converter 字典中get出对应交易所名称的时区转换器
        converter: OffsetConverter = self.offset_converters.get(order.gateway_name, None)
        if converter:
            converter.update_order(order)

    def process_trade_event(self, event: Event) -> None:
        """交易"""
        trade: TradeData = event.data
        self.trades[trade.vt_tradeid] = trade  # 添加交易信息对象

        # Update to offset converter 获取时区转换器
        converter: OffsetConverter = self.offset_converters.get(trade.gateway_name, None)
        if converter:
            converter.update_trade(trade)

    def process_position_event(self, event: Event) -> None:
        """持仓"""
        position: PositionData = event.data
        self.positions[position.vt_positionid] = position  # 添加持仓信息对象

        # Update to offset converter 获取时区转换器
        converter: OffsetConverter = self.offset_converters.get(position.gateway_name, None)
        if converter:
            converter.update_position(position)

    def process_account_event(self, event: Event) -> None:
        """账户"""
        account: AccountData = event.data
        self.accounts[account.vt_accountid] = account  # 添加持仓信息对象

    def process_contract_event(self, event: Event) -> None:
        """合约"""
        contract: ContractData = event.data
        self.contracts[contract.vt_symbol] = contract  # 添加合约信息对象

        # Initialize offset converter for each gateway 初始化每个交易接口的时区转换器
        if contract.gateway_name not in self.offset_converters:
            self.offset_converters[contract.gateway_name] = OffsetConverter(self)

    def process_quote_event(self, event: Event) -> None:
        """盘口报价"""
        quote: QuoteData = event.data
        self.quotes[quote.vt_quoteid] = quote  # 添加盘口报价信息对象

        # If quote is active, then update data in dict.
        if quote.is_active():  # 更新盘口信息对象
            self.active_quotes[quote.vt_quoteid] = quote
        # Otherwise, pop inactive quote from in dict # 移除过期盘口对象
        elif quote.vt_quoteid in self.active_quotes:
            self.active_quotes.pop(quote.vt_quoteid)

    def get_tick(self, vt_symbol: str) -> Optional[TickData]:
        """
            Get latest market tick data by vt_symbol.
            用vt_symbol获取tick对象
        """
        return self.ticks.get(vt_symbol, None)

    def get_order(self, vt_orderid: str) -> Optional[OrderData]:
        """
            Get latest order data by vt_orderid.
            用vt_symbol获取tick对象
        """
        return self.orders.get(vt_orderid, None)

    def get_trade(self, vt_tradeid: str) -> Optional[TradeData]:
        """
            Get trade data by vt_tradeid.
            用vt_symbol获取trades对象
        """
        return self.trades.get(vt_tradeid, None)

    def get_position(self, vt_positionid: str) -> Optional[PositionData]:
        """
            Get latest position data by vt_positionid.
            vt_positionid获取仓位对象
        """
        return self.positions.get(vt_positionid, None)

    def get_account(self, vt_accountid: str) -> Optional[AccountData]:
        """
            Get latest account data by vt_accountid.
            vt_accountid获取账户对象
        """
        return self.accounts.get(vt_accountid, None)

    def get_contract(self, vt_symbol: str) -> Optional[ContractData]:
        """
            Get contract data by vt_symbol.
            vt_symbol获取合约对象
        """
        return self.contracts.get(vt_symbol, None)

    def get_quote(self, vt_quoteid: str) -> Optional[QuoteData]:
        """
            Get latest quote data by vt_orderid.
            vt_orderid获取盘口对象
        """
        return self.quotes.get(vt_quoteid, None)

    def get_all_ticks(self) -> List[TickData]:
        """
            Get all tick data.
            获取所有tick
        """
        return list(self.ticks.values())

    def get_all_orders(self) -> List[OrderData]:
        """
            Get all order data.
            获取所有订单
        """
        return list(self.orders.values())

    def get_all_trades(self) -> List[TradeData]:
        """
            Get all trade data.
            获取所有交易
        """
        return list(self.trades.values())

    def get_all_positions(self) -> List[PositionData]:
        """
            Get all position data.
            获取所有仓位
        """
        return list(self.positions.values())

    def get_all_accounts(self) -> List[AccountData]:
        """
            Get all account data.
            获取所有账户
        """
        return list(self.accounts.values())

    def get_all_contracts(self) -> List[ContractData]:
        """
            Get all contract data.
            获取所有合约
        """
        return list(self.contracts.values())

    def get_all_quotes(self) -> List[QuoteData]:
        """
            Get all quote data.
            获取所有盘口信息
        """
        return list(self.quotes.values())

    def get_all_active_orders(self, vt_symbol: str = "") -> List[OrderData]:
        """
            Get all active orders by vt_symbol.

            If vt_symbol is empty, return all active orders.
            获取所有活跃订单
        """
        if not vt_symbol:  # 无指定交易对返回全部
            return list(self.active_orders.values())
        else:  # 返回指定交易对对应的订单对象
            active_orders: List[OrderData] = [
                order
                for order in self.active_orders.values()
                if order.vt_symbol == vt_symbol
            ]
            return active_orders

    def get_all_active_quotes(self, vt_symbol: str = "") -> List[QuoteData]:
        """
            Get all active quotes by vt_symbol.
            If vt_symbol is empty, return all active qutoes.
            获取活跃盘口
        """
        if not vt_symbol:  # 无指定交易对返回全部
            return list(self.active_quotes.values())
        else:  # 返回指定交易对对应的盘口对象
            active_quotes: List[QuoteData] = [
                quote
                for quote in self.active_quotes.values()
                if quote.vt_symbol == vt_symbol
            ]
            return active_quotes

    def update_order_request(self, req: OrderRequest, vt_orderid: str, gateway_name: str) -> None:
        """
            Update order request to offset converter.
            更新订单信息的通过转换器
        """
        converter: OffsetConverter = self.offset_converters.get(gateway_name, None)
        if converter:
            converter.update_order_request(req, vt_orderid)

    def convert_order_request(
            self,
            req: OrderRequest,
            gateway_name: str,
            lock: bool,
            net: bool = False
    ) -> List[OrderRequest]:
        """
            Convert original order request according to given mode.
            通过转换器转换原始订单请求为框架可处理的请求
        """
        converter: OffsetConverter = self.offset_converters.get(gateway_name, None)
        if not converter:  # 无转换器直接返回请求
            return [req]

        reqs: List[OrderRequest] = converter.convert_order_request(req, lock, net)
        return reqs

    def get_converter(self, gateway_name: str) -> OffsetConverter:
        """
            Get offset converter object of specific gateway.
            获取对应交易接口的订单请求转换器
        """
        return self.offset_converters.get(gateway_name, None)


class EmailEngine(BaseEngine):
    """
        Provides email sending function.
        发送邮件引擎
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super(EmailEngine, self).__init__(main_engine, event_engine, "email")

        self.thread: Thread = Thread(target=self.run)  # 多线程异步执行
        self.queue: Queue = Queue()  # 创建邮件处理队列对象
        self.active: bool = False  # 发送邮件引擎启动标识

        self.main_engine.send_email = self.send_email  # 定义主引擎直接调用发送邮件方法

    def send_email(self, subject: str, content: str, receiver: str = "") -> None:
        """"""
        # Start email engine when sending first email.
        if not self.active:
            self.start()

        # Use default receiver if not specified. # 没有传入收件人邮箱，使用配置默认邮箱
        if not receiver:
            receiver: str = SETTINGS["email.receiver"]

        # 发送邮件
        msg: EmailMessage = EmailMessage()
        msg["From"] = SETTINGS["email.sender"]  # 发件人
        msg["To"] = receiver  # 收件人
        msg["Subject"] = subject  # 标题
        msg.set_content(content)  # 内容

        self.queue.put(msg)  # 加入处理队列

    def run(self) -> None:
        """"""
        while self.active:
            try:
                msg: EmailMessage = self.queue.get(block=True, timeout=1)  # 取出队列任务

                with smtplib.SMTP_SSL(  # 传入邮件服务器的地址和端口号
                        SETTINGS["email.server"], SETTINGS["email.port"]
                ) as smtp:
                    smtp.login(  # 登录邮箱
                        SETTINGS["email.username"], SETTINGS["email.password"]
                    )
                    smtp.send_message(msg)  # 发送邮件
            except Empty:
                pass

    def start(self) -> None:
        """"""
        self.active = True
        self.thread.start()  # 多线程执行self.run()

    def close(self) -> None:
        """"""
        if not self.active:
            return

        self.active = False
        self.thread.join()  # 等待线程任务完成后关闭
