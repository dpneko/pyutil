

import pandas as pd
import datetime

def format_day(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp/1000)
    return date.strftime("%d %B %Y")

def format_date(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp/1000)
    return date.strftime("%d/%m/%y %H:%M")


def export_deposit():
    """
    select user_address, underlying_amount, timestamp, tx_id from stusdt_transfer_log
    where action_type = 1 and timestamp >= 1690819200000 and timestamp < 1691942400000
    order by timestamp asc ;
    """

    raw = pd.read_csv("deposit.csv", sep='\t')

    raw['day'] = raw['timestamp'].apply(format_day)
    raw['date'] = raw['timestamp'].apply(format_date)

    export = raw[['user_address', 'underlying_amount', 'tx_id', 'date', 'day']]
    print(export)

    export.to_csv("deposit_export.csv", float_format='%g', index=False)

def export_unstake():
    """
    select user_address, withdraw_amount, withdraw_fee, request_timestamp, request_tx from stusdt_withdraw_log
    where status in (0,1,2,3) and request_timestamp >= 1690819200000 and request_timestamp < 1691942400000
    order by request_timestamp asc ;
    """

    raw = pd.read_csv("unstake.csv", sep='\t')

    raw['day'] = raw['request_timestamp'].apply(format_day)
    raw['date'] = raw['request_timestamp'].apply(format_date)
    raw['without_fee'] = raw['withdraw_amount'] - raw['withdraw_fee']

    export = raw[['user_address', 'withdraw_amount', 'withdraw_fee', 'request_tx', 'date', 'day', 'without_fee']]
    print(export)

    export.to_csv("unstake_export.csv", float_format='%g', index=False)

def export_claim():
    """
    select user_address, withdraw_amount, withdraw_fee, claim_timestamp, claim_tx from stusdt_withdraw_log
    where status in (3) and claim_timestamp >= 1690819200000 and claim_timestamp < 1691942400000
    order by claim_timestamp asc ;
    """

    raw = pd.read_csv("claim.csv", sep='\t')

    raw['day'] = raw['claim_timestamp'].apply(format_day)
    raw['date'] = raw['claim_timestamp'].apply(format_date)
    raw['without_fee'] = raw['withdraw_amount'] - raw['withdraw_fee']
    raw['status'] = '已提取'

    export = raw[['user_address', 'withdraw_amount', 'withdraw_fee', 'claim_tx', 'status','date', 'day', 'without_fee']]
    print(export)

    export.to_csv("claim_export.csv", float_format='%g', index=False)

export_claim()