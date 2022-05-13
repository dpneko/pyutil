import json
import requests
from base58 import Base58
import SolTypeConvert


def gettransactioninfobyid(transaction_id):
    return requests.get("https://api.trongrid.io/wallet/gettransactioninfobyid?value="+transaction_id).json()
    

def triggerconstantcontract(contract_address:str, function_selector:str, parameter:str, host="mainnet")->str:
    contract_address = Base58(contract_address).decodeWithPrefix()
    params = {
        "contract_address":contract_address,
        "owner_address": '4128fb7be6c95a27217e0e0bff42ca50cd9461cc9f', # owner address 可以是任意地址
        "function_selector":function_selector,
        "parameter":parameter
        }
    ret = requests.post(url = "https://api.trongrid.io/wallet/triggerconstantcontract", json=params, headers={"Content-Type":"application/json"}).json()
    if "constant_result" in ret and len(ret["constant_result"][0]) != 0:
        return ret["constant_result"][0]
    else:
        print(params)
        print(ret)
        return None


def balanceOf(token, user):
    # 参数是base58check encode
    user = Base58(user).decodeWithPrefix()
    ret = triggerconstantcontract(token, "balanceOf(address)", "0000000000000000000000"+user)
    return int(ret, base=16)


def locked(user, vesun):
    # 参数是base58check encode
    rst = triggerconstantcontract(
        vesun,
        "locked(address)",
        SolTypeConvert.address_to_bytes32(user)
    )
    if rst is None or len(rst) != 128:
        return None
    # 返回值格式：
    # amount: 00000000000000000000000000000000000000000000060e2590145962fc0000
    # end:    0000000000000000000000000000000000000000000000000000000064125c00
    amount = SolTypeConvert.getInt(rst, 0)
    end = SolTypeConvert.getInt(rst, 1)
    return user, amount, end


def decimals(token):
    ret = triggerconstantcontract(token, "decimals()", "")
    return int(ret, base=16)
