import json
from datetime import datetime
from trongrid import *

# with open(f"output/transactions_{speeder}.json", "w") as f:
#     json.dump(getTransactionsCallDataByContract(speeder), f, indent=6)

def print_schedules(speeder, start):
    with open(f"output/transactions_{speeder}.json") as f:
        call_datas = json.load(f)
    for txn_id, call_data in call_datas.items():
        if call_data[0] == "setEmissionSchedule(uint128[],uint128[])":
            schedules = json.loads(call_data[1][0])
            rates = json.loads(call_data[1][1])
            for schedule, rate in zip(schedules, rates):
                # if rate != 0:
                print(datetime.fromtimestamp(schedule + start), rate)

print_schedules("TP2JD7LfzXZU1L61ThHmLGi1n6sUJuUtK8", 1658361600)
# print_schedules("TEHoWRBQJi7LJ4jWxszoDksMyLf5BRrDv2", 1680767819)
