import requests
import time

domain = "https://api.etherscan.io/api"
# domain = "https://api-goerli.etherscan.io/api"
apikey = "EF5B594AGKZU4ZE2ZZAS88JYZUC4HQI14D"

def eth_blockNumber():
    return int(requests.get(f"{domain}?apikey={apikey}&module=proxy&action=eth_blockNumber").json()['result'], 16)

def txlist(address, startblock, endblock):
    return requests.get(f"{domain}?endblock={endblock}&startblock={startblock}&address={address}&apikey={apikey}&module=account&action=txlist").json()['result']

def eth_getTransactionByHash(txn_hash):
    url = f"{domain}?module=proxy&action=eth_getTransactionByHash&txhash={txn_hash}&apikey={apikey}"
    return requests.get().json(url)['result']

def eth_getBlockByNumber(block_num):
    return requests.get(f"{domain}?module=proxy&action=eth_getBlockByNumber&tag={hex(block_num)}&boolean=true&apikey={apikey}").json()['result']

def find_txlist_delay():
    txn_block = eth_blockNumber()
    block_info = eth_getBlockByNumber(txn_block)
    txn_time = int(block_info['timestamp'], 16)

    if not block_info['transactions']:
        print(f"there is no txn in block:{txn_block}")
        time.sleep(12)
        return find_txlist_delay()
    txn_info = block_info['transactions'][-1]
    txn_hash = txn_info['hash']
    address = txn_info['to']
    print(f"try to find txn:{txn_hash} to:{address} at block:{txn_block}")

    last = time.time()
    while True:
        if time.time() - last >= 1:
            block = eth_blockNumber()
            passed = time.time()-txn_time
            print(f"------current block: {block}, txn_block: {txn_block}, time passed: {passed}-----")
            txn_list = txlist(address, txn_block, block)
            if txn_hash in [item['hash'] for item in txn_list]:
                print(f"find txn_hash in {passed} seconds")
                return passed
            last = time.time()


if __name__ == "__main__":
    print(f"mean: {sum([find_txlist_delay() for i in range(10)]) / 10}")
