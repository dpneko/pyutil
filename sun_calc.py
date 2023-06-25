# -*- encoding: utf-8 -*-
import pymysql
import json
import pandas as pd
import time


def all_pools(conn: pymysql.Connection):
    sql = f"SELECT distinct(pool_address) FROM speed_changes_gov;"

    data = []
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()

    # print(data)
    return data


def current_total_balance(conn: pymysql.Connection, pool: str):
    sql = f"SELECT * FROM current_total_balance WHERE pool_address = '{pool}'"

    data = []
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchone()

    # print(data)
    return data


def current_state(conn: pymysql.Connection, pool: str):
    sql = f"SELECT * FROM current_user_balance WHERE pool_address = '{pool}'"
    data = []
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()

    # print(data)
    return data


def history_speeds(conn: pymysql.Connection, pool:str):
    sql = f"SELECT * FROM speed_changes where pool_address = '{pool}' order by ts asc, id asc"
    data = []
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()

    # print(data)
    return data


def history_gover_speeds(conn: pymysql.Connection, pool:str):
    sql = f"SELECT * FROM speed_changes_gov WHERE pool_address = '{pool}' ORDER BY ts ASC, id ASC"
    data = []
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()

    # print(data)
    return data


def history_events(conn: pymysql.Connection, pool: str):
    sql = f"SELECT * FROM sunio_pool_event_update_liquidity_limit WHERE gauge_address = '{pool}' order by ts asc, id asc"
    data = []
    with conn.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()

    # print(data)
    return data


# current_state: user -> [balance, reward, last_ts, reward_per_token_paid]
# balance_changes: [ts, user, balance, total_balance], 根据 ts 倒序.
def back_through(current_total_balance: int, current_ts: int, start_ts: int,
                 current_state: dict, balance_changes: list):
    earlier_than_st = False
    total_balance = current_total_balance
    state = current_state
    bc = reversed(balance_changes)

    for each in bc:
        # 回溯到 start_ts 之前一个事件即可.
        if earlier_than_st:
            break
        if each[0] > current_ts:
            continue
        if each[0] < start_ts:
            earlier_than_st = True
        total_balance = each[3]
        user = each[1]
        state[user] = [each[2], 0, each[0], 0]

    print(total_balance, state)
    return total_balance, state


# initial_state: user -> [balance, reward, last_ts, reward_per_token_paid]
# balance_changes: [ts, user, balance, total_balance]
# speed_changes: [ts, speed]
def calculate(total_balance: int, reward_per_token_paid: int, speed: int,
              last_ts: int, end_ts: int,
              initial_state: dict, balance_changes: list, speed_changes: list):
    total_balance = total_balance
    # 放大 10 ** 18
    reward_per_token_paid = reward_per_token_paid
    last_ts = last_ts
    # 为了避免误差, 在计算里将 speed 放大 10 ** 18 倍.
    speed = speed * 10 ** 18
    state = initial_state
    balance_changes = balance_changes
    speed_changes = speed_changes

    len_balance_changes = len(balance_changes)
    len_speed_changes = len(speed_changes)
    i_balance_changes = 0
    i_speed_changes = 0

    while i_balance_changes < len_balance_changes or i_speed_changes < len_speed_changes:
        # 只有 bc 或 bc 时间更早
        if i_speed_changes >= len_speed_changes or (i_balance_changes < len_balance_changes and balance_changes[i_balance_changes][0] <= speed_changes[i_speed_changes][0]):
            change = balance_changes[i_balance_changes]
            if change[0] > end_ts:
                break

            user = change[1]
            if user not in state:
                state[user] = [0, 0, last_ts, reward_per_token_paid]

            if change[0] < last_ts:
                # 更新余额数据.
                state[user][0] = change[2]
                total_balance = change[3]

            # 需要更新 rptp 和 lt
            if change[0] >= last_ts:
                if total_balance != 0:
                    reward_per_token_paid += speed * (change[0] - last_ts) // total_balance
                last_ts = change[0]

                # update user info
                state[user][1] += state[user][0] * (reward_per_token_paid - state[user][3])
                state[user][3] = reward_per_token_paid
                state[user][2] = last_ts

                # update user balance
                state[user][0] = change[2]

                # update total balance
                total_balance = change[3]
            i_balance_changes += 1

        # 只有 sc 或 sc 时间更早
        else:
            change = speed_changes[i_speed_changes]
            if change[0] > end_ts:
                break
            # 需要更新 rptp 和 lt 和 sp
            if change[0] < last_ts:
                speed = change[1] * 10 ** 18
            if change[0] >= last_ts:
                if total_balance != 0:
                    reward_per_token_paid += speed * (change[0] - last_ts) // total_balance
                last_ts = change[0]
                speed = change[1] * 10 ** 18

            i_speed_changes += 1

    if last_ts < end_ts:
        if total_balance > 0:
            reward_per_token_paid += speed * (end_ts - last_ts) // total_balance
        last_ts = end_ts

    rewards = []
    for user in state.keys():
        if state[user][3] < reward_per_token_paid:
            state[user][1] += state[user][0] * (reward_per_token_paid - state[user][3])
            state[user][2] = last_ts
            state[user][3] = reward_per_token_paid

        if state[user][1] > 0:
            rewards.append([user, state[user][1] // 10 ** 18])

    # print(state)
    return rewards


def visit_pool(conn: pymysql.Connection, pool: str):
    # id, ts, pool_address, total_balance, total_working_supply
    ctb = current_total_balance(conn, pool)

    # id, ts, pool, user, balance, working_balance
    cs = current_state(conn, pool)

    # id, ts, pool_address, new_speed
    hs = history_speeds(conn, pool)

    # id, ts, pool, user, user_balance, total_balance, working_balance, total_working_supply
    he = history_events(conn, pool)

    current_ts = ctb[1]
    total_balance = ctb[3]

    # TODO: 开始时间: 2022-09-30 21:00:00
    # start_ts = 1664542800
    start_ts = current_ts

    c_s = dict()
    for each in cs:
        c_s[each[3]] = [int(each[4]), 0, start_ts, 0]

    b_c = []
    for each in he:
        b_c.append([each[1], each[3], int(each[4]), int(each[5])])

    s_c = []
    for each in hs:
        s_c.append([each[1], int(each[3])])

    # prev_tb, prev_st = back_through(total_balance, current_ts, start_ts, c_s, b_c)
    # calculate(prev_tb, 0, 0, start_ts, current_ts, prev_st, b_c, s_c)

    return calculate(0, 0, 0, start_ts, current_ts, dict(), b_c, s_c)


def visit_pool_for_period(conn: pymysql.Connection, pool: str, start: int, end: int):
    # id, ts, pool_address, new_speed
    hs = history_speeds(conn, pool)

    # id, ts, pool_address, new_speed
    hgs = history_gover_speeds(conn, pool)

    # id, ts, pool, user, user_balance, total_balance, working_balance, total_working_supply
    he = history_events(conn, pool)

    b_c = []
    g_b_c = []
    for each in he:
        b_c.append([each[1]/1000, each[3], int(each[4]), int(each[5])])
        g_b_c.append([each[1]/1000, each[3], int(each[6]), int(each[7])])

    s_c = []
    for each in hs:
        s_c.append([each[1], int(each[3])])

    g_s_c = []
    for each in hgs:
        g_s_c.append([each[1], int(each[3])])

    project_rewards = calculate(0, 0, 0, start, end, dict(), b_c, s_c)
    governance_rewards = calculate(0, 0, 0, start, end, dict(), g_b_c, g_s_c)

    return project_rewards, governance_rewards


def run():
    db = pymysql.connect(host="47.252.23.81", database="sun_pool_stats", user="root", password="admin")
    results = dict()
    results['project'] = dict()
    results['gov'] = dict()

    # 北京时间周六凌晨0点
    starttime = "2023-06-10 00:00:00"
    endtime = "2023-06-17 00:00:00"
    start = int(time.mktime(time.strptime(starttime, '%Y-%m-%d %H:%M:%S')))
    end = int(time.mktime(time.strptime(endtime, '%Y-%m-%d %H:%M:%S'))) 

    justin_addresses = ("TCy2gn2skTzzRizqqKJRRq25NEHKcTz5cD", "TPyjyZfsYaXStgz2NmAraF1uZcMtkgNan5",
                        "TDqMwZVTSPLTCZQC55Db3J69eXY7HLCmfs", "TFsuFNs5vyjJ8iKUT5uvJUhjnx5VjFdWPy",
                        "TGfWKtSDs96TrX1GwH3xsf5HxZhj1PPydv", "TUjx6w55Nx9G4GjjRNEB4e7w5BUH3WmJTZ",
                        "TQwh1ZDBdqMKDtGWEeDdrRUUbtgaVL1Se2", "TSF2rqLdrrZG7PZkDxtvu6B2PTpofidMAX")

    project_percentage = dict()
    gov_percentage = dict()

    for each in all_pools(db):
    # for each in [['TEULJy4MJeRUTMPGTTvsBkmDPM4PEsMBTw'],['TPx8BXTgiB1tiL9A9BZuz67bZBvFGYdJS8'],
    #              ['TAkrcKsS5FW9f3ZfzvWy6Zvsz9uEjUxPoV'],['TJ3Qnm9VhzJzhcxk49ZpHBRatD1bsD4xYq'],
    #              ['TCpu3GnK6PPZV9ama85mRP97YqRuVXdcSd'],['THZgwb6LTg9LydbLw6gT4YMdu9y4nA5dnp'],
    #              ['TBSRZYLZ2pguF3EqLz86Kt9hZ4eqKEQMSY']]:
        pool = each[0]

        project, governance = visit_pool_for_period(db, pool, start, end)

        results['project'][pool] = project
        results['gov'][pool] = governance

        justin = 0
        total = 0
        for address, reward in project:
            total += reward
            if address in justin_addresses:
                justin += reward

        project_percentage[pool] = [total, justin, justin / total if total > 0 else 0.0]

        gov_justin = 0
        gov_total = 0
        for address, reward in governance:
            gov_total += reward
            if address in justin_addresses:
                gov_justin += reward

        gov_percentage[pool] = [gov_total, gov_justin, gov_justin / gov_total if gov_total > 0 else 0.0]

    # print(results)

    # print(json.dumps(project_percentage))
    # print(json.dumps(gov_percentage))
    df_project = pd.DataFrame(project_percentage, dtype=float, index=['total', 'justin', 'percentage']).T
    df_gov = pd.DataFrame(gov_percentage, dtype=float, index=['total', 'justin', 'percentage']).T
    df_project.to_csv(f"挖矿/项目方挖矿_{start}_{end}.csv", float_format="%.0f")
    df_gov.to_csv(f"挖矿/治理挖矿_{start}_{end}.csv", float_format="%.0f")
    print(f"文件保存到 挖矿/项目方挖矿_{start}_{end}.csv 和 挖矿/治理挖矿_{start}_{end}.csv")


def generate_sql(file:str):
    result = []
    with open(file, 'r') as f:
        for line in f.readlines():
            data = line.replace('\n', '').split('\t')
            i = 1
            while i < len(data):
                result.append(f"INSERT INTO speed_changes_gov(ts, pool_address, new_speed) VALUES ({data[i]}, '{data[0]}', {data[i+1]});")
                i += 2

    print('\n'.join(result))
    return result


if __name__ == '__main__':
    run()
    # generate_sql("/Users/daniel/Desktop/speeds.txt")

################################################
    # # TODO: 开始时间: 2022-10-14 00:00:00
    # start = 1665676800

    # # TODO: 结束时间: 2022-10-21 00:00:00
    # end = 1666281600


#####################################
    # # TODO: 开始时间: 2022-10-21 00:00:00
    # start = 1666281600

    # # TODO: 结束时间: 2022-10-28 00:00:00
    # end = 1666886400