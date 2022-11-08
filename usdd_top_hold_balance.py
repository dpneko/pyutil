import pandas as pd
import requests
from datetime import datetime
from datetime import timedelta
from io import StringIO
from functools import reduce

def top20(startDay, endDay):
    format = "%Y-%m-%d"
    start = datetime.strptime(startDay, format)
    end = datetime.strptime(endDay, format)
    day = end
    df_top_list = []
    df_top_map = {}
    while day >= start:
        top = requests.get(f"https://mining.ablesdxd.link/statistic/usdd/get_usdd_holder_top?day={day.strftime(format)}").text
        df_top = pd.read_csv(StringIO(top), dtype={"排名": int})
        df_top = df_top.query("链=='TRON'").rename(columns={'地址':'Holder_address'}).set_index("Holder_address")
        df_top_map[day.strftime(format)] = df_top
        df_top = df_top['USDD数量'].rename(day.strftime(format))
        df_top_list.append(df_top)
        day -= timedelta(days=1)
    df = reduce(lambda a, b: pd.merge(a, b, how='left', on='Holder_address'), df_top_list)
    df = df.reindex(columns=df.columns[::-1])
    df = df.merge(df_top_map[startDay]['排名'].rename('起始排名'), how='left', on='Holder_address').merge(df_top_map[endDay]['排名'].rename('截止排名'), how='left', on='Holder_address')
    df['持仓量变化'] = df[endDay] - df[startDay]
    df['排名变化'] = df['起始排名'] - df['截止排名']
    df.to_csv(f"usdd_top_{startDay}_{endDay}.csv", float_format="%.0f")

if __name__ == '__main__':
    startDay = '2022-10-25'
    endDay = '2022-11-02'
    top20(startDay, endDay)