import requests
import json
import pathos
import tqdm


def func(item):
    rtn = requests.get(f"https://labc.ablesdxd.link/sunProject/tronbullish?pool=TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP,TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd,TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA,TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno,TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv,TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT,TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts,TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt,TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV,TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE,TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e,TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy,TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R,TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto,TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS&addr={item['address']}").json()
    sum = 0
    for k,v in rtn['data'].items():
        new = float(v['JSTNEW']['gainNew'])
        if new != 0:
            sum += new
    if sum != 0:
        print(f"{item['address']}: {sum}")
        return {item['address']:sum}
    else:
        return {}


if __name__ == '__main__':
    cores = pathos.multiprocessing.cpu_count()
    pool = pathos.pools.ProcessPool(cores)
    with open("address.json") as f:
        addresses = json.load(f)
    remain = {}
    with open("print.txt", 'w+') as f:
        for ret in tqdm.tqdm(pool.map(func, addresses), total=len(addresses)):
            remain.update(ret)
            if len(ret) > 0:
                f.write(f"{ret}\n")
    with open("remain.json", 'w') as f:
        json.dump(remain, f, indent = 2)
    print(sum(remain.values()))