import requests

jtokens = ["TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP", 
"TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS", 
"TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd", 
"TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA", 
"TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e", 
"TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv", 
"TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT", 
"TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts", 
"TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt", 
"TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV", 
"TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R", 
"TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy", 
"TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE", 
"TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto", 
"TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno", 
]

def total_reserve():
    sum_totalReserves_usd = 0
    for jtoken in jtokens:
        detail = requests.get(f"https://labc.ablesdxd.link/justlend/markets/jtokenDetails?jtokenAddr={jtoken}").json()['data']
        priceUSD = float(detail['priceUSD'])
        totalReserves = float(detail['totalReserves'])
        sum_totalReserves_usd += priceUSD * totalReserves
    print(sum_totalReserves_usd)
    return sum_totalReserves_usd

