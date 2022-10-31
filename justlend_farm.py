import requests
import pandas as pd
import json
import farm

boss = ["TCy2gn2skTzzRizqqKJRRq25NEHKcTz5cD","TPyjyZfsYaXStgz2NmAraF1uZcMtkgNan5","TDqMwZVTSPLTCZQC55Db3J69eXY7HLCmfs","TFsuFNs5vyjJ8iKUT5uvJUhjnx5VjFdWPy",
    "TGfWKtSDs96TrX1GwH3xsf5HxZhj1PPydv", "TUjx6w55Nx9G4GjjRNEB4e7w5BUH3WmJTZ", "TQwh1ZDBdqMKDtGWEeDdrRUUbtgaVL1Se2", "TSF2rqLdrrZG7PZkDxtvu6B2PTpofidMAX"]
# farm_stats = requests.get("https://grey-justlend.ablesdxd.link//data_platform/get_farm_stats").json()['data']
# farmAccountInfoListMap = {}
# for farm_info in farm_stats:
#     farmAccountInfoListMap[farm_info['collateralSymbol']] = farm_info.pop('farmAccountInfoList')
# df_farm_stats = pd.DataFrame(farm_stats)
# df_farm_stats.to_csv("output/justlend_farm.csv", index=False)

# for symbol,farmAccountInfoList in farmAccountInfoListMap.items():
#     df_farmAccountInfoList = pd.DataFrame(farmAccountInfoList).set_index('account')
#     print(f'{symbol}: {df_farmAccountInfoList.query(f"account in {boss}").sum().to_dict()}')
#    df_farmAccountInfoList.to_csv(f"output/justlend_farm_{symbol}.csv", index=False)


allaccounttoken = pd.concat([pd.read_csv("output/justlend_farm/allaccounttoken_1_USDD_44654299_45338996.txt", sep="\t",
    names=['jtoken', 'jtoken_address', 'type', 'farm_token_type', 'user', 'reward']),
    pd.read_csv("output/justlend_farm/allaccounttoken_4_USDD_44654299_45338881.txt", sep="\t",
    names=['jtoken', 'jtoken_address', 'type', 'farm_token_type', 'user', 'reward'])])
allaccounttoken['reward_float'] = allaccounttoken['reward'].astype('float') / 1e18
allaccounttoken = allaccounttoken.query("reward != '0'").sort_values(['jtoken', 'reward_float'], ascending=[True, False])
alltoken = farm.alltoken("output/justlend_farm/")
alltoken['actual_reward'] = alltoken['actual_reward'] / 1e18
boss_sum = allaccounttoken.query(f"user in {boss}").groupby("jtoken_address").sum()['reward_float']
merge = pd.merge(alltoken[['symbol', 'address', 'actual_reward']], boss_sum, left_on='address', right_on='jtoken_address', how='outer')
merge.to_csv("output/justlend_farm/boss_reward.csv", index=False, float_format="%.0f")

allaccounttoken.groupby('jtoken').head(100)[['jtoken', 'user', 'reward']].to_csv("output/justlend_farm/top_100.csv", index=False)
