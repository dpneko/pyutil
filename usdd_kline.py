import requests
import pandas as pd
from datetime import datetime
result = requests.get("https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id=19891&range=1M").json()
kline = [(datetime.fromtimestamp(int(k)).strftime("%Y-%m-%d %H:%M:%S"), v['v'][0]) for k,v in result['data']['points'].items()]
pd.DataFrame(kline, columns=['date', 'price']).to_csv("usdd_kline.csv")
