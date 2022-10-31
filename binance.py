import pandas as pd

def get_klines_iter(symbol, interval, start, end, limit=1000):
    df = pd.DataFrame()
    startDate = start
    while startDate<end:
        url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}&startTime={startDate}&endTime={end}'
        df2 = pd.read_json(url)
        df2.columns = ['Opentime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quote asset volume', 'Number of trades','Taker by base', 'Taker buy quote', 'Ignore']
        df = pd.concat([df2, df], axis=0, ignore_index=True, keys=None)
        startDate = df.Opentime[-1]
    df.reset_index(drop=True, inplace=True)    
    return df