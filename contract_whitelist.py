import requests

addresses = {

"TXA2WjFc5f86deJcZZCdbdpkpUTKTA3VDM": "energyRateModelContract",

"TSe1pcCnU1tLdg69JvbFmQirjKwTbxbPrG": "sTRXImpl",

"TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5": "sTRXProxy",

"TNoHbPuBQrVanVf9qxUsSvHdB2eDkeDAKD": "marketImpl",

"TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd": "marketProxy",
}

json_ori = {
    "contractAddress": "",
    "contractName": "",
    "projectId": 2,
    "remark": "",
    "accessToken": "tronsmart"
}

for address, name in addresses.items():
    json = json_ori.copy()
    json['contractAddress'] = address
    json['contractName'] = name
    resp = requests.post("https://mining.ablesdxd.link" + "/admin/upsertContractIntoWhiteList", json=json)
    print(f"{address} {name} {resp.text}")
