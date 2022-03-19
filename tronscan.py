from functools import partial
import tqdm
import requests
import pathos
import json


def filter_method(transaction, method_id):
    return transaction['call_data'].startswith(method_id)


def filter_contract(transaction, contract):
    return contract == transaction['toAddress'] and 'data' in transaction['contractData']


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

    contract = 'TQx6CdLHqjwVmJ45ecRzodKfVumAsdoRXH' # USDCSWAP
    method_id = 'a6417ed6' # exchange_underlying(int128,int128,uint256,uint256)

    def f_filter(transaction):
        return transaction['toAddress'] in [
            "TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd",
            "TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA",
            "TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno",
            "TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv",
            "TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT",
            "TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts",
            "TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt",
            "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
            "TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV",
            "TMypaK8uiihyrQfJRAQGQHM9ZKiDdYx1AR",
            "TDB8Y2WMMeRivgxdsYniAyrGNWdCQisCvQ",
            "TWPcaMKwJAqHk7Ta3fYdHaHeBU2kES9TLH",
            "TGTN3wq6bDNMxvzYZrJqq6irJ9M1HWYAxX",
            "TWnTQ5grjn4nAJThs4JVGcyCYzzACd4ycq",
            "TLNBj6KNXMxcQutEPjgqotA6Wvr5mEVNd6",
            "TLCWfcYqmYZ6anvfq8AVPSiUuvRKwTyQx5",
            "TWKrCJCaeMzvixk8y1QLNbfwNVEjZz3CYF",
            "TL5uiT7s5kYwJJSdy4qxv2qbjiDZyhQp6i",
            "TNRd6HfeWosrZKe3J1eFbwXS57M71wH5K2",
            "TJwpin5Wv4Xrvcmsff4WWMiMhg5DGyWGSz",
            "TPX6nmRUqCQXGsAF9p64wLC4tgVE3JR9gR",
            "TV1nW5ay1JWaDrNg9xJpzp78W3CFiGwERd",
            "TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R",
            "TSNsDHNRmSyjhM42ET9fdW4P9B8nynVcrL",
            "TAt58Q8W7XPfnMzXmvJRxyeif3s5AuBxiC",
            "TUp1BWfAZidkNbWkoiCjJcf4ctE4PAR2Rg",
            "TVn5SqEfrKd2aeoQm1ZWioH458KM3Vb5iD",
            "TRpbsXviyETj1ngrgYSjEympGx8geA1sFW",
            "TPX5DGqK8ALCxFgWZompkGL5AUhycWL6xi",
            "TCBNm3ATvioeaLHLceRuA62usrTJS6KXWq",
            "TK2sKJP8Nr8xRPipbVckqnX6t9HBW6adBR",
            "TPDMF7GVzivR6heo3PzN85HZFLoGScd9Bb",
            "TKKMuQuMRrpcHYPoP55zmgkLwGgd1TMK2N",
            "TBTK7orRXZxv9BLR7J22RDY2CY4Pv2Fkwm",
            "TGCAcLQBdiA3ymsBs438EfLzD6n45DGVWW",
            "TJMmbVY4EMjCscRcPYSYbnzLy6VP6QegvH",
            "TLDheC4NNVH2SHwqEjxwqQUnKhxrgwsv88",
            "TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE",
            "TMbf5ZMK3UNthUDbQsYe8w8wQVJh4FwnpZ",
            "TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e",
            "TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy",
            "TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto",
        ]
    transactions = get_transaction_by_blocks(range(38950540, 38950580), f_filter=f_filter, f_map=pool.imap)
    with open("scan_result.json", "w") as f:
        json.dump(transactions, f, indent=6)
