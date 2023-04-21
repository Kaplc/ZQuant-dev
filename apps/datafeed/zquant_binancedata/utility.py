import os
import zipfile
from datetime import datetime


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


def unzip_to_csv():
    """解压binanceK线zip"""
    # 指定待解压的文件夹路径
    folder_path = '/path/to/zip/files/'

    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)

    # 循环处理每个文件
    for file in files:
        file_path = os.path.join(folder_path, file)
        if file.endswith('.zip'):  # 只处理后缀名为 .zip 的文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)  # 解压到同一目录下
            print(f'解压文件 {file} 完成.')


if __name__ == '__main__':
    unzip_to_csv()
