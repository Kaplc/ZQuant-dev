import csv
import pytz
import os
from datetime import datetime
from pathlib import Path

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData
from vnpy.trader.database import database_manager

CHINA_TZ = pytz.timezone("Asia/Shanghai")


def load_data_from_csv(filename: str):
    """从CSV文件读取数据插入到数据库"""
    with open(filename) as f:
        reader = csv.DictReader(f)

        bars = []
        for d in reader:
            dt = datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M:%S")
            dt = CHINA_TZ.localize(dt)

            bar = BarData(
                symbol=d["symbol"],
                exchange=Exchange(d["exchange"]),
                interval=Interval.MINUTE,
                datetime=dt,
                open_price=float(d["open"]),
                high_price=float(d["high"]),
                low_price=float(d["low"]),
                close_price=float(d["close"]),
                volume=float(d["volume"]),
                open_interest=float(d["open_interest"]),
                gateway_name="DB"
            )
            bars.append(bar)

        database_manager.save_bar_data(bars)
        print(f"完成{filename}数据插入，起始点{bars[0].datetime}，结束点{bars[-1].datetime}，总数据量{len(bars)}")


if __name__ == "__main__":
    for root, dirs, files in os.walk(Path.cwd()):
        for filename in files:
            if filename.endswith("csv"):
                load_data_from_csv(filename)

# csv打开文件对象
        # 用来迭代CSV文件中的每一行，每一行都被转换为一个字典，
        # 其中字典的键是CSV文件中每一列的标题，而字典的值则是对应行中的数据。