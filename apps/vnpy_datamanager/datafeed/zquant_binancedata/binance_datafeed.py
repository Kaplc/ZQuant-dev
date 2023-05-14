import csv
import zipfile
import os
from datetime import datetime, timedelta
from typing import List, Optional, Callable
from numpy import ndarray

from apps.vnpy_datamanager import ManagerEngine
from core.trader.setting import SETTINGS
from core.trader.constant import Exchange, Interval
from core.trader.object import BarData, TickData, HistoryRequest
from core.trader.utility import ZoneInfo
from core.trader.datafeed import BaseDatafeed
from sdk.binance_sdk.binance.download.download_kline import download_daily_klines


class BinanceDatafeed(BaseDatafeed):
    """binance数据服务接口"""

    def __init__(self, mainEngine):
        """"""
        self.mainEngine = mainEngine
        self.username: str = SETTINGS["datafeed.username"]
        self.password: str = SETTINGS["datafeed.password"]

        self.inited: bool = False
        self.symbols: ndarray = None

    def init(self, output: Callable = print) -> bool:
        """初始化"""
        pass

    def query_bar_history(self, req: HistoryRequest, output: Callable = print) -> Optional[
        List[BarData]]:
        """查询K线数据"""
        converted_req = self._req_converter(req)
        save_path = os.path.dirname(os.path.abspath(__file__))
        # binanceSDK下载历史行情
        download_path = download_daily_klines(
            trading_type=converted_req.trading_type,
            symbols=converted_req.symbols,
            intervals=converted_req.intervals,
            start_date=converted_req.start_date,
            end_date=converted_req.end_date,
            folder=save_path,
        )

        if download_path is None:
            output('网络可能出现异常!')
            return []

        # 批量解压zip成csv
        csv_path = self._unzip_to_csv(download_path, req, output)
        # 批量加载csv
        data: List[BarData] = self._import_data_from_csv(
            folder_path=csv_path,
            symbol=req.symbol,
            exchange=req.exchange,
            interval=req.interval,
            tz_name=SETTINGS['timezone'],
            datetime_head='open_time',
            open_head='open',
            high_head='high',
            low_head='low',
            close_head='close',
            volume_head='volume',
            turnover_head='quote_volume',
            open_interest_head='open_interest',
            datetime_format='%Y-%m-%d %H:%M:%S'
        )
        return data

    def query_tick_history(self, req: HistoryRequest, output: Callable = print) -> Optional[List[TickData]]:
        """查询Tick数据"""
        pass

    def _import_data_from_csv(
            self,
            folder_path: str,
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
    ) -> List[BarData]:
        """csv文件导入数据"""
        # 定义表头
        header = 'open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n'
        print(f"正在读取csv.")

        files = os.listdir(folder_path)  # 获取csv的文件夹中的所有文件
        sorted_files = sorted(files, key=self._parse_file_name)  # 文件列表并降序

        dataManager: ManagerEngine = self.mainEngine.get_engine("DataManager")  # 获取DataManager对象
        overviews = dataManager.get_bar_overview()

        existOverview = False
        filter_files = []
        if overviews:
            for overview in overviews:
                # 将‘d’转'1d'
                if interval.value == 'd':
                    goalInterval = '1' + interval.value
                else:
                    goalInterval = interval.value

                # 数据库存在该数据作过滤处理
                if overview.symbol == symbol and overview.interval.value == goalInterval:
                    existOverview = True
                    start_overview = overview.start
                    end_overview = overview.end

                    for file in sorted_files:
                        dt = self._parse_file_name(file)
                        if dt < start_overview or dt > end_overview:
                            filter_files.append(file)

                    sorted_files = filter_files

                    break

        data: List[BarData] = []
        # 循环处理每个文件
        for file in sorted_files:
            file_path = os.path.join(folder_path, file)

            if file.endswith('.csv'):  # 只处理后缀名为 .csv 的文件
                with open(file_path, "rt") as f:
                    buf: list = [line.replace("\0", "") for line in f]

                if header != buf[0]:  # 无表头动态添加
                    buf.insert(0, header)

                reader: csv.DictReader = csv.DictReader(buf, delimiter=",")

                start: datetime = None
                count: int = 0
                tz = ZoneInfo(tz_name)

                for item in reader:

                    dt = self._csv_time_converter(item[datetime_head])  # datetime转换

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

                    data.append(bar)

                    # do some statistics
                    count += 1
                    # if not start:
                    #     start = bar.datetime

        # end: datetime = bar.datetime
        return data

    def _parse_file_name(self, file_name):
        """以日期时间排序key"""
        # 获取日期部分，并解析为日期时间对象
        split_list = file_name.split(".")[0].split("-")
        dt_str = split_list[2] + '-' + split_list[3] + '-' + split_list[4]
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        return dt

    def _csv_time_converter(self, sum_second):
        """
        转换币安下载历史数据的csv时间
        :param sum_second: 从 1970 年 1 月 1 日开始的毫秒数
        :return: datetime
        """
        # 计算对应的秒数
        seconds_since_1970 = int(sum_second) // 1000
        # 创建一个表示 1970 年 1 月 1 日的 datetime 对象
        year_1970 = datetime(1970, 1, 1)
        # 计算 1970 年 1 月 1 日开始的时间差
        time_difference = timedelta(seconds=seconds_since_1970)
        # 计算对应的日期
        target_date = year_1970 + time_difference
        return target_date

    def _req_converter(self, req):
        """请求转换成sdk合法参数"""

        # 设置获取的交易类型cm，um，spot
        trading_type: str = 'um'
        # 交易对列表
        symbols: list = []
        symbols.append(req.symbol)
        # 时间周期
        intervals: list = []
        intervals.append(req.interval.value)
        # 开始结束时间
        start_date: str = req.start.strftime('%Y-%m-%d')
        end_date: str = req.end.strftime('%Y-%m-%d')

        # 添加参数
        req.trading_type = trading_type
        req.symbols = symbols
        req.intervals = intervals
        req.start_date = start_date
        req.end_date = end_date

        return req

    def _unzip_to_csv(self, path, req, output):
        """解压binanceK线zip"""
        # 指定待解压的文件夹路径
        folder_path = path

        # 获取文件夹中的所有文件
        files = os.listdir(folder_path)

        # 循环处理每个文件
        print("正在解压历史数据.")
        for file in files:

            file_path = os.path.join(folder_path, file)
            if file.endswith('.zip'):  # 只处理后缀名为 .zip 的文件
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        csv_path = folder_path + 'csv'
                        zip_ref.extractall(csv_path)  # 解压到csv目录下
                except Exception as e:
                    print(e)
                    output(f' {file}已损坏，解压文件失败！.')
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"{file} 删除成功, 正在尝试重新下载")
                        self.query_bar_history(req, output)  # 重新调用下载
                    else:
                        print(f"{file} 不存在")
        return csv_path
