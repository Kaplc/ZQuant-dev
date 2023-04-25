import csv
import os
import zipfile

from typing import List
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from core.trader.constant import Exchange, Interval
from core.trader.object import BarData


def import_data_from_csv(
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
    # 指定待加载csv的文件夹路径
    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)

    data: List[BarData] = []
    # 循环处理每个文件
    for file in files:
        file_path = os.path.join(folder_path, file)
        if file.endswith('.csv'):  # 只处理后缀名为 .csv 的文件
            with open(file_path, "rt") as f:
                buf: list = [line.replace("\0", "") for line in f]

            reader: csv.DictReader = csv.DictReader(buf, delimiter=",")


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

                data.append(bar)

                # do some statistics
                count += 1
                if not start:
                    start = bar.datetime


            # 导入数据库
            # self.database.save_bar_data(bars)

    end: datetime = bar.datetime
    return data


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
    return target_date


def req_converter(req):
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


def unzip_to_csv(path):
    """解压binanceK线zip"""
    # 指定待解压的文件夹路径
    folder_path = path

    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)

    # 循环处理每个文件
    for file in files:

        file_path = os.path.join(folder_path, file)
        if file.endswith('.zip'):  # 只处理后缀名为 .zip 的文件
            if file.split('.')[0] + '.csv' in files:
                continue

            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(folder_path)  # 解压到同一目录下
                print(f'解压文件 {file} 完成.')
            except:
                print(f'解压文件 {file} 失败！请重新点击下载.')
                pass


if __name__ == '__main__':
    unzip_to_csv()
