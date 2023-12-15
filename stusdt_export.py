

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
    where action_type = 1 and timestamp >= 1699200000000
    order by timestamp asc ;
    """

    raw = pd.read_csv("stusdt_export" + sep + "deposit.csv", sep='\t',
                       names=['user_address','underlying_amount','timestamp','tx_id'])

    raw['day'] = raw['timestamp'].apply(format_day)
    raw['date'] = raw['timestamp'].apply(format_date)

    export = raw[['user_address', 'underlying_amount', 'tx_id', 'date', 'day']]
    # print(export)

    export.to_csv("stusdt_export" + sep + "deposit_export.csv", float_format='%g', index=False, header=False, sep='\t')

def export_unstake():
    """
    select user_address, withdraw_amount, withdraw_fee, request_timestamp, request_tx from stusdt_withdraw_log
    where request_timestamp >= 1699200000000
    order by request_timestamp asc ;
    """

    raw = pd.read_csv("stusdt_export" + sep + "unstake.csv", sep='\t',
                       names = ['user_address', 'withdraw_amount', 'withdraw_fee', 'request_timestamp', 'request_tx'])

    raw['day'] = raw['request_timestamp'].apply(format_day)
    raw['date'] = raw['request_timestamp'].apply(format_date)
    raw['without_fee'] = raw['withdraw_amount'] - raw['withdraw_fee']

    export = raw[['user_address', 'withdraw_amount', 'withdraw_fee', 'request_tx', 'date', 'day', 'without_fee']]
    # print(export)

    export.to_csv("stusdt_export" + sep + "unstake_export.csv", float_format='%g', index=False, header=False, sep='\t')

def export_claim():
    """
    select user_address, withdraw_amount, withdraw_fee, claim_timestamp, claim_tx from stusdt_withdraw_log
    where status in (3) and claim_timestamp >= 1699200000000
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

    export.to_csv("stusdt_export" + sep + "claim_export.csv", float_format='%g', index=False, header=False, sep='\t')

def to_unstake_contract():
    """
    https://tronscan.org/#/contract/TURYwFtG6gvpEyPSm55FyjJWpgQQ2rDm5e/transfers
    
    """
    pass

def top_stusdt_holder():
    """
    select user_address, share_amount from stusdt_account_info order by convert(share_amount, decimal(64,0)) desc limit 10;

select total_stUSDT, total_share from stusdt_status;
    """
    raw = """
TGkxzkDKyMeq2T7edKnyjZoFypyzjkkssq	1290082856425659591783525235
TDToUxX8sH4z6moQpK3ZLAN24eupu2ivA4	399458047165511402731855054
TYFCLifsFVvK1eitGSCDUR3DBSkBNJ5u9b	698664396326904092954765
TNuf5rB6pwmbPBA2t67FGsgXoRg9C7npNg	519689443101218731654932
TCvPmfRMQWqGFydy8Xph67BZ7meADRFyQ1	509212653894633030289809
TW8qFAkFT9DrbvkXy1TcrPWwFyBWGjPc57	399244782363524426442258
TRQhxYbRuv5juTuYZEn1mjwFybLXzFhiz8	316727443678698103893043
TJ753vBmGuv3RLKKJzpaYFF7xEMavMqj97	202552428279195008787066
TFKv3gB3LmXtkos4JHVNvtreUDS53c6AzL	198434174853914655512200
TJfZioPawaNqEN9ESgFDbbKZqW6SdghgXM	137027130250001344366566
    """
    total_stUSDT = '1711901236.271394878503389409'
    total_share = '1694540512388823680704991450'
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

def eth_log():
    """
     select user_address, underlying_amount, from_unixtime(timestamp/1000 + 3600*8), tx_id from stusdt_transfer_log
    where action_type = 1 and timestamp >= 1695484800000
    order by timestamp asc ;

    select user_address, withdraw_amount, withdraw_fee, from_unixtime(request_timestamp/1000+3600*8), request_tx from stusdt_withdraw_log
    where request_timestamp >= 1695484800000
    order by request_timestamp asc ;

     select user_address, withdraw_amount, withdraw_fee, from_unixtime(claim_timestamp/1000+3600*8), claim_tx from stusdt_withdraw_log
    where status in (3) and claim_timestamp >= 1695484800000
    order by claim_timestamp asc ;
    """
    pass

def check():
    """
    select sum(convert(underlying_amount, decimal(64, 18))) from stusdt_transfer_log
    where action_type = 1 and timestamp < 1695546000000;

    select sum(convert(rebase_amount, decimal(64, 18))) from stusdt_rebase_log where status = 3 and review_time < 1695546000000;

    select sum(convert(withdraw_amount, decimal(64, 18))) - sum(convert(withdraw_fee, decimal(64, 18))), sum(convert(withdraw_fee, decimal(64, 18))) from stusdt_withdraw_log
    where request_timestamp < 1695546000000;

    """
    pass
    
export_deposit()
export_unstake()
export_claim()

# top_stusdt_holder()
# daily_snapshot()