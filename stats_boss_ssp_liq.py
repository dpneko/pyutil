from base58 import Base58
from wallet import *

if __name__ == '__main__':
    pools = {"old 2pool": "TAUGwRhmCP518Bm4VBqv7hDun9fg8kYjC4", "2pool": "TNTfaTpkdd4AQDeqr8SGG7tgdkdjdhbP5c", "3pool": "TKVsYedAY23WFchBniU7kcx1ybJnmRSbGt", "old3pool": "TKcEU8ekq2ZoFzLSGFYCUY6aocJBX9X31b", "oldUsdcPool": "TQx6CdLHqjwVmJ45ecRzodKfVumAsdoRXH"}
    gauges = {
        "TAUGwRhmCP518Bm4VBqv7hDun9fg8kYjC4": ["TBSRZYLZ2pguF3EqLz86Kt9hZ4eqKEQMSY"],
        "TNTfaTpkdd4AQDeqr8SGG7tgdkdjdhbP5c": ["TJmn1bjmNfE2F1sw2x6P224i8sFQj5mnbg", "TFpg63byqDwniXnyxVYpSzBfWGBwZExM9J"],
        "TKVsYedAY23WFchBniU7kcx1ybJnmRSbGt": ["THZgwb6LTg9LydbLw6gT4YMdu9y4nA5dnp"],
        "TKcEU8ekq2ZoFzLSGFYCUY6aocJBX9X31b": ["TCpu3GnK6PPZV9ama85mRP97YqRuVXdcSd"],
        "TQx6CdLHqjwVmJ45ecRzodKfVumAsdoRXH": ["TJ3Qnm9VhzJzhcxk49ZpHBRatD1bsD4xYq"],
        }
    bosses = ["TPyjyZfsYaXStgz2NmAraF1uZcMtkgNan5", "TScVwVTjqoqPEJ6atnvGCtErWnCyNbzmUL", "TCy2gn2skTzzRizqqKJRRq25NEHKcTz5cD", "TDqMwZVTSPLTCZQC55Db3J69eXY7HLCmfs", "TFsuFNs5vyjJ8iKUT5uvJUhjnx5VjFdWPy", "TGfWKtSDs96TrX1GwH3xsf5HxZhj1PPydv", "TUjx6w55Nx9G4GjjRNEB4e7w5BUH3WmJTZ", "TQwh1ZDBdqMKDtGWEeDdrRUUbtgaVL1Se2", "TSF2rqLdrrZG7PZkDxtvu6B2PTpofidMAX"]
    for name, pool in pools.items():
        if "TQx6CdLHqjwVmJ45ecRzodKfVumAsdoRXH" != pool:
            token = Base58(triggerconstantcontract(pool, "token()")).encode()
        else:
            token = Base58(triggerconstantcontract(pool, "lp_token()")).encode()
        # print(f"{name} {pool} {token}")
        balance = sum([balanceOf(token, user) for user in bosses])/1e18
        in_gauge = sum([balanceOf(gauge, user) for user in bosses for gauge in gauges[pool]])/1e18
        total = totalSupply(token)/1e18
        print(f"{name}: {balance} + {in_gauge} / total_supply = {balance+in_gauge} / {total}")
    