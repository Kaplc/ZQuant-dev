import csv
from datetime import datetime
from typing import List, Optional, Callable

from core.trader.engine import BaseEngine, MainEngine, EventEngine
from core.trader.constant import Interval, Exchange
from core.trader.object import BarData, TickData, ContractData, HistoryRequest
from core.trader.database import BaseDatabase, get_database, BarOverview, DB_TZ
from core.trader.datafeed import BaseDatafeed, get_datafeed
from core.trader.utility import ZoneInfo

APP_NAME = "DataManager"


class ManagerEngine(BaseEngine):
    """数据库管理引擎"""

    def __init__(
            self,
            main_engine: MainEngine,
            event_engine: EventEngine,
    ) -> None:
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.database: BaseDatabase = get_database()  # 获取数据库对象
        self.datafeed: BaseDatafeed = get_datafeed()  # 获取数据服务对象

    def import_data_from_csv(
            self,
            file_path: str,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            tz_name: str,
            datetime_head: str,
            open_head: str,
            high_head: str,
            low_head: str,
            close_head: str,
            volume_head: str,
            turnover_head: str,
            open_interest_head: str,
            datetime_format: str
    ) -> tuple:
        """csv文件导入数据"""
        with open(file_path, "rt") as f:
            buf: list = [line.replace("\0", "") for line in f]

        reader: csv.DictReader = csv.DictReader(buf, delimiter=",")

        bars: List[BarData] = []
        start: datetime = None
        count: int = 0
        tz = ZoneInfo(tz_name)

        for item in reader:
            if datetime_format:
                dt: datetime = datetime.strptime(item[datetime_head], datetime_format)
            else:
                dt: datetime = datetime.fromisoformat(item[datetime_head])
            dt = dt.replace(tzinfo=tz)

            turnover = item.get(turnover_head, 0)
            open_interest = item.get(open_interest_head, 0)

            bar: BarData = BarData(
                symbol=symbol,
                exchange=exchange,
                datetime=dt,
                interval=interval,
                volume=float(item[volume_head]),
                open_price=float(item[open_head]),
                high_price=float(item[high_head]),
                low_price=float(item[low_head]),
                close_price=float(item[close_head]),
                turnover=float(turnover),
                open_interest=float(open_interest),
                gateway_name="DB",
            )

            bars.append(bar)

            # do some statistics
            count += 1
            if not start:
                start = bar.datetime

        end: datetime = bar.datetime

        # insert into database 保存到数据库
        self.database.save_bar_data(bars)

        return start, end, count

    def output_data_to_csv(
            self,
            file_path: str,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ) -> bool:
        """数据库导出数据成csv"""
        bars: List[BarData] = self.load_bar_data(symbol, exchange, interval, start, end)

        fieldnames: list = [
            "symbol",
            "exchange",
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
            "open_interest"
        ]

        try:
            with open(file_path, "w") as f:
                writer: csv.DictWriter = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                writer.writeheader()

                for bar in bars:
                    d: dict = {
                        "symbol": bar.symbol,
                        "exchange": bar.exchange.value,
                        "datetime": bar.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": bar.open_price,
                        "high": bar.high_price,
                        "low": bar.low_price,
                        "close": bar.close_price,
                        "turnover": bar.turnover,
                        "volume": bar.volume,
                        "open_interest": bar.open_interest,
                    }
                    writer.writerow(d)

            return True
        except PermissionError:
            return False

    def get_bar_overview(self) -> List[BarOverview]:
        """调用database对象"""
        return self.database.get_bar_overview()

    def load_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval,
            start: datetime,
            end: datetime
    ) -> List[BarData]:
        """"""
        bars: List[BarData] = self.database.load_bar_data(
            symbol,
            exchange,
            interval,
            start,
            end
        )

        return bars

    def delete_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: Interval
    ) -> int:
        """"""
        count: int = self.database.delete_bar_data(
            symbol,
            exchange,
            interval
        )

        return count

    def download_bar_data(
            self,
            symbol: str,
            exchange: Exchange,
            interval: str,
            start: datetime,
            output: Callable,
    ) -> int:
        """
        Query bar data from datafeed. 服务器下载K线数据
        """
        # 创建请求对象
        req: HistoryRequest = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            interval=Interval(interval),
            start=start,
            end=datetime.now(DB_TZ)
        )

        vt_symbol: str = f"{symbol}.{exchange.value}"
        contract: Optional[ContractData] = self.main_engine.get_contract(vt_symbol)

        # If history data provided in gateway, then query 交易接口获取历史数据
        if contract and contract.history_data:
            data: List[BarData] = self.main_engine.query_history(
                req, contract.gateway_name
            )
        # Otherwise use datafeed to query data 数据服务获取
        else:
            data: List[BarData] = self.datafeed.query_bar_history(req, output)

        if data:
            self.database.save_bar_data(data)
            return (len(data))

        return 0

    def download_tick_data(
            self,
            symbol: str,
            exchange: Exchange,
            start: datetime,
            output: Callable
    ) -> int:
        """
        Query tick data from datafeed. 服务器下载tick数据
        """
        req: HistoryRequest = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            start=start,
            end=datetime.now(DB_TZ)
        )

        data: List[TickData] = self.datafeed.query_tick_history(req, output)  # 数据服务获取

        if data:
            self.database.save_tick_data(data)
            return (len(data))

        return 0
