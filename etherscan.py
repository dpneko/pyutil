import requests
import time

# last = time.time()
# while True:
#     if time.time() - last >= 1:
#         block = int(requests.get("https://api-goerli.etherscan.io/api?apikey=EF5B594AGKZU4ZE2ZZAS88JYZUC4HQI14D&module=proxy&action=eth_blockNumber").json()['result'], 16)
#         print(f"--------{block}-----------")
#         print(requests.get(f"https://api-goerli.etherscan.io/api?endblock={block}&address=0xd35cceead182dcee0f148ebac9447da2c4d449c4&apikey=EF5B594AGKZU4ZE2ZZAS88JYZUC4HQI14D&offset=&module=account&action=txlist&startblock={block}").json()['result'])
#         last = time.time()


last = time.time()
while True:
    if time.time() - last >= 12:
        block = int(requests.get("https://api.etherscan.io/api?apikey=EF5B594AGKZU4ZE2ZZAS88JYZUC4HQI14D&module=proxy&action=eth_blockNumber").json()['result'], 16)
        print(f"--------{block}-----------")
        print(requests.get(f"https://api.etherscan.io/api?endblock={16668764}&startblock={16668764}&address=0x5f927395213ee6b95de97bddcb1b2b1c0f16844f&apikey=EF5B594AGKZU4ZE2ZZAS88JYZUC4HQI14D&module=account&action=txlist").json()['result'])
        last = time.time()
