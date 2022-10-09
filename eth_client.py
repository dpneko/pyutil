import json
import requests
import pathos
import tqdm
import os
from web3 import Web3, HTTPProvider

bsc = "https://skilled-spring-patron.bsc.discover.quiknode.pro/3abc1b482d5250918ec09ea802ad40eed42c165f/"
eth = "https://mainnet.infura.io/v3/5f7b1e325e3d46cb8867a7b496365dea"

def get_logs(address, topics, fromBlock, toBlock):
    param = {
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [
            {
                "topics": topics,
                "address": address,
                # "blockhash": '0x9d1f6c5b7ad1a423a594a046387286abf97e82b8bcf9d69bc2368e40a44996f4'
                "fromBlock": hex(fromBlock),
                "toBlock": hex(toBlock)
            }
        ],
        "id": 1,
    }
    return requests.post(bsc, json=param).json()['result']

def get_pancake_user():
    if os.path.exists("pancake_user.json"):
        with open("pancake_user.json") as f:
            users = json.load(f)
            return users

    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ProcessPool(cores)

    users = {}
    fromBlock = 17050265
    toBlock = 21150960
    def func(start):
        address = "0x45c54210128a065de780C4B0Df3d16664f7f859e"
        topics = ["0x2b943276e5d747f6f7dd46d3b880d8874cb8d6b9b88ca1903990a2738e7dc7a1"] # lock
        users = {}
        logs = get_logs(address, topics, start, start+5000)
        for log in logs:
            user = log['topics'][1]
            lockedAmount = int(log['data'][2 : (2+64)], 16)
            lockedDuration = int(log['data'][(2+64*2) : (2+64*3)], 16)//86400
            users[user] = (lockedAmount, lockedDuration)
        return users


    for ret in tqdm.tqdm(pool.map(func, list(range(fromBlock, toBlock, 5000)))):
        # print(ret)
        users.update(ret)
    with open("pancake_user.json", 'w') as f:
        json.dump(users, f, indent=1)
    return users

if __name__ == '__main__':
    get_pancake_user()
    