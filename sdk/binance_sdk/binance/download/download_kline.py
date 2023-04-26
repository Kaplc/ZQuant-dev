#!/usr/bin/env python

"""
  script to download klines.
  set the absolute path destination folder for STORE_DIRECTORY, and run

  e.g. STORE_DIRECTORY=/data/ ./download_kline.py
    下载K线
"""
import sys
from datetime import *
from typing import Callable

import pandas as pd
from sdk.binance_sdk.binance.download.enums import *
from sdk.binance_sdk.binance.download.utility import download_file, get_all_symbols, get_parser, \
    get_start_end_date_objects, convert_to_date_object, \
    get_path, get_dates


def download_monthly_klines(trading_type, symbols, num_symbols, intervals, years, months, start_date, end_date, folder,
                            checksum):
    """月K线"""
    current = 0
    date_range = None

    if start_date and end_date:
        date_range = start_date + " " + end_date

    if not start_date:
        start_date = START_DATE
    else:
        start_date = convert_to_date_object(start_date)

    if not end_date:
        end_date = END_DATE
    else:
        end_date = convert_to_date_object(end_date)

    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download monthly {} klines ".format(current + 1, num_symbols, symbol))
        for interval in intervals:
            for year in years:
                for month in months:
                    current_date = convert_to_date_object('{}-{}-01'.format(year, month))
                    if current_date >= start_date and current_date <= end_date:
                        path = get_path(trading_type, "klines", "monthly", symbol, interval)
                        file_name = "{}-{}-{}-{}.zip".format(symbol.upper(), interval, year, '{:02d}'.format(month))
                        download_file(path, file_name, date_range, folder)

                        if checksum == 1:
                            checksum_path = get_path(trading_type, "klines", "monthly", symbol, interval)
                            checksum_file_name = "{}-{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, year,
                                                                                   '{:02d}'.format(month))
                            download_file(checksum_path, checksum_file_name, date_range, folder)

        current += 1


def download_daily_klines(trading_type: str = None,
                          symbols: list = None,
                          num_symbols: int = None,
                          intervals: list = None,
                          dates: list = None,
                          start_date: str = None,
                          end_date: str = None,
                          folder=None,
                          checksum: int = None,) -> str:
    """
    下载日内K线
    :param trading_type: 'um'           - 交易类型 (spot/um(BTCUSDT)/cm（BTCUSD))
    :param symbols: ['BTCUSDT',...]     - 交易对符号 (ETHUSDT BTCUSDT BNBBUSD...)
    :param num_symbols: 224             - 交易对数量 get_all_symbols()获取
    :param intervals: ['1m',...]        - K线时间间隔 (1s,1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1mo)
    :param dates:                       - 指定日期范围列表
    :param start_date: '2020-01-30'     - 起始日期
    :param end_date: '2020-01-30'       - 结束日期
    :param folder:                      - 保存文件夹
    :param checksum: 0                  - 是否下载校验
    :return:None
    """
    # 获取num_symbols
    if not num_symbols:
        num_symbols = get_all_symbols(trading_type)
        if num_symbols == [0]:
            return None
    # 获取dates最早时间2020-1-1
    if not dates:
        dates = get_dates()

    current = 0
    date_range = None

    if start_date and end_date:
        date_range = start_date + " " + end_date

    if not start_date:
        start_date = START_DATE
    else:
        start_date = convert_to_date_object(start_date)  # 转换data对象

    if not end_date:
        end_date = END_DATE
    else:
        end_date = convert_to_date_object(end_date)

    # Get valid intervals for daily 获取时间间隔
    intervals = list(set(intervals) & set(DAILY_INTERVALS))
    print("Found {} symbols".format(num_symbols))

    for symbol in symbols:
        print("[{}/{}] - start download daily {} klines ".format(current + 1, num_symbols, symbol))
        for interval in intervals:
            for date in dates:
                current_date = convert_to_date_object(date)
                if current_date >= start_date and current_date <= end_date:
                    # 拼接url 'data/futures/um/daily/klines/BTCUSDT/1m/'
                    path = get_path(trading_type, "klines", "daily", symbol, interval)
                    file_name = "{}-{}-{}.zip".format(symbol.upper(), interval, date)
                    unzip_path = download_file(path, file_name, date_range, folder)  # 下载文件

                    if checksum == 1:
                        checksum_path = get_path(trading_type, "klines", "daily", symbol, interval)
                        checksum_file_name = "{}-{}-{}.zip.CHECKSUM".format(symbol.upper(), interval, date)
                        download_file(checksum_path, checksum_file_name, date_range, folder)

        current += 1

    return unzip_path  # 返回保存目录=解压地址


if __name__ == "__main__":
    parser = get_parser('klines')
    args = parser.parse_args(sys.argv[1:])

    if not args.symbols:  # 无交易对则，获取所有品种
        print("fetching all symbols from exchange")
        symbols = get_all_symbols(args.type)
        num_symbols = len(symbols)
    else:
        symbols = args.symbols
        num_symbols = len(symbols)

    if args.dates:
        dates = args.dates
    else:
        # 计算日期列表
        period = convert_to_date_object(datetime.today().strftime('%Y-%m-%d')) - convert_to_date_object(
            PERIOD_START_DATE)
        dates = pd.date_range(end=datetime.today(), periods=period.days + 1).to_pydatetime().tolist()
        dates = [date.strftime("%Y-%m-%d") for date in dates]
        if args.skip_monthly == 0:
            download_monthly_klines(args.type, symbols, num_symbols, args.intervals, args.years, args.months,
                                    args.startDate, args.endDate, args.folder, args.checksum)
    if args.skip_daily == 0:
        download_daily_klines(args.type, symbols, num_symbols, args.intervals, dates, args.startDate, args.endDate,
                              args.folder, args.checksum)
