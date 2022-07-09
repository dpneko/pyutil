import re

line ='''
airdrop_JST: 66725837550061610072014848
airdrop_NFT: 13471867864062194
airdrop_TRX: 2524047938290
airdrop_WBTT: 9028574978994
airdrop_WIN: 21676716215556
airdrop_JST: 66725837550061610072014848
airdrop_NFT: 13471867864062194
airdrop_TRX: 2524047938290
airdrop_WBTT: 9028574978994
airdrop_WIN: 21676716215556


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
    "USDD": 18,
}
regMatch = re.findall(r'^airdrop_(\w+): (\d+)', line, re.M)
if regMatch:
    for oneLine in regMatch:
        token = oneLine[0]
        amount = int(oneLine[1])
        real_amount = amount / (10**decimal[token])
        print(f"{token}\t{amount:32.0f}\t{real_amount:>32.18f}")
    print("")
    for oneLine in regMatch:
        token = oneLine[0]
        amount = int(oneLine[1])
        real_amount = amount / (10**decimal[token])
        print(f"{token}\t{real_amount:>32.6f}")