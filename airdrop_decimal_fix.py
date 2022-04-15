import re

line ='''
airdrop_JST: 110059457758804433648484352
airdrop_NFT: 121223953907293952
airdrop_TRX: 22712149049280
airdrop_WBTT: 81241856595442
airdrop_WIN: 195053668421296
'''

decimal = {
    "SUN": 18,
    "TRX": 6,
    "JST": 18,
    "WBTT": 6,
    "WIN": 6,
    "BTCST": 17,
    "YFX": 18,
    "NFT": 6,
    "NEWSUN": 18,
}
regMatch = re.findall(r'^airdrop_(\w+): (\d+)', line, re.M)
if regMatch:
    for oneLine in regMatch:
        token = oneLine[0]
        amount = int(oneLine[1])
        real_amount = amount / (10**decimal[token])
        print(f"{token}\t{amount:32.0f}\t{real_amount:>32.18f}")
