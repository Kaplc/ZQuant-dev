import os

from core.event import EventEngine
from core.trader.engine import MainEngine
from core.trader.ui import MainWindow, create_qapp

from apps.database.vnpy_datamanager import DataManagerApp


def main():
    """"""
    # print(os.getcwd())
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    # 添加交易接口
    # main_engine.add_gateway(CtpGateway)

    # 添加子应用
    main_engine.add_app(DataManagerApp)

    # ui
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    qapp.exec()


if __name__ == "__main__":
    main()

