

import pandas as pd
import datetime
from decimal import Decimal
from io import StringIO
import requests
import wallet
from os.path import sep

def format_day(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp/1000)
    return date.strftime("%d %B %Y")

def format_date(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp/1000)
    return date.strftime("%d/%m/%Y %H:%M")


def export_deposit():
    """
    select user_address, underlying_amount, timestamp, tx_id from stusdt_transfer_log
    where action_type = 1 and timestamp >= 1690819200000
    order by timestamp asc ;
    """

    raw = pd.read_csv("stusdt_export" + sep + "deposit.csv", sep='\t',
                       names=['user_address','underlying_amount','timestamp','tx_id'])

    raw['day'] = raw['timestamp'].apply(format_day)
    raw['date'] = raw['timestamp'].apply(format_date)

    export = raw[['user_address', 'underlying_amount', 'tx_id', 'date', 'day']]
    # print(export)

    export.to_csv("stusdt_export" + sep + "deposit_export.csv", float_format='%g', index=False)

def export_unstake():
    """
    select user_address, withdraw_amount, withdraw_fee, request_timestamp, request_tx from stusdt_withdraw_log
    where status in (0,1,2,3) and request_timestamp >= 1690819200000
    order by request_timestamp asc ;
    """

    raw = pd.read_csv("stusdt_export" + sep + "unstake.csv", sep='\t',
                       names = ['user_address', 'withdraw_amount', 'withdraw_fee', 'request_timestamp', 'request_tx'])

    raw['day'] = raw['request_timestamp'].apply(format_day)
    raw['date'] = raw['request_timestamp'].apply(format_date)
    raw['without_fee'] = raw['withdraw_amount'] - raw['withdraw_fee']

    export = raw[['user_address', 'withdraw_amount', 'withdraw_fee', 'request_tx', 'date', 'day', 'without_fee']]
    # print(export)

    export.to_csv("stusdt_export" + sep + "unstake_export.csv", float_format='%g', index=False)

def export_claim():
    """
    select user_address, withdraw_amount, withdraw_fee, claim_timestamp, claim_tx from stusdt_withdraw_log
    where status in (3) and claim_timestamp >= 1690819200000
    order by claim_timestamp asc ;
    """

    raw = pd.read_csv("stusdt_export" + sep + "claim.csv", sep='\t',
                      names=['user_address', 'withdraw_amount', 'withdraw_fee', 'claim_timestamp', 'claim_tx'])

    raw['day'] = raw['claim_timestamp'].apply(format_day)
    raw['date'] = raw['claim_timestamp'].apply(format_date)
    raw['without_fee'] = raw['withdraw_amount'] - raw['withdraw_fee']
    raw['status'] = '已提取'

    export = raw[['user_address', 'withdraw_amount', 'withdraw_fee', 'claim_tx', 'status','date', 'day', 'without_fee']]
    # print(export)

    export.to_csv("stusdt_export" + sep + "claim_export.csv", float_format='%g', index=False)


def top_stusdt_holder(total_stUSDT: str, total_share: str):
    """
    select user_address, share_amount from stusdt_account_info order by convert(share_amount, decimal(64,0)) desc limit 10;

select total_stUSDT, total_share from stusdt_status;
    """
    raw = """
0x176f3dab24a159341c0509bb36b833e7fdd0a132	48334620180842855429149032
0x9fcc67d7db763787bb1c7f3bc7f34d3c548c19fe	20000000000000000000000000
0xf85711780237b09bd243ab886bf39fec03b1b01c	246538339376324411711793
0x65c83d96f4cef2b77f1a757f1e51ff47f3aa7b4c	2697120665476285618356
0x946e2b9a3e9d05836f97f48dca9749b7252bd5c2	49887583095684344614
0x6ad5bfecbbf3fe11d4f2d7496ac8da06f734aac7	29975808235798643955
0x21547a10ec69f459aa5ffcb7109020a2b070ac6a	24957776572355694354
0x25ec98773d7b4ced4cafab96a2a1c0945f145e10	1000000000000000000
0x0e636d680b300214cf10e3343d0eef14f642c8a4	1000000000000000000
0x0c4f202dcc2b44d7a8bfe5a2443d4a3cac89271a	999499500000000000
    """
    account = pd.read_csv(StringIO(raw), sep='\t', names=['user_address', 'share_amount'], dtype={'share_amount': str})
    exchange = Decimal(total_stUSDT) / Decimal(total_share)
    account['stusdt_amount'] = (account['share_amount'].apply(Decimal) * exchange).astype(str)
    # account['percentage'] = account['stusdt_amount'].apply(Decimal) / Decimal(total_stUSDT)
    account[['user_address', 'stusdt_amount']].to_csv("top_stusdt_holder.csv", float_format=".1%", index=False)

def daily_snapshot():
    dashboard = requests.get('https://api.stusdt.org/stusdt/dashboard').json()['data']
    stusdt_supply = dashboard['totalAmount']
    apy = dashboard['apy']
    staker = dashboard['totalStaker']
    balanceOfMinter = wallet.balanceOf("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "TVh1PF9xr4zC5uAqRcCbxF1By6ucp95G4i") / 1e6 # 0xe22D16a16d8a5A92241cF696C35c08eaa873728c
    balanceOfUnstaker = wallet.balanceOf("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "TURYwFtG6gvpEyPSm55FyjJWpgQQ2rDm5e") / 1e6 # 0x156269966404Ca72F6721c3228676c56412c058c
    balanceOfMinterTusd = wallet.balanceOf("TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4", "TLT4iNRdYn9avUepRbUkPZxgRsZot1tm56") / 1e18
    
    print(f"stusdt_supply: {stusdt_supply}")
    print(f"apy: {apy}")
    print(f"staker: {staker}")
    print(f"balanceOfMinter: {balanceOfMinter}")
    print(f"balanceOfUnstaker: {balanceOfUnstaker}")
    print(f"balanceOfMinterTusd: {balanceOfMinterTusd}")
    """
    select cast(sum(convert(withdraw_amount, decimal(64,18)) - convert(withdraw_fee, decimal(64,18))) as char) as sumUsdtAmount from stusdt_withdraw_log where status <> 3
    """

def daily_volume():
    """
    select rebase_amount, create_time, old_total_underlying, apy from stusdt_rebase_log where status = 3;

    select sum(convert(underlying_amount, decimal(64,18))) as volumn, count(*) as count, count(distinct user_address) as count_user, DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(timestamp/1000), '+00:00', '+08:00'), '%Y-%m-%d') as day
    from stusdt_transfer_log where action_type=1 group by day;

    
    select sum(convert(withdraw_amount, decimal(64,18))) as volumn, count(*) as count, count(distinct user_address) as count_user, DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(request_timestamp/1000), '+00:00', '+08:00'), '%Y-%m-%d') as day
    from stusdt_withdraw_log group by day;
    
    select sum(convert(withdraw_amount, decimal(64,18))) as volumn, count(*) as count, count(distinct user_address) as count_user, DATE_FORMAT(CONVERT_TZ(FROM_UNIXTIME(claim_timestamp/1000), '+00:00', '+08:00'), '%Y-%m-%d') as day
    from stusdt_withdraw_log where status = 3 group by day;
    """
    pass
    
export_deposit()
export_unstake()
export_claim()

# top_stusdt_holder('68738510.873545500000000003','68583963461552059965162104')
# daily_snapshot()