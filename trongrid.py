import requests
import json
import subprocess
import os

nile = 'https://api.nileex.io'
trongrid = 'https://api.trongrid.io'

def getBlockByNum(block_num:int, host="mainnet"):
    if host == "nile":
        domain = nile
    else:
        domain = trongrid
    params = {'num': block_num}
    ret = requests.post(domain + "/walletsolidity/getblockbynum", data=json.dumps(params)).json()
    return ret if 'block_header' in ret else None


def getNowBlock(host="mainnet"):
    if host == "nile":
        domain = nile
    else:
        domain = trongrid
    ret = requests.post(domain + "/walletsolidity/getnowblock").json()
    return ret if 'block_header' in ret else None


def getBlockByLimitNext(start_num, end_num, host="mainnet"):
    """批量获取块，包含startNum，不包含endNum"""
    if host == "nile":
        domain = nile
    else:
        domain = trongrid
    if start_num > end_num:
        start_num, end_num = end_num, start_num
    params = {"startNum": start_num, "endNum": end_num}
    ret = requests.post(domain + "/walletsolidity/getblockbylimitnext", data=json.dumps(params)).json()
    return ret if 'block' in ret['block'] else []


def getBlockNumAndTimeStamp(block:dict):
    raw_data = block['block_header']['raw_data']
    return raw_data['number'], raw_data['timestamp']


def calBlockNumByTime(timestamp, ref_block_num, ref_timestamp):
    return (timestamp - ref_timestamp) // 3000 + ref_block_num


def getBlockNumByTimeStamp(timestamp:int, ref_block_num=None, ref_timestamp=None, host="mainnet"):
    """
    获取大于等于timeStamp的第一个块的块高
    timestamp是毫秒级时间戳
    """
    # 获取第一个参考块
    if ref_block_num is None or ref_timestamp is None:
        block = getNowBlock(host)
        if block is None:
            block = getBlockByNum(31183538, host)
            if block is None:
                return None
        ref_block_num, ref_timestamp = getBlockNumAndTimeStamp(block)
    if ref_timestamp <= timestamp:
        return calBlockNumByTime(timestamp, ref_block_num, ref_timestamp)
    # 从参考块开始查找，直到参考块高与预计块高相差10个以内
    while abs(ref_timestamp - timestamp) >= 30000:
        # 缩短要查找的块的范围直到10个块以内，以防出现连续丢块导致死循环
        find = getBlockByNum(calBlockNumByTime(timestamp, ref_block_num, ref_timestamp), host)
        jump = 0
        while find is None:
            jump -= 1
            find = getBlockByNum(calBlockNumByTime(timestamp, ref_block_num, ref_timestamp) + jump, host)
        ref_block_num, ref_timestamp = getBlockNumAndTimeStamp(find)

    # 一次性获取参考块到预计块高的所有块
    block_range = [] # 从小到大排列的块序列
    if ref_timestamp < timestamp:
        # 获取 [ref, 预估的块高+1] 的所有块
        blocks = getBlockByLimitNext(ref_block_num + 1, calBlockNumByTime(timestamp, ref_block_num, ref_timestamp) + 2, host)
        block_range = [getBlockNumAndTimeStamp(block) for block in blocks]
        block_range.insert(0, (ref_block_num, ref_timestamp)) # ref插入到列表开头
    elif ref_timestamp > timestamp:
        # 获取 [预估的块高-1, ref] 的所有块
        block_range = getBlockByLimitNext(calBlockNumByTime(timestamp, ref_block_num, ref_timestamp) - 1, ref_block_num, host)
        block_range.append((ref_block_num, ref_timestamp)) # ref插入到列表末尾
    else :
        return ref_block_num
    
    # 定位到目标块
    if timestamp < block_range[0][1]:
      # 目标时间戳小于blockRange最小的
        smallest_block_num, smallest_timestamp = block_range[0]
        find_block = smallest_block_num - 1
        while True:
            find = getBlockByNum(find_block, host)
            find_block -= 1
            if find is not None:
                find_block_num, find_timestamp = getBlockNumAndTimeStamp(find)
                if find_timestamp > timestamp:
                    smallest_block_num, smallest_timestamp = find_block_num, find_timestamp
                elif find_timestamp < timestamp:
                    return smallest_block_num
                else:
                    return find_block_num
    elif timestamp > block_range[-1][1]:
      # 目标时间戳大于blockRange最大的
      largest_block_num, largest_timestamp = block_range[-1]
      find_block = largest_block_num + 1
      while True:
        find = getBlockByNum(find_block, host)
        find_block += 1
        if find is not None:
            find_block_num, find_timestamp = getBlockNumAndTimeStamp(find)
            if find_timestamp < timestamp:
                largest_block_num, largest_timestamp = find_block_num, find_timestamp
            elif find_timestamp > timestamp:
                return largest_block_num
            else:
                return find_block_num
    else:
        i = 0
        while block_range[i][1] < timestamp:
            i += 1
        return block_range[i][0]


def getEventsByContractAndEvent(contract:str, event_name:str=None, min_block_timestamp=None, max_block_timestamp=None, host="mainnet"):
    if host == "nile":
        domain = nile
    else:
        domain = trongrid
    events = []
    url = domain + f"/v1/contracts/{contract}/events?limit=200"
    if event_name is not None:
        url = url + f"&event_name={event_name}"
    if min_block_timestamp is not None:
        url = url + f"&min_block_timestamp={min_block_timestamp}"
    if max_block_timestamp is not None:
        url = url + f"&max_block_timestamp={max_block_timestamp}"
    retry = False
    while True:
        result = requests.get(url).json()
        if not result['success']:
            print(url)
            continue
        if not retry and 'data' in result:
            events.extend(result['data'])
        elif not retry:
            print(url)
            print(result)
            continue
        if 'meta' in result and 'links' in result['meta'] and 'next' in result['meta']['links']:
            url = result['meta']['links']['next']
        else:
            if not retry:
                retry = True
                continue
            else:
                retry = False
                break
    return events


def gettransactionbyid(txn_id):
    url = f"https://api.trongrid.io/wallet/gettransactionbyid"
    payload = {"value": txn_id}
    result = requests.post(url, json=payload)
    if not result.ok:
        print(url)
        print(result.text)
        return None
    return result.json()


def gettransactioninfobyid(txn_id):
    url = f"https://api.trongrid.io/wallet/gettransactioninfobyid"
    payload = {"value": txn_id}
    result = requests.post(url, json=payload)
    if not result.ok:
        print(url)
        print(result.text)
        return None
    return result.json()


def getTransactionInfosByContract(contract:str, min_block_timestamp=None, max_block_timestamp=None, host="mainnet"):
    if host == "nile":
        domain = nile
    else:
        domain = trongrid
    events = []
    url = domain + f"/v1/contracts/{contract}/transactions?limit=50"
    if min_block_timestamp is not None:
        url = url + f"&min_block_timestamp={min_block_timestamp}"
    if max_block_timestamp is not None:
        url = url + f"&max_block_timestamp={max_block_timestamp}"
    retry = False
    while True:
        result = requests.get(url).json()
        if not result['success']:
            print(url)
            continue
        if not retry and 'data' in result:
            events.extend(result['data'])
        elif not retry:
            print(url)
            print(result)
            continue
        if 'meta' in result and 'links' in result['meta'] and 'next' in result['meta']['links']:
            url = result['meta']['links']['next']
        else:
            if not retry:
                retry = True
                continue
            else:
                retry = False
                break
    return events


def getCallDataFromTransactionInfo(transaction_info:dict):
    if 'raw_data' not in transaction_info:
        return None
    raw_data = transaction_info['raw_data']
    if 'contract' not in raw_data:
        return None
    contract = raw_data['contract']
    if not isinstance(contract, list):
        return None
    for c in contract:
        if 'type' not in c or c['type'] != 'TriggerSmartContract':
            continue
        if 'parameter' not in c:
            continue
        parameter = c['parameter']
        if 'value' not in parameter:
            continue
        value = parameter['value']
        if 'data' not in value:
            continue
        return value['data']
    return None


def decodeTransactionCallData(call_data_dict:dict):
    for txn_id, call_data in call_data_dict.items():
        if len(call_data.removeprefix("0x")) == 8:
            exitcode, output = subprocess.getstatusoutput("cast 4byte " + call_data)
        else:
            exitcode, output = subprocess.getstatusoutput("cast 4byte-decode " + call_data)
        if exitcode != 0:
            print(txn_id)
            print(call_data)
            print(output)
            continue
        lines = output.split(os.linesep)
        if "\"" in lines[0]:    
            method = lines[0].split("\"")[1]
        else:
            method = lines[0]
        params = lines[1:]
        call_data_dict[txn_id] = (method, params)
    return call_data_dict


def getTransactionsCallDataByContract(contract:str, min_block_timestamp=None, max_block_timestamp=None, host="mainnet"):
    transaction_info = getTransactionInfosByContract(contract, min_block_timestamp, max_block_timestamp, host)
    call_data_dict = {}
    for t in transaction_info:
        txn_id = t['txID']
        call_data = getCallDataFromTransactionInfo(t)
        if call_data is None:
            continue
        call_data_dict[txn_id] = call_data
    return decodeTransactionCallData(call_data_dict)


if __name__ == '__main__':
    # print(json.dumps(gettransactionbyid("308d1ab62bc7ed2c403e81918741c827a4d9f8e6c89075733c76357281a6bd9c"), indent=6))
    # print(json.dumps(getEventsByContractAndEvent("TP2JD7LfzXZU1L61ThHmLGi1n6sUJuUtK8"), indent=6))
    with open("output/transactions.json", "w") as f:
        json.dump(getTransactionsCallDataByContract("TP2JD7LfzXZU1L61ThHmLGi1n6sUJuUtK8"), f, indent=6)
