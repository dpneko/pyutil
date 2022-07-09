import json
import os
from path import Path
import pandas as pd
import requests
import tqdm
import pathos
from decimal import Decimal
from trongrid import getBlockNumByTimeStamp


def get_next_assign_frozen_reward(assign_json, week = 4):
    """获取下一次方法的奖励中历史冻结部分"""
    frozen_assign = json.loads(assign_json)
    total_next_assign = 0
    for d in frozen_assign:
        if int(d['l']) > int(d['s'])*week:
            total_next_assign += int(d['s'])*week
        else:
            total_next_assign += int(d['l'])
    return total_next_assign


def get_new_farmed(assign_json):
    """获取刚出完报表的这周的新挖的奖励"""
    for d in json.loads(assign_json):
        if round(float(d['l']) / float(d['s'])) == 23:
            return int(d['s'])*24
    return 0


def cal_detal_index(farm_speed, decimal, delta_block, total_balance):
    speed = Decimal(str(farm_speed))*pow(10, decimal)//Decimal(3600 * 24 // 3)
    if delta_block > 0:
        accrued = speed * Decimal(delta_block)
        return accrued * pow(10, 36) / Decimal(total_balance)
    return Decimal(0)


def get_prod_reward(dir):
    prodReward = Path(dir)
    dfs = []
    for file in filter(lambda f: f.basename().startswith('alltoken'), prodReward.files()):
        dfs.append(pd.read_csv(file, sep='\t', names=['symbol', 'address', 'type', 'farm_token_type', 'actual_reward', 'theory_reward', 'sub'], index_col=False))
    alltoken = pd.concat(dfs).reset_index(drop=True)
    alltoken['actual_reward'] = alltoken['actual_reward'].str.replace('actual_reward: ', '').astype('float64')
    alltoken['theory_reward'] = alltoken['theory_reward'].str.replace('theory_reward: ', '').astype('float64')
    alltoken['sub'] = alltoken['sub'].str.replace('sub: ', '').astype('float64')
    alltoken['percent'] = (alltoken['sub'] / (alltoken['theory_reward'] ) * 100).astype(str) + '%'
    return alltoken


def cal_farm_index(speeds, total_balances, decimal):
    """
    speeds格式: [[start_block, end_block, speed]]
    total_balances格式: [[block, total_balances]]  要求total_balances没有除精度
    a |000|-------|-----|
    b |0|---|---|----------|----
    """
    index = Decimal(0)
    index_array = [[speeds[0][0], 0]]
    for start_block, end_block, speed in speeds:
        if total_balances[-1][0] < end_block:
            total_balances.append([end_block, 0])
        for i in range(len(total_balances)-1):
            if total_balances[i][0] >= start_block and total_balances[i+1][0] <=  end_block:
                delta_block = total_balances[i+1][0] - total_balances[i][0]
            elif total_balances[i][0] <= start_block and total_balances[i+1][0] >=  end_block:
                delta_block = end_block - start_block
            elif total_balances[i][0] <= start_block and total_balances[i+1][0] >= start_block:
                delta_block = total_balances[i+1][0] - start_block
            elif total_balances[i][0] <= end_block and total_balances[i+1][0] >= end_block:
                delta_block = end_block - total_balances[i][0]
            else:
                continue
            index += cal_detal_index(speed, decimal, delta_block, total_balances[i][1])
            index_array.append([total_balances[i+1][0], index])
    return index, index_array


def cal_fix_apy_reward(apys, balances):
    """
    apys格式: [[start_block, end_block, apy]]
    balances格式: [[block, balance]]
    a |000|-------|-----|
    b |0|---|---|----------|----
    """
    sum_reward = 0
    for start_block, end_block, apy in apys:
        if balances[-1][0] < end_block:
            balances.append([end_block, 0])
        for i in range(len(balances)-1):
            if balances[i][0] >= start_block and balances[i+1][0] <=  end_block:
                delta_block = balances[i+1][0] - balances[i][0]
            elif balances[i][0] <= start_block and balances[i+1][0] >=  end_block:
                delta_block = end_block - start_block
            elif balances[i][0] <= start_block and balances[i+1][0] >= start_block:
                delta_block = balances[i+1][0] - start_block
            elif balances[i][0] <= end_block and balances[i+1][0] >= end_block:
                delta_block = end_block - balances[i][0]
            else:
                continue
            sum_reward += apy / 10512000 *  delta_block * balances[i][1]
    return sum_reward


def get_token_all_transfers(token, startTime="", endTime="", f_map=map):
    if os.path.exists(f"get_token_all_transfers_{token}.json"):
        with open(f"get_token_all_transfers_{token}.json", "r") as f:
            return json.load(f)
    url = 'https://apilist.tronscan.org/api/token_trc20/transfers'
    limit=20
    start=0
    confirm = 0
    ret = requests.get(f"{url}?limit={limit}&start={start}&contract_address={token}&start_timestamp={startTime}&end_timestamp={endTime}&confirm={confirm}")
    first = ret.json()
    total = first['total']
    token_transfers = first['token_transfers']
    def func(page):
        start=(page-1)*limit
        ret = requests.get(f"{url}?limit={limit}&start={start}&contract_address={token}&start_timestamp={startTime}&end_timestamp={endTime}&confirm={confirm}")
        return ret.json()['token_transfers']
    total_page = (total-limit-1)//limit + 2
    for ret in tqdm.tqdm(f_map(func, range(2, total_page+1)), total=total_page-1):
        token_transfers.extend(ret)
    token_transfers = sorted(token_transfers, key=lambda transfer: transfer['block'])
    with open(f"get_token_all_transfers_{token}.json", "w") as f:
        json.dump(token_transfers, f, indent=2)
    return token_transfers


def get_token_transfers(address, token, f_map=map):
    if os.path.exists(f"get_token_transfers_{token}_{address}.json"):
        with open(f"get_token_transfers_{token}_{address}.json", "r") as f:
            return json.load(f)
    url = "https://apilist.tronscan.org/api/token_trc20/transfers"
    limit=20
    start=0
    ret = requests.get(f"{url}?limit={limit}&start={start}&sort=timestamp&count=true&tokens={token}&relatedAddress={address}")
    first = ret.json()
    total = first['total']
    token_transfers = first['token_transfers']
    def func(page):
        start=(page-1)*limit
        ret = requests.get(f"{url}?limit={limit}&start={start}&sort=timestamp&count=true&tokens={token}&relatedAddress={address}")
        return ret.json()['token_transfers']
    total_page = (total-limit-1)//limit + 2
    for ret in tqdm.tqdm(f_map(func, range(2, total_page+1)), total=total_page-1):
        token_transfers.extend(ret)
    token_transfers = sorted(token_transfers, key=lambda transfer: transfer['block'])
    with open(f"get_token_transfers_{token}_{address}.json", "w") as f:
        json.dump(token_transfers, f, indent=2)
    return token_transfers


def get_token_balances(address, token, startTime=None, endTime=None, f_map=map):
    """
    返回的balances格式: [[block, balance]]
    """
    if address == token:
        token_transfers = get_token_all_transfers(token, endTime=endTime, f_map=f_map)
    else:
        token_transfers = get_token_transfers(address, token, f_map)
    balances = [[0, 0]]
    for transfer in token_transfers:
        if transfer['from_address'] == address:
            delta_balance = -int(transfer['quant'])
        elif transfer['to_address'] == address:
            delta_balance = int(transfer['quant'])
        else:
            continue
        if address == token: # 此时balance表示total supply
            delta_balance = -delta_balance
        if startTime is not None and transfer['block_ts'] <= startTime:
            balances[0] = [transfer['block'], balances[-1][1] + delta_balance]
        else:
            balances.append([transfer['block'], balances[-1][1] + delta_balance])
        if endTime is not None and transfer['block_ts'] >= endTime:
            break
    return balances


def get_fix_apy_reward():
    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ProcessPool(cores)

    balances = get_token_balances("TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS", "TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS", f_map=pool.imap)
    print(balances)
    apys = [[40601316, 40802667, 0.3]]
    print(f"usdd reward: {cal_fix_apy_reward(apys, balances)/1e10}")
    for i in range(len(balances)):
        if balances[i][0] >= apys[-1][1]:
            print(f"最后的balance: {balances[i-1][1]}")
            break
    if balances[-1][0] < apys[-1][1]:
        print(f"最后的balance: {balances[-1][1]}")


def get_deposit_index():
    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ProcessPool(cores)

    balances = get_token_balances("TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS", "TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS", startTime=1652356800000, endTime=1652961600000, f_map=pool.imap)
    print(f"balances:\n{balances[:5]}\n{balances[-5:]}")
    speeds = [[40601316, 40802667, 206643]]
    # speeds = [[40630084, 40745118, 100000], [40745118, 40802667, 80000]]
    for i in range(len(balances)):
        if balances[i][0] >= speeds[-1][1]:
            print(f"最后的balance: {balances[i-1][1]}")
            break
    if balances[-1][0] < speeds[-1][1]:
        print(f"最后的balance: {balances[-1][1]}")
    index, index_array = cal_farm_index(speeds, balances, 18)
    print(f"usdd挖jst 最后index: {index}")
    print(f"index:\n{index_array[:5]}\n{index_array[-5:]}")


def cal_predict_total_reward(speed, start_block, end_block):
    return speed / (86400//3) * (end_block - start_block)


if __name__ == '__main__':
    print(sum([cal_predict_total_reward(a,b,c) for a,b,c in [(50000, 41809095, 41921204),(90000, 41921204, 42007106)]]))
    print(463077430555555555542471/1e18)
    