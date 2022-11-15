import pandas as pd
import requests
from datetime import datetime
from datetime import timedelta
from io import StringIO
from functools import reduce

def top20(start, end):
    format = "%Y-%m-%d"
    start = datetime.strptime(start, format)
    end = datetime.strptime(end, format)
    day = end
    df_top_list = []
    while day >= start:
        top = requests.get(f"https://mining.ablesdxd.link/statistic/usdd/get_usdd_holder_top?day={day.strftime(format)}").text
        df_top = pd.read_csv(StringIO(top))
        df_top = df_top.query("链=='TRON'")[['地址', 'USDD数量']].set_axis(['Holder_address', day.strftime(format)], axis='columns').set_index('Holder_address')
        df_top_list.append(df_top)
        day -= timedelta(days=1)
    df = reduce(lambda a, b: a.merge(b, how='left', on='Holder_address'), df_top_list)
    df = df.reindex(columns=df.columns[::-1])
    df.to_csv(f"usdd_top_{start}_{end}.csv", float_format="%.0f")

if __name__ == '__main__':
    start = '2022-10-25'
    end = '2022-11-02'
    top20(start, end)