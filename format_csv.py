import pandas as pd
df_user_infos = pd.read_csv("TMWFaKzrhhD7Zp9kY7Cd9iy8WRrA4UUEBq.csv", index_col=0)
df_user_infos['lockEndTime'] = df_user_infos['lockStartTime'] + df_user_infos['lockDuration']
df_user_infos['lockStartTime_str'] = pd.to_datetime(df_user_infos['lockStartTime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
df_user_infos['lockEndTime_str'] = pd.to_datetime(df_user_infos['lockEndTime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
df_user_infos['lockDuration_day'] = df_user_infos['lockDuration'] // 86400
df_user_infos.to_csv("2pool.csv")

df_user_infos = pd.read_csv("TEjGcD7Fb7KfEsJ2ouGCFUqqQqGjtvbmbu.csv", index_col=0)
df_user_infos['lockEndTime'] = df_user_infos['lockStartTime'] + df_user_infos['lockDuration']
df_user_infos['lockStartTime_str'] = pd.to_datetime(df_user_infos['lockStartTime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
df_user_infos['lockEndTime_str'] = pd.to_datetime(df_user_infos['lockEndTime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
df_user_infos['lockDuration_day'] = df_user_infos['lockDuration'] // 86400
df_user_infos.to_csv("usdd_usdt_pool.csv")