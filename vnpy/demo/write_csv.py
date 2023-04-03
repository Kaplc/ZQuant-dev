# 加载内置模块
from time import sleep
from csv import DictWriter
from typing import Dict, TextIO
from datetime import datetime

# 加载三方模块
from vnpy.event import Event, EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_TICK, EVENT_CONTRACT
from vnpy.trader.object import TickData, ContractData, SubscribeRequest
from vnpy.trader.utility import load_json, TRADER_DIR
from vnpy.gateway.ctp import CtpGateway


# 全局变量
main_engine: MainEngine = None
symbol_file_map: Dict[str, TextIO] = {}
symbol_writer_map: Dict[str, DictWriter] = {}

today = datetime.now().strftime("%Y%m%d")
csv_dir = TRADER_DIR.joinpath(today)
if not csv_dir.exists():
    csv_dir.mkdir()


def run():
    """程序主入口"""
    # 创建事件引擎
    event_engine = EventEngine()

    # 注册事件监听
    event_engine.register(EVENT_CONTRACT, process_contract_event)
    event_engine.register(EVENT_TICK, process_tick_event)

    # 初始化全局对象
    global main_engine
    main_engine = MainEngine(event_engine)

    # 添加并连接交易接口
    main_engine.add_gateway(CtpGateway)
    
    # 对于普通用户直接在这里写接口配置即可
    # setting = {
    #     "用户名": "",
    #     "密码": "",
    #     "经纪商代码": "9999",
    #     "交易服务器": "180.168.146.187:10130",
    #     "行情服务器": "180.168.146.187:10131",
    #     "产品名称": "simnow_client_test",
    #     "授权编码": "0000000000000000",
    #     "产品信息": ""
    # }
    
    # 为了避免泄露账号密码，我这里用了load_json
    setting = load_json("connect_ctp.json")

    main_engine.connect(setting, "CTP")

    # 启动无限循环，阻塞主线程避免退出
    while 1:
        # 但如果捕捉到用户主动按下Ctrl-C
        try:
            sleep(2)
        # 则中断循环并退出
        except KeyboardInterrupt:
            print("退出程序")
            break
    
    # 关闭主引擎中的所有模块、接口
    main_engine.close()

    # 保存所有的文件
    global symbol_file_map
    for f in symbol_file_map.values():
        f.close()


def process_tick_event(event: Event):
    """接收TICK推送，并进行对应处理"""
    tick: TickData = event.data
    print(tick.name, tick.symbol, tick.last_price, tick.datetime)
    
    # 将Tick对象转换为数据字典
    data = {
        "symbol": tick.symbol,
        "exchange": tick.exchange.value,
        "datetime": tick.datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "open_price": tick.open_price,
        "high_price": tick.high_price,
        "low_price": tick.low_price,
        "last_price": tick.last_price,
        "volume": tick.volume,
        "open_interest": tick.open_interest,
        "bid_price_1": tick.bid_price_1,
        "bid_volume_1": tick.bid_volume_1,
        "ask_price_1": tick.ask_price_1,
        "ask_volume_1": tick.ask_volume_1,
    }

    # 获取对应的writer对象，并写入
    global symbol_writer_map
    writer: DictWriter = symbol_writer_map[tick.symbol]
    writer.writerow(data)


def process_contract_event(event: Event):
    """收到合约数据后立即订阅其行情"""
    # 获取合约对象，并创建对应的行情订阅请求
    contract: ContractData = event.data
    req = SubscribeRequest(contract.symbol, contract.exchange)
    
    # 获取主引擎全局对象，并调用订阅函数发送订阅
    global main_engine
    main_engine.subscribe(req, contract.gateway_name)

    # 打开对应的CSV文件，并初始化DictWriter
    filename = f"{contract.symbol}.csv"

    global csv_dir
    filepath = csv_dir.joinpath(filename)

    # a为后续追加模式，万一中断后则重启继续写入
    # newline用于避免在windows上产生多余的一行
    f = open(filepath, mode="a", newline="")

    fieldnames = [
        "symbol",
        "exchange",
        "datetime",
        "open_price",
        "high_price",
        "low_price",
        "last_price",
        "volume",
        "open_interest",
        "bid_price_1",
        "bid_volume_1",
        "ask_price_1",
        "ask_volume_1",
    ]

    writer = DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    global symbol_file_map
    symbol_file_map[contract.symbol] = f

    global symbol_writer_map
    symbol_writer_map[contract.symbol] = writer


if __name__ == "__main__":
    run()
    