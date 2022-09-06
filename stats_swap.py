from functools import reduce
from io import StringIO
from operator import xor
import time
import pandas as pd
import requests
from os.path import exists
from datetime import datetime


def stats_sunio_vol(start, end):
    csv = requests.get(
        f"http://3.128.125.155:10088/ssp_day_data/csv?item=swap_vol&start={start}&end={end}"
    ).text
    df = pd.read_csv(StringIO(csv), sep=",", index_col="Date")

    def get_sum(pair):
        return (
            df[filter(lambda x: x.endswith(pair), df.columns)].sum(axis=1).rename(pair)
        )

    sum = pd.DataFrame(
        map(
            get_sum,
            [
                "TUSD_to_USDT",
                "USDJ_to_TUSD",
                "USDT_to_TUSD",
                "USDC_to_USDT",
                "USDJ_to_USDT",
                "USDC_to_TUSD",
                "USDT_to_USDJ",
                "TUSD_to_USDC",
                "USDT_to_USDC",
                "USDC_to_USDJ",
                "USDJ_to_USDC",
                "TUSD_to_USDJ",
                "USDD_to_TUSD",
                "USDD_to_USDT",
                "USDT_to_USDD",
                "TUSD_to_USDD",
                "USDC_to_USDD",
                "USDD_to_USDC",
            ],
        )
    ).T
    return sum


def stats_sun_swap_v2_vol(start=None, end=None):
    start_ts = datetime.strptime(start, "%Y-%m-%d").timestamp()
    end_ts = datetime.strptime(end, "%Y-%m-%d").timestamp()
    csv_path = "transaction_swap.csv"
    if False:
        df = pd.read_csv(csv_path, index_col="id")
    else:
        if start is not None and end is not None:
            sql = f"select a.*, b.token0_address, b.token1_address, c.symbol as token0_symbol, d.symbol as token1_symbol from (select * from transaction_swap where block_create_time BETWEEN FROM_UNIXTIME({start_ts}) AND FROM_UNIXTIME({end_ts})) as a left join pair as b on a.pair_address = b.pair_address left join token as c on b.token0_address = c.token_address left join token as d on b.token1_address = d.token_address"
        else:
            sql = "select a.*, b.token0_address, b.token1_address, c.symbol as token0_symbol, d.symbol as token1_symbol from transaction_swap as a left join pair as b on a.pair_address = b.pair_address left join token as c on b.token0_address = c.token_address left join token as d on b.token1_address = d.token_address"
        _t1 = time.time()
        df = pd.read_sql_query(sql, "mysql+pymysql://v2_ro:etVvjMKaKTpCySCvtPVcU33#6@3.139.203.45:3306/defiswap-v2", index_col="id", dtype={"amount0In":float, "amount1In":float, "amount0Out":float, "amount1Out": float, "amount_usd": float})
        # print(time.time() - _t1)
        df.to_csv(csv_path)
    df.drop(columns=['txn_hash_index', 'create_time', 'update_time'], inplace=True)
    
    # def real_trans(txn_df):
    #     # txn_df = df.groupby("txn_hash").get_group("fff7371b68aeea471ad736cf514cea10a1c3fe6295e3cedea7be82680393635a")
    #     # 这个函数同样适用于txn_df只有一行的情况
    #     txn_df = txn_df.sort_values('log_index')
    #     first, last = txn_df.iloc[0], txn_df.iloc[-1] # python df的数据用iloc或者loc
    #     in_token = (first['amount0In'] and first['token0_address']) or (first['amount1In'] and first['token1_address'])
    #     out_token = (last['amount1Out'] and last['token1_address']) or (last['amount0Out'] and last['token0_address'])
    #     in_amount = first['amount0In'] + first['amount1In']
    #     out_amount = last['amount0Out'] + last['amount1Out']
    #     # if (first['amount_usd'] and not last['amount_usd']) or (not first['amount_usd'] and last['amount_usd']):
    #     #     print(f"{first['amount_usd']}, {last['amount_usd']}")
    #     real = pd.DataFrame({'txn_hash': first['txn_hash'], 'block_create_time': first['block_create_time'], 'from_address': first['from_address'], 'in_token': in_token, 'out_token': out_token, 'in_amount': in_amount, 'out_amount': out_amount, 'amount_usd': first['amount_usd'] or last['amount_usd']}, index=[first['txn_hash']])
    #     return real

    # real_swap = df.groupby("txn_hash").apply(real_trans)
    # real_swap.reset_index(drop=True, inplace=True)
    # return real_swap

    # 优化方法：
    df_groupby = df.groupby("txn_hash").agg(['first', 'last'])
    in_token = df_groupby[('token0_address', 'first')].where(df_groupby[("amount0In", "first")]>0, other=df_groupby[('token1_address', 'first')])
    out_token = df_groupby[('token1_address', 'last')].where(df_groupby[("amount1Out", "last")]>0, other=df_groupby[('token0_address', 'last')])
    in_token_symbol = df_groupby[('token0_symbol', 'first')].where(df_groupby[("amount0In", "first")]>0, other=df_groupby[('token1_symbol', 'first')])
    out_token_symbol = df_groupby[('token1_symbol', 'last')].where(df_groupby[("amount1Out", "last")]>0, other=df_groupby[('token0_symbol', 'last')])
    in_amount = df_groupby[('amount0In', 'first')] + df_groupby[('amount1In', 'first')]
    out_amount = df_groupby[('amount0Out', 'last')] + df_groupby[('amount1Out', 'last')]
    amount_usd = df_groupby[('amount_usd', 'first')].where(df_groupby[('amount_usd', 'first')]>0, other=df_groupby[('amount_usd', 'last')])
    real_swap = pd.DataFrame({
        'block_create_time': df_groupby[('block_create_time', 'first')],
        'from_address': df_groupby[('from_address', 'first')],
        'in_token': in_token,
        'out_token': out_token,
        'in_token_symbol': in_token_symbol,
        'out_token_symbol': out_token_symbol,
        'in_amount': in_amount,
        'out_amount': out_amount,
        'amount_usd': amount_usd
    }, index=df_groupby.index)

    return real_swap


if __name__ == '__main__':
    start = "2022-07-30"
    end = "2022-09-04"
    stats_sunio = stats_sunio_vol(start, end)
    sum_sunio = stats_sunio.sum().sort_values(ascending=False)
    sum_sunio.to_csv("sunio币对交易额.csv", header=None)

    stats_swapv2 = stats_sun_swap_v2_vol(start, end)
    sum_swapv2 = stats_swapv2.groupby(['in_token', 'out_token', 'in_token_symbol', 'out_token_symbol']).sum()['amount_usd'].sort_values(ascending=False)
    sum_swapv2.to_csv("swapv2交易额.csv", header=None)