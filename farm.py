import json


def get_next_assign_frozen_reward(assign_json, week = 4):
    """获取下一次方法的奖励中历史冻结部分"""
    frozen_assign = json.loads(assign_json)
    total_next_assign = 0
    for d in frozen_assign:
        if int(d['l']) > int(d['s'])*week:
            total_next_assign += int(d['s'])*week
        else:
            total_next_assign += int(d['l'])
    return total_next_assign


def get_new_farmed(assign_json):
    """获取刚出完报表的这周的新挖的奖励"""
    for d in json.loads(assign_json):
        if round(float(d['l']) / float(d['s'])) == 23:
            return int(d['s'])*24
    return 0
