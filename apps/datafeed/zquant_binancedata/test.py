from sdk.binance_sdk.binance.download.download_kline import download_daily_klines

path = download_daily_klines(
    trading_type='um',
    symbols=['BTCUSDT'],
    num_symbols=None,
    intervals=['1m'],
    dates=None,
    start_date='2023-04-21',
    end_date='2023-04-23',
    folder='/home/kaplc/PycharmProjects/ZQuant_dev/apps/datafeed/zquant_binancedata',
    checksum=None
)
pass