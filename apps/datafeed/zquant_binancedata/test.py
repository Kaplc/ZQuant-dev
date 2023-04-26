import csv
from typing import List
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData
# from .utility import csv_time_converter
from sdk.binance_sdk.binance.download.download_kline import download_daily_klines

def parse_file_name(file_name):
    """以日期时间排序key"""
    # 获取日期部分，并解析为日期时间对象
    dt_str = file_name.split("-")[2, 3, 4]  # .split(".")[0]
    dt = datetime.strptime(dt_str, "%Y-%m-%d")
    return dt

def csv_time_converter(sum_second):
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
    # 输出年、月、日
    return target_date


def import_data_from_csv(
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
) -> List[BarData]:
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
            dt = csv_time_converter(item[datetime_head])  # datetime转换
            # dt: datetime = datetime.strptime(item[datetime_head], datetime_format)
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

    return bars


if __name__ == '__main__':
    # csv_time_converter()
    parse_file_name()
