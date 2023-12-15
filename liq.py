import pandas as pd
import pytz
import json
from os.path import sep
from datetime import datetime
from io import StringIO

def to_ts(utc_str):
    utc = pytz.timezone('UTC')
    return int(utc.localize(datetime.strptime(utc_str, "%d/%m/%Y %H:%M")).timestamp())

def date_to_ts(utc_str):
    utc = pytz.timezone('UTC')
    return int(utc.localize(datetime.strptime(utc_str, '%Y-%m-%d %H:%M:%S')).timestamp())

liq = pd.read_csv("liq_export" + sep + "liq.csv", sep="\t", header=0)
liq['ts'] = liq['time'].apply(to_ts)
liq['left_ts'] = liq['ts'] - 3600 * 2
liq['right_ts'] = liq['ts'] + 3600 * 2
start = liq['ts'].min() - 3600 * 2
end = liq['ts'].max() + 3600 * 2
f"select tx_id, event_time, feed_token, feed_price from lend_price_record where event_time between from_unixtime({start}) and from_unixtime({end}) order by id asc;"

price_record = pd.read_csv("liq_export" + sep + "price_record.csv", sep="\t", names=['tx_id', 'event_time', 'feed_token', 'feed_price'])
price_record = price_record.drop_duplicates()
price_record['ts'] = price_record['event_time'].apply(date_to_ts)

ctoken_address_str = """
TRX	T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb	6
USDT	TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t	6
USDJ	TMwFHYXLJaRUPeW6421aqXL4ZEzPRFGkGT	18
SUNOLD	TKkeiboTkxXKJpbmVFbv4a8ov5rAfRDMf9	18
WIN	TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7	6
BTC	TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9	8
JST	TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9	18
WBTT	TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt	6
ETHOLD	THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF	18
TUSD	TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4	18
NFT	TFczxzPhnThNSqr5by8tvxsdCFRRz6cPNq	6
SUN	TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S	18
USDC	TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8	6
BTT	TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4	18
USDD	TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn	18
BUSD	TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH	18
sTRX	TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5	18
ETH	TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh	18
wstUSDT	TGkxzkDKyMeq2T7edKnyjZoFypyzjkkssq	18
"""
ctoken_address_df = pd.read_csv(StringIO(ctoken_address_str), sep="\t", names=['collateral_symbol', 'collateral_address', 'collateral_decimal'])
ctoken_names = {names[1]:names[0] for names in ctoken_address_df[['collateral_symbol', 'collateral_address']].values.tolist()}
ctoken_decimals = {names[1]:pow(10, names[0]) for names in ctoken_address_df[['collateral_decimal', 'collateral_address']].values.tolist()}
price_record['feed_price_decimal'] = price_record.apply(lambda raw: int(raw['feed_price']) * ctoken_decimals[raw['feed_token']] / 1e18 / 1e6 , axis=1)
price_record['symbol'] = price_record['feed_token'].replace(ctoken_names)
price_unstake = price_record.pivot(index=['event_time', 'ts'], columns='symbol', values='feed_price_decimal')


ts_ranges = liq.sort_values('ts')[['left_ts', 'right_ts']].values.tolist()
price_records_in_ranges = [price_unstake.query(f"ts >= {ts_range[0]} and ts < {ts_range[1]}") for ts_range in ts_ranges]
price_records_in_range = pd.concat(price_records_in_ranges)
price_records_in_range = price_records_in_range.reset_index().rename(columns={'event_time': '喂价时间'})
price_records_in_range.to_csv("liq_export" + sep + "price_records_in_range.csv", index=False, float_format="%.8f")


liq_all = pd.read_csv("liq_export" + sep + "liq_all.csv", sep="\t", names=
                      ['id', 'jtoken_address', 'user_address', 'action_type', 'associate_amount', 'note', 'blocknum', 'blocktimestamp', 'create_time', 'update_time', 'tx_id', 'ext'])
liq_with_ext = liq_all.drop(columns='ext').join(pd.json_normalize(liq_all['ext'].apply(json.loads)))
liq_clean = liq_with_ext[['blocknum', 'tx_id', 'liquidator', 'borrower', 'seizeJToken.address', 'borrowJToken.underlyingAddress', 'seizeJToken.exchangeRate', 'borrowJToken.exchangeRate']]
liq_clean['seizeAmount'] = liq_clean['seizeAmount'].astype(float)
liq_clean['repayAmount'] = liq_clean['repayAmount'].astype(float)
# liq_clean[['blocknum', 'liquidator', 'borrower', 'seizeJToken.address', 'borrowJToken.underlyingAddress']].drop_duplicates()
liq_merge = pd.merge(liq, liq_clean, how="left"
         , left_on=['blockHeight', 'borrower', 'liquidator', 'seizeJToken', 'repayToken']
         , right_on=['blocknum', 'borrower', 'liquidator', 'seizeJToken.address', 'borrowJToken.underlyingAddress'])
liq_merge.drop(columns=['left_ts', 'right_ts'], inplace=True)
liq_merge.drop_duplicates(inplace=True)
liq_merge.to_csv("liq_export" + sep + "liq_merge.csv", index=False)
# 
# liq_clean.query("blocktimestamp >= 1676995200000")