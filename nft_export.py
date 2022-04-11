# apenft空投数据导出
import pandas as pd
from sqlalchemy import create_engine
from base58 import Base58

pd.set_option('display.precision', 18)

engine = create_engine("mysql+pymysql://tron:123456@localhost:3306/balance_info_nft_20220310.sql")
balance_info_nft_0 = pd.read_sql_query("select account_address,is_contract,balance from balance_info_nft_0 where balance != 0 and is_contract=0 and account_address not in ('TLsV52sRDL79HXGGm9yzwKibb6BeruhUzy', 'TUsoN4SCEoQV28yNQPPNsopriZfxsrLWXJ', 'T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb') order by ROUND(balance) desc limit 100000",
 engine, coerce_float=False)
balance_info_nft_0['balance'] = balance_info_nft_0['balance'].astype(float)
balance_info_nft_0.insert(0, 'base58', balance_info_nft_0['account_address'].map(lambda addr: Base58(addr).decodeWithPrefix()))

balance_info_nft_0.to_csv("nft_airdrop/nft_airdrop_20220310.txt", sep='\t', header=False, index=False, float_format='%.0f')


print(f"总量: {balance_info_nft_0['balance'].sum()/1e6:.6f}")
print(f"最少balance: {balance_info_nft_0['balance'].iloc[-1]:.0f}")
