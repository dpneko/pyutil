import pandas as pd
import requests

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

def get_depth(symbol, limit=500):
    url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={limit}'
    result = requests.get(url).json()
    bids = [(float(item[0]), float(item[1])) for item in result['bids']]
    asks = [(float(item[0]), float(item[1])) for item in result['asks']]
    price = (bids[0][0] + asks[0][0]) / 2 if len(bids) > 0 and len(asks) > 0 else 0
    return price, bids, asks

# bids: 买价, [[价格, 挂单量], ...]，按照价格从高到低排序
# asks: 卖价, [[价格, 挂单量], ...]，按照价格从低到高排序
def cal_2per_vol(price, bids, asks):
    if not price:
        raise Exception("没有价格")
    up_2per_price = price * 1.02
    down_2per_price = price * 0.98
    up_2per_vol = 0
    down_2per_vol = 0
    for bid in bids:
        if bid[0] <= down_2per_price:
            break
        down_2per_vol += bid[1] * bid[0]
    for ask in asks:
        if ask[0] <= up_2per_price:
            break
        up_2per_vol += ask[1] * ask[0]
    return down_2per_vol, up_2per_vol

if __name__ == "__main__":
    tokens = ["BTTC", "JST", "SUN", "TRX", "TUSD", "USDC", "WIN", "AAVE", "AXS", "BUSD", "COMP", "CRV", "ETH", "FTM", "GRT", "KNC", "LINK", "MATIC", "QNT", "SHIB", "SUSHI", "UNI", "ADA", "ALPACA", "AUTO", "AVAX", "BAKE", "BCH", "BNB", "BTC", "BURGER", "CAKE", "DOT", "FOR", "LTC", "REEF", "TWT", "XRP", "XVS"]
    for token in tokens:
        exchange = token + "USDT"
        price, bids, asks = get_depth(exchange)
        if not price:
            print(f"{token}, 没有深度数据")
            continue
        down_2per_vol, up_2per_vol = cal_2per_vol(price, bids, asks)
        depth = (down_2per_vol + up_2per_vol) / 2
        print(f"{token}, {depth}")