import os

from core.event import EventEngine
from core.trader.engine import MainEngine
from core.trader.ui import MainWindow, create_qapp

from apps.database.vnpy_datamanager import DataManagerApp
from apps.chartwizard import ChartWizardApp
from apps.vnpy_ctastrategy import CtaStrategyApp
from apps.vnpy_ctabacktester import CtaBacktesterApp


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
    main_engine.add_app(ChartWizardApp)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    # ui
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    qapp.exec()


if __name__ == "__main__":
    main()
