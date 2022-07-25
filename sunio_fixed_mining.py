import pathos
import json
import tqdm
import pandas as pd

from trongrid import getEventsByContractAndEvent
from base58 import Base58
from wallet import triggerconstantcontract


def export_fixed_mining(pool_address, fmap=map):
    events = getEventsByContractAndEvent(pool_address, "SnapShot")
    # with open(f"events_{pool_address}.json", "w") as f:
    #     json.dump(events, f, indent=6)
    users = [event['result']['user'] for event in events]
    users = set(users)
    users = [Base58(raw).encode() for raw in users]

    user_infos = {}
    def func(user:str, pool_address=pool_address):
        user_decode = Base58(user).decodeWithPrefix()
        user_info_raw = triggerconstantcontract(pool_address, "userInfo(address)", "0000000000000000000000"+user_decode)
        if user_info_raw is None:
            return {}
        balance_of_raw = triggerconstantcontract(pool_address, "balanceOf(address)", "0000000000000000000000"+user_decode)
        user_info = {}
        # user_info['user_info_raw'] = user_info_raw
        user_info['boostedBalance'] = int(user_info_raw[64*0 : 64*1], 16)
        user_info['rewardPerTokenPaid'] = int(user_info_raw[64*1 : 64*2], 16)
        user_info['rewards'] = int(user_info_raw[64*2 : 64*3], 16)
        user_info['prevRewards'] = int(user_info_raw[64*3 : 64*4], 16)
        user_info['lockStartTime'] = int(user_info_raw[64*4 : 64*5], 16)
        user_info['lockDuration'] = int(user_info_raw[64*5 : 64*6], 16)
        user_info['lastActionTime'] = int(user_info_raw[64*6 : 64*7], 16)
        user_info['balanceOf'] = int(balance_of_raw, 16)
        user_info['type'] = 'Fixed' if user_info['lockDuration'] != 0 else 'Flexible'
        user_info['boostRate'] = 0 if user_info['balanceOf'] == 0 else user_info['boostedBalance'] / user_info['balanceOf']

        return {user : user_info}

    for ret in tqdm.tqdm(fmap(func, users), total=len(users)):
        user_infos.update(ret)
    # with open(f"user_infos_{pool_address}.json", "w") as f:
    #     json.dump(user_infos, f, indent=6)
    
    df_user_infos = pd.DataFrame.from_dict(user_infos, orient='index')

    # df_user_infos = pd.read_csv("TMWFaKzrhhD7Zp9kY7Cd9iy8WRrA4UUEBq.csv", index_col=0)
    df_user_infos['lockEndTime'] = df_user_infos['lockStartTime'] + df_user_infos['lockDuration']
    df_user_infos['lockStartTime_str'] = pd.to_datetime(df_user_infos['lockStartTime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
    df_user_infos['lockEndTime_str'] = pd.to_datetime(df_user_infos['lockEndTime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai').dt.strftime('%Y-%m-%d %H:%M:%S')
    df_user_infos['lockDuration_day'] = df_user_infos['lockDuration'] // 86400

    df_user_infos.to_csv(pool_address+".csv")
    return df_user_infos


if __name__ == '__main__':
    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ProcessPool(cores)

    # pool_address = "TMWFaKzrhhD7Zp9kY7Cd9iy8WRrA4UUEBq" # 2pool
    # pool_address = "TEjGcD7Fb7KfEsJ2ouGCFUqqQqGjtvbmbu" # USDD-USDT Pool
    _2pool = export_fixed_mining("TMWFaKzrhhD7Zp9kY7Cd9iy8WRrA4UUEBq", pool.uimap)
    usdd_usdt_pool = export_fixed_mining("TEjGcD7Fb7KfEsJ2ouGCFUqqQqGjtvbmbu", pool.uimap)
