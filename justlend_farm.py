from turtle import pd
import requests
import pandas as pd
import json

farm_stats = requests.get("https://grey-justlend.ablesdxd.link//data_platform/get_farm_stats").json()['data']
farmAccountInfoListMap = {}
for farm_info in farm_stats:
    farmAccountInfoListMap[farm_info['collateralSymbol']] = farm_info.pop('farmAccountInfoList')
df_farm_stats = pd.DataFrame(farm_stats)
df_farm_stats.to_csv("output/justlend_farm.csv", index=False)
for symbol,farmAccountInfoList in farmAccountInfoListMap.items():
    df_farmAccountInfoList = pd.DataFrame(farmAccountInfoList)
    df_farmAccountInfoList.to_csv(f"output/justlend_farm_{symbol}.csv", index=False)
