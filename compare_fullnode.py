import requests

if __name__ == '__main__':
    url = "/wallet/GetNowBlock".lower()
    domains = {
        "pubsun-event001": "http://47.90.206.231:8090",
        "pubsun-Solidity001": "http://47.252.15.247:8090",
        "sun.tronex.io": "https://sun.tronex.io"
    }

    results = {name: requests.get(domain+url).json() for name, domain in domains.items()}

    distinct = list()
    for name, result in results.items():
        if result not in distinct:
            distinct.append(result)
            print(f"----- Not equal, name:{name} -----")
            print(result)
