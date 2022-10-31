import pandas as pd
import requests
from io import StringIO 
from binance import get_klines_iter

start = '2022-09-30'
end = '2022-10-09'
klines = get_klines_iter("USDCUSDT", '5m', start=1664467200000, end=1665244800000)
klines['time'] = pd.to_datetime(klines['Opentime'], unit='ms', utc=True).dt.tz_convert("Asia/Shanghai")
klines['time_str'] = klines['time'].dt.strftime("%Y-%m-%d %H:%M:%S")
print(klines)

reserve = requests.get(f"https://mining.ablesdxd.link/statistic/usdd/get_psm_gem_reserve_record?start={start}&end={end}")
df_reserve = pd.read_csv(StringIO(reserve.text), sep=",", header=0)

df_merge_usdc = klines[['time_str', 'Open']].merge(df_reserve[['时间', 'USDC余额', 'USDC价格']], left_on='time_str', right_on='时间')

print(df_merge_usdc)


transfer = pd.read_csv("output/TCVAudfvpT57VjHivn9KnghyE2a6i9two9_transfer.csv")
transfer = transfer.query("block >= 44341258")
addresses = set(transfer['from_address'].tolist()) | set(transfer['to_address'].tolist())
no_name_address = []
contract_address = {}
for address in addresses:
    account = requests.get(f"https://apilist.tronscanapi.com/api/accountv2?address={address}").json()
    if account['name'] == '' and 'addressTag' not in account:
        no_name_address.append(address)
    else:
        contract_address[address] = account['name'] or account['addressTag']
        print(f"{address}: {contract_address[address]}")
print(*no_name_address, sep='\n')
"""
TMn5WeW8a8KH9o8rBQux4RCgckD2SuMZmS: USDT GemJoin
TPxcmB9dQC3LHswCNEc4rJs1HFGb8McYjT: TUSD GemJoin
TRGTuMiDYAbztetdndYyMzYvtaRmucjz5q: USDC GemJoin
TMgSSHn8APyUVViqXxtveqFEB7mBBeGqNP: Vault
TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA: USDT PSM
TY2op6AKcEkFhv8hxNJj3FBUfjManxYLSe: TUSD PSM
TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA: USDC PSM
TYDzsYUEpvnYmQk4zGP9sWWcTEd2MiAtW6: FTX
TYvHkGZ5t3KV5RatJjJjRZJNqUogkhAy9K: FTX充币
TQrY8tryqsYVCYS3MFbtffiPp2ccyn4STm: Binance
TYASr5UV6HEcXatwdFQfmLVUqQQQMUxHLS: Binance-Hot
TV6MuMXfmLbBqPZvBHdwFsDnQeVfnmiuSi: Binance-Hot
TNXoiAJ3dct8Fjg4M9fkLFh9S2v9TXc32G: Binance-Hot
TAzsQ9Gx8eqFNFSKbeXrbi45CuVPHzA8wr: Binance-Hot
TJDENsfBJs4RFETt1X1W8wMDc8M5XnJhCe: Binance-Hot
TLtjEkPo3bvRc64cH1iHJnRs9pvKwzSszj: Binance充币
TPKsogvYSGCQXzKpNW7Hwsn974DtfbSszj: 广告地址
TJgNy1oPTYBAFAqYDD518CvB1godEuMZmS: 广告地址
TAqDmfrFJZBejcZiBaKJZFmLBG528zSszj: 广告地址
"""