# 加载内置模块
from time import sleep

# 加载三方模块
from vnpy.event import Event, EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_TICK, EVENT_CONTRACT
from vnpy.trader.object import TickData, ContractData, SubscribeRequest
from vnpy.trader.utility import load_json
from vnpy.gateway.ctp import CtpGateway


# 全局变量
main_engine: MainEngine = None


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


def process_tick_event(event: Event):
    """接收TICK推送，并进行对应处理"""
    tick: TickData = event.data
    print(tick.name, tick.symbol, tick.last_price, tick.datetime)


def process_contract_event(event: Event):
    """收到合约数据后立即订阅其行情"""
    # 获取合约对象，并创建对应的行情订阅请求
    contract: ContractData = event.data
    req = SubscribeRequest(contract.symbol, contract.exchange)
    
    # 获取主引擎全局对象，并调用订阅函数发送订阅
    global main_engine
    main_engine.subscribe(req, contract.gateway_name)


if __name__ == "__main__":
    run()
    