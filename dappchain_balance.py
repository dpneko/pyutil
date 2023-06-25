import requests
import pathos
import tqdm
from base58 import Base58


def getbalance(address, balance):
    decode = Base58(address).decodeWithPrefix()
    result = requests.get(f"https://sun.tronex.io/wallet/getaccount?address={decode}").json()

    if 'balance' not in result:
        real_balance = 0
    else:
        real_balance = result['balance']
    if balance != real_balance:
        print(f"balance not correct address: {address} ori balance: {balance} real balance: {real_balance}")
        return address, real_balance
    return address, balance


if __name__ == '__main__':
    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ThreadPool(cores)

    account_list = requests.get("https://dappchainapi.tronscan.org/api/account/list?sort=-balance&limit=50&start=0").json()['data']
    account_address_list = [(item['address'], item['balance']) for item in account_list]
    account_balances = list(tqdm.tqdm(pool.imap(lambda x: getbalance(*x), account_address_list), total=len(account_address_list)))

    account_balances = sorted(account_balances, key=lambda item: -item[1])
    print("\n".join([f"{addr}: {bal//1000000}" for addr, bal in account_balances[:10]]))
    pool.close()