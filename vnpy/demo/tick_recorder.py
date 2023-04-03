# 加载内置模块
from time import sleep
from csv import DictWriter
from typing import Dict, TextIO
from datetime import datetime

# 加载三方模块
from vnpy.event import Event, EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_TICK, EVENT_CONTRACT, EVENT_TIMER
from vnpy.trader.object import TickData, ContractData, SubscribeRequest
from vnpy.trader.utility import load_json, TRADER_DIR
from vnpy.gateway.ctp import CtpGateway


class TickRecorder:
    """TICK行情录制插件"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        self.main_engine = main_engine
        self.event_engine = event_engine

        self.symbol_file_map: Dict[str, TextIO] = {}
        self.symbol_writer_map: Dict[str, DictWriter] = {}

        today = datetime.now().strftime("%Y%m%d")
        self.csv_dir = TRADER_DIR.joinpath(today)
        if not self.csv_dir.exists():
            self.csv_dir.mkdir()

        self.timer_count = 0

        self.register_event()

    def register_event(self):
        """向事件引擎注册监听"""
        self.event_engine.register(EVENT_CONTRACT, self.process_contract_event)
        self.event_engine.register(EVENT_TICK, self.process_tick_event)
        self.event_engine.register(EVENT_TIMER, self.process_timer_event)

    def process_tick_event(self, event: Event):
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
        writer: DictWriter = self.symbol_writer_map[tick.symbol]
        writer.writerow(data)

    def process_contract_event(self, event: Event):
        """收到合约数据后立即订阅其行情"""
        # 获取合约对象，并创建对应的行情订阅请求
        contract: ContractData = event.data
        req = SubscribeRequest(contract.symbol, contract.exchange)
        
        # 获取主引擎全局对象，并调用订阅函数发送订阅
        self.main_engine.subscribe(req, contract.gateway_name)

        # 打开对应的CSV文件，并初始化DictWriter
        filename = f"{contract.symbol}.csv"
        filepath = self.csv_dir.joinpath(filename)

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

        self.symbol_file_map[contract.symbol] = f
        self.symbol_writer_map[contract.symbol] = writer

    def process_timer_event(self, event: Event):
        """每60秒保存一次文件到硬盘"""
        self.timer_count += 1
        if self.timer_count < 60:
            return
        self.timer_count = 0

        self.flush_files()

    def flush_files(self):
        """保存文件到硬盘"""
        # flush的作用是清空文件缓冲区（写入硬盘）
        # 但同时并不会像close一样关闭文件
        for f in self.symbol_file_map.values():
            f.flush()

    def close(self):
        """关闭保存"""
        self.flush_files()


def run():
    """程序主入口"""
    # 创建引擎
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    # 初始化插件
    recorder = TickRecorder(main_engine, event_engine)

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
    
    # 关闭记录模块
    recorder.close()

    # 关闭主引擎中的所有模块、接口
    main_engine.close()


if __name__ == "__main__":
    run()
    