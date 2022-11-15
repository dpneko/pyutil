# -*- encoding: utf-8 -*-
import pymysql


def current_state(conn: pymysql.Connection, pool: str):
    sql = f"SELECT * FROM current_total_balance WHERE pool_address = '{pool}'"
    cursor = conn.cursor()
    cursor.execute(sql)

    print(cursor.fetchone())


# current_state: user -> [balance, reward, last_ts, reward_per_token_paid]
# balance_changes: [ts, user, balance, total_balance], 根据 ts 倒序.
def back_through(current_total_balance: int, current_ts: int, start_ts: int,
                 current_state: dict, balance_changes: list):
    earlier_than_st = False
    total_balance = current_total_balance
    state = current_state
    bc = balance_changes

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
    tb = total_balance
    # 放大 10 ** 18
    rptp = reward_per_token_paid
    lt = last_ts
    # 为了避免误差, 在计算里将 speed 放大 10 ** 18 倍.
    sp = speed * 10 ** 18
    state = initial_state
    bc = balance_changes
    sc = speed_changes

    l_bc = len(bc)
    l_sc = len(sc)
    i_bc = 0
    i_sc = 0

    while i_bc < l_bc or i_sc < l_sc:
        # 只有 bc 或 bc 时间更早
        if i_sc >= l_sc or bc[i_bc][0] <= sc[i_sc][0]:
            change = bc[i_bc]
            if change[0] > end_ts:
                break
            # 需要更新 rptp 和 lt
            if change[0] >= lt:
                rptp += sp * (change[0] - lt) // tb
                lt = change[0]
                user = change[1]
                if user not in state:
                    state[user] = [0, 0, lt, rptp]

                # update user info
                state[user][1] += state[user][0] * (rptp - state[user][3])
                state[user][3] = rptp
                state[user][2] = lt

                # update user balance
                state[user][0] = change[2]

                # update total balance
                tb = change[3]
            i_bc += 1

        # 只有 sc 或 sc 时间更早
        else:
            change = sc[i_sc]
            if change[0] > end_ts:
                break
            # 需要更新 rptp 和 lt 和 sp
            if change[0] >= lt:
                rptp += sp * (change[0] - lt) // tb
                lt = change[0]
                sp = change[1] * 10 ** 18

            i_sc += 1

    if lt < end_ts:
        rptp += sp * (end_ts - lt) // tb
        lt = end_ts

    for user in state.keys():
        if state[user][3] < rptp:
            state[user][1] += state[user][0] * (rptp - state[user][3])
            state[user][3] = rptp
            state[user][2] = lt

    print(state)
    return state


if __name__ == '__main__':
    db = pymysql.connect(host="127.0.0.1", database="sun_pool", user="root", password="root")
    pool = "TQAkP6jDnHkCbNw3E9bejAdsFou7Sp9his"

    current_state(db, pool)

    # initial_state: user -> [balance, reward, last_ts, reward_per_token_paid]
    # balance_changes: [ts, user, balance, total_balance]
    # speed_changes: [ts, speed]
    # def calculate(total_balance: int, reward_per_token_paid: int, speed: int,
    #               last_ts: int, end_ts: int,
    #               initial_state: dict, balance_changes: list, speed_changes: list):
    calculate(10000, 0, 100, 0, 1000, {"asd": [10000, 0, 0, 0]}, [[100, "zxc", 10000, 20000],[900, "asd", 0, 10000]], [])

    # current_state: user -> [balance, reward, last_ts, reward_per_token_paid]
    # balance_changes: [ts, user, balance, total_balance], 根据 ts 倒序.
    # def back_through(current_total_balance: int, current_ts: int, start_ts: int,
    #                  current_state: dict, balance_changes: list):
    back_through(10000, 1000, 0, {"zxc": [10000, 0, 1000, 0]}, [[900, "asd", 0, 10000], [100, "zxc", 10000, 20000],
                                                                [-100, "9999", 0, 10000], [-200, "asd", 10000, 90000]])
