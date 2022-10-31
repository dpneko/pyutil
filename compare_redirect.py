import requests
import pandas as pd
holders = pd.read_csv("output/export-jusdd-holder.csv")
addresses = holders['holder_address'].tolist()
for address in addresses:
    url = f"zapper/justlend/account?address={address}"
    abc = requests.get(f"https://grey-justlend.ablesdxd.link/{url}").json()
    grey = requests.get(f"https://greymining.ablesdxd.link/{url}").json()
    if abc != grey:
        print(f"https://grey-justlend.ablesdxd.link/{url}" + "\n"+ f"https://greymining.ablesdxd.link/{url}")
    url = f"/zapper/lend/account?account={address}"
    abc = requests.get(f"https://grey-justlend.ablesdxd.link/{url}").json()
    grey = requests.get(f"https://greymining.ablesdxd.link/{url}").json()
    if abc != grey:
        print(f"https://grey-justlend.ablesdxd.link/{url}" + "\n"+ f"https://greymining.ablesdxd.link/{url}")
        