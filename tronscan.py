from functools import partial
import tqdm
import requests
import pathos
import json


def filter_method(transaction, method_id):
    return transaction['call_data'].startswith(method_id)


def filter_contract(transaction, contract):
    return contract == transaction['toAddress'] and 'data' in transaction['contractData']


def filter_from(transaction, from_addr):
    return transaction['ownAddress'] == from_addr

def filter_failed(transaction):
    return transaction['contractRet'] != "SUCCESS"

def get_all_transactions_by_contract(contract, f_filter=None, f_map=map):
    url = 'https://apiasia.tronscan.io:5566/api/contracts/transaction'
    limit=50
    start=0
    confirm = True
    ret = requests.get(f"{url}?sort=-timestamp&count=true&limit={limit}&start={start}&confirm={confirm}&contract={contract}")
    first = ret.json()
    total = first['total']
    transactions = list(filter(f_filter, first['data'])) if f_filter is not None else first['data']
    def func(page, start=start, limit=limit, url=url, confirm=confirm, contract=contract):
        start=(page-1)*limit
        ret = requests.get(f"{url}?sort=-timestamp&count=true&limit={limit}&start={start}&confirm={confirm}&contract={contract}")
        return list(filter(f_filter, ret.json()['data'])) if f_filter is not None else ret.json()['data']
    total_page = (total-limit-1)//limit + 2
    for ret in tqdm.tqdm(f_map(func, range(2, total_page+1)), total=total_page-1):
        transactions.extend(ret)
    return transactions


def get_transaction_by_blocks(block_nums, f_filter=None, f_map=map):
    def func(block_num):
        limit=50
        start=0
        ret = requests.get(f"https://apilist.tronscan.org/api/transaction?sort=timestamp&count=true&limit={limit}&start={start}&block={block_num}")
        first = ret.json()
        total = first['total']
        transactions = list(filter(f_filter, first['data'])) if f_filter is not None else first['data']
        for i in range((total-50-1)//50+1):
            start=(i+1)*limit
            ret = requests.get(f"https://apilist.tronscan.org/api/transaction?sort=timestamp&count=true&limit={limit}&start={start}&block={block_num}")
            transactions += list(filter(f_filter, ret.json()['data'])) if f_filter is not None else ret.json()['data']
        block_transaction = {}
        if len(transactions)>0:
            block_transaction[block_num]=transactions
        return block_transaction
    block_transaction_all = {}
    for ret in tqdm.tqdm(f_map(func, block_nums), total=len(block_nums)):
        block_transaction_all.update(ret)
    return block_transaction_all


if __name__ == '__main__':
    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ProcessPool(cores)

    contract = 'TQoiXqruw4SqYPwHAd6QiNZ3ES4rLsejAj' # USDCSWAP

    def f_filter(transaction):
        return transaction['call_data'] == 'c3f5de33' and filter_failed(transaction)

    transactions = get_all_transactions_by_contract(contract, f_filter=f_filter, f_map=pool.imap)
    user = [txn['ownAddress'] for txn in transactions]
    user = set(user)
    print("\n".join(user))
    print(f"Total: {len(user)}")
    pool.close()