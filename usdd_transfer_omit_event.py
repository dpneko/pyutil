from decimal import Decimal
from io import StringIO
import pandas as pd
import requests


# select from_unixtime((block_time div 86400000) * 86400), count(*) from usdd_transfer 
# where chain = 0 group by from_unixtime((block_time div 86400000) * 86400) order by from_unixtime((block_time div 86400000) * 86400);
df_usdd_transfer_count = pd.read_csv("output/usdd_transfer_count.csv", names=['day', 'count'], sep="\t")
analysis = requests.get("https://apilist.tronscanapi.com/api/token/analysis?token=TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn&start_day=2018-01-01&end_day=2022-10-14").json()
analysis_transfer_count = [(item['day']+" 00:00:00", item['transfer_count']) for item in analysis['data']]
df_analysis_transfer_count = pd.DataFrame(analysis_transfer_count, columns=['day', 'count'])

compare = df_usdd_transfer_count.merge(df_analysis_transfer_count, on='day', suffixes=['_my', '_scan'])
print(compare.query("count_my != count_scan"))


token_trc20_holders = requests.get("https://apilist.tronscanapi.com/api/token_trc20/holders?sort=-balance&start=0&limit=20&contract_address=TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn").json()
usdd_holder = pd.DataFrame(token_trc20_holders['trc20_tokens'])
# usdd_holder['balance'] = usdd_holder['balance'].astype(str)
get_usdd_holder_top = requests.get("https://greymining.ablesdxd.link//statistic/usdd/get_usdd_holder_top").text
usdd_holder_top = pd.read_csv(StringIO(get_usdd_holder_top), converters={'USDD数量':Decimal})
usdd_holder_top['USDD数量'] = (usdd_holder_top['USDD数量']*Decimal("1e18")).apply(lambda x: f"{x:.0f}")
holder_top_10_compare = pd.concat([usdd_holder[['holder_address', 'balance']].iloc[0:10], usdd_holder_top.query("链=='TRON'")[['地址', 'USDD数量']].reset_index(drop=True)], axis=1, ignore_index=False)
holder_top_10_compare.query("holder_address != 地址 or balance != USDD数量")


df_usdd_transfer_0825 = pd.read_csv("output/usdd_transfer_0825.csv")
df_usdd_transfer_0825_mysql = pd.read_csv("output/usdd_transfer_0825_mysql.csv", sep="\t")
tronscan_value = df_usdd_transfer_0825.rename(columns={'transaction_id':'txn_hash', 'quant': 'value'}).set_index(['txn_hash', 'from_address', 'to_address'])['value']
mysql_value = df_usdd_transfer_0825_mysql.set_index(['txn_hash', 'from_address', 'to_address'])['value']
tronscan_value.index.difference(mysql_value.index)
mysql_value.index.difference(tronscan_value.index)


df_usdd_transfer_eth = pd.concat([pd.read_csv("output/export-token-0x0C10bF8FcB7Bf5412187A595ab97a3609160b5c6.csv"),
     pd.read_csv("output/export-token-0x0C10bF8FcB7Bf5412187A595ab97a3609160b5c6 (1).csv")])
df_usdd_transfer_eth_mysql = pd.read_csv("output/usdd_transfer_eth_mysql.csv", sep="\t")
scan_value = df_usdd_transfer_eth.rename(
    columns={'Txhash':'txn_hash', 'Quantity': 'value', 'From': 'from_address', 'To': 'to_address'}).set_index(
        ['txn_hash', 'from_address', 'to_address'])
mysql_value = df_usdd_transfer_eth_mysql.set_index(['txn_hash', 'from_address', 'to_address'])
scan_value.index.difference(mysql_value.index).to_frame().reset_index(drop=True)['txn_hash'].tolist()
scan_value.loc[scan_value.index.difference(mysql_value.index)].sort_values('UnixTimestamp').reset_index(drop=True)
mysql_value.index.difference(scan_value.index)

