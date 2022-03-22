import requests
import json


def getBlockByNum(block_num:int):
    params = {'num': block_num}
    ret = requests.post(f"https://api.trongrid.io/walletsolidity/getblockbynum", data=json.dumps(params)).json()
    return ret if 'block_header' in ret else None


def getNowBlock():
    ret = requests.post(f"https://api.trongrid.io/walletsolidity/getnowblock").json()
    return ret if 'block_header' in ret else None


def getBlockByLimitNext(start_num, end_num):
    """批量获取块，包含startNum，不包含endNum"""
    if start_num > end_num:
        start_num, end_num = end_num, start_num
    params = {"startNum": start_num, "endNum": end_num}
    ret = requests.post(f"https://api.trongrid.io/walletsolidity/getblockbylimitnext", data=json.dumps(params)).json()
    return ret if 'block' in ret['block'] else []


def getBlockNumAndTimeStamp(block:dict):
    raw_data = block['block_header']['raw_data']
    return raw_data['number'], raw_data['timestamp']


def calBlockNumByTime(timestamp, ref_block_num, ref_timestamp):
    return (timestamp - ref_timestamp) // 3000 + ref_block_num


def getBlockNumByTimeStamp(timestamp:int, ref_block_num=None, ref_timestamp=None):
    """
    获取大于等于timeStamp的第一个块的块高
    timestamp是毫秒级时间戳
    """
    # 获取第一个参考块
    if ref_block_num is None or ref_timestamp is None:
        block = getNowBlock()
        if block is None:
            block = getBlockByNum(31183538)
            if block is None:
                return None
        ref_block_num, ref_timestamp = getBlockNumAndTimeStamp(block)
    if ref_timestamp <= timestamp:
        return calBlockNumByTime(timestamp, ref_block_num, ref_timestamp)
    # 从参考块开始查找，直到参考块高与预计块高相差10个以内
    while abs(ref_timestamp - timestamp) >= 30000:
        # 缩短要查找的块的范围直到10个块以内，以防出现连续丢块导致死循环
        find = getBlockByNum(calBlockNumByTime(timestamp, ref_block_num, ref_timestamp))
        jump = 0
        while find is None:
            jump -= 1
            find = getBlockByNum(calBlockNumByTime(timestamp, ref_block_num, ref_timestamp) + jump)
        ref_block_num, ref_timestamp = getBlockNumAndTimeStamp(find)

    # 一次性获取参考块到预计块高的所有块
    block_range = [] # 从小到大排列的块序列
    if ref_timestamp < timestamp:
        # 获取 [ref, 预估的块高+1] 的所有块
        blocks = getBlockByLimitNext(ref_block_num + 1, calBlockNumByTime(timestamp, ref_block_num, ref_timestamp) + 2)
        block_range = [getBlockNumAndTimeStamp(block) for block in blocks]
        block_range.insert(0, (ref_block_num, ref_timestamp)) # ref插入到列表开头
    elif ref_timestamp > timestamp:
        # 获取 [预估的块高-1, ref] 的所有块
        block_range = getBlockByLimitNext(calBlockNumByTime(timestamp, ref_block_num, ref_timestamp) - 1, ref_block_num)
        block_range.append((ref_block_num, ref_timestamp)) # ref插入到列表末尾
    else :
        return ref_block_num
    
    # 定位到目标块
    if timestamp < block_range[0][1]:
      # 目标时间戳小于blockRange最小的
        smallest_block_num, smallest_timestamp = block_range[0]
        find_block = smallest_block_num - 1
        while True:
            find = getBlockByNum(find_block)
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
        find = getBlockByNum(find_block)
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

