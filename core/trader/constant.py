"""
General constant enums used in the trading platform.
"""

from enum import Enum


# 继承枚举类限制取值

class Direction(Enum):
    """
    Direction of order/trade/position.
    开仓方向
    """
    LONG = "多"
    SHORT = "空"
    NET = "净"


class Offset(Enum):
    """
    Offset of order/trade.
    开平仓
    """
    NONE = ""
    OPEN = "开"
    CLOSE = "平"
    CLOSETODAY = "平今"
    CLOSEYESTERDAY = "平昨"


class Status(Enum):
    """
    Order status.
    订单状态
    """
    SUBMITTING = "提交中"
    NOTTRADED = "未成交"
    PARTTRADED = "部分成交"
    ALLTRADED = "全部成交"
    CANCELLED = "已撤销"
    REJECTED = "拒单"


class Product(Enum):
    """
    Product class.
    交易品种类型
    """
    EQUITY = "股票"
    FUTURES = "期货"
    OPTION = "期权"
    INDEX = "指数"
    FOREX = "外汇"
    SPOT = "现货"
    ETF = "ETF"
    BOND = "债券"
    WARRANT = "权证"
    SPREAD = "价差"
    FUND = "基金"


class OrderType(Enum):
    """
    Order type.
    挂单类型
    """
    LIMIT = "限价"
    MARKET = "市价"
    STOP = "STOP"
    FAK = "FAK"
    FOK = "FOK"
    RFQ = "询价"


class OptionType(Enum):
    """
    Option type.
    """
    CALL = "看涨期权"
    PUT = "看跌期权"


class Exchange(Enum):
    """
    Exchange.
    交易所
    """
    # Chinese
    # CFFEX = "CFFEX"  # China Financial Futures Exchange
    # SHFE = "SHFE"  # Shanghai Futures Exchange
    # CZCE = "CZCE"  # Zhengzhou Commodity Exchange
    # DCE = "DCE"  # Dalian Commodity Exchange
    # INE = "INE"  # Shanghai International Energy Exchange
    # GFEX = "GFEX"  # Guangzhou Futures Exchange
    # SSE = "SSE"  # Shanghai Stock Exchange
    # SZSE = "SZSE"  # Shenzhen Stock Exchange
    # BSE = "BSE"  # Beijing Stock Exchange
    # SGE = "SGE"  # Shanghai Gold Exchange
    # WXE = "WXE"  # Wuxi Steel Exchange
    # CFETS = "CFETS"  # CFETS Bond Market Maker Trading System
    # XBOND = "XBOND"  # CFETS X-Bond Anonymous Trading System

    # Global
    # SMART = "SMART"  # Smart Router for US stocks
    # NYSE = "NYSE"  # New York Stock Exchnage
    # NASDAQ = "NASDAQ"  # Nasdaq Exchange
    # ARCA = "ARCA"  # ARCA Exchange
    # EDGEA = "EDGEA"  # Direct Edge Exchange
    # ISLAND = "ISLAND"  # Nasdaq Island ECN
    # BATS = "BATS"  # Bats Global Markets
    # IEX = "IEX"  # The Investors Exchange
    # AMEX = "AMEX"  # American Stock Exchange
    # TSE = "TSE"  # Toronto Stock Exchange
    # NYMEX = "NYMEX"  # New York Mercantile Exchange
    # COMEX = "COMEX"  # COMEX of CME
    # GLOBEX = "GLOBEX"  # Globex of CME
    # IDEALPRO = "IDEALPRO"  # Forex ECN of Interactive Brokers
    # CME = "CME"  # Chicago Mercantile Exchange
    # ICE = "ICE"  # Intercontinental Exchange
    # SEHK = "SEHK"  # Stock Exchange of Hong Kong
    # HKFE = "HKFE"  # Hong Kong Futures Exchange
    # SGX = "SGX"  # Singapore Global Exchange
    # CBOT = "CBT"  # Chicago Board of Trade
    # CBOE = "CBOE"  # Chicago Board Options Exchange
    # CFE = "CFE"  # CBOE Futures Exchange
    # DME = "DME"  # Dubai Mercantile Exchange
    # EUREX = "EUX"  # Eurex Exchange
    # APEX = "APEX"  # Asia Pacific Exchange
    # LME = "LME"  # London Metal Exchange
    # BMD = "BMD"  # Bursa Malaysia Derivatives
    # TOCOM = "TOCOM"  # Tokyo Commodity Exchange
    # EUNX = "EUNX"  # Euronext Exchange
    # KRX = "KRX"  # Korean Exchange
    # OTC = "OTC"  # OTC Product (Forex/CFD/Pink Sheet Equity)
    # IBKRATS = "IBKRATS"  # Paper Trading Exchange of IB

    # Special Function
    # LOCAL = "LOCAL"  # For local generated data

    # CryptoCoin
    BINANCE = "BINANCE"  # 币安


class Currency(Enum):
    """
    Currency.
    货币单位
    """
    USD = "USD"
    HKD = "HKD"
    CNY = "CNY"
    CAD = "CAD"


class Interval(Enum):
    """
    Interval of bar data.
    K线周期
    """
    MINUTE = "1m"
    MINUTE_15 = "15m"
    HOUR = "1h"
    DAILY = "d"
    # DAILY = "1d"
    WEEKLY = "w"
    TICK = "tick"
