from datetime import datetime
from trongrid import getEventsByContractAndEvent

def stats_buy_sell(psm, buyOrSell, start, end, decimal=6):
    event_name = "BuyGem" if buyOrSell else "SellGem"
    start_ts = datetime.strptime(start, "%Y-%m-%d").timestamp()*1000
    end_ts = datetime.strptime(end, "%Y-%m-%d").timestamp()*1000
    events = getEventsByContractAndEvent(psm, event_name, start_ts, end_ts)
    trans_values = [int(event['result']['value']) for event in events]
    txn_ids = [event['transaction_id'] for event in events]
    return len(trans_values), sum(trans_values)/pow(10, decimal)


def print_result(start, end):
    count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", True, start, end) # usdt BuyGem
    print(f"usdd兑换usdt, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", False, start, end) # usdt SellGem
    print(f"usdt兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", True, start, end) # usdc BuyGem
    print(f"usdd兑换usdc, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", False, start, end) # usdc SellGem
    print(f"usdc兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    count, volume = stats_buy_sell("TY2op6AKcEkFhv8hxNJj3FBUfjManxYLSe", True, start, end, 18) # tusd BuyGem
    print(f"usdd兑换tusd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    count, volume = stats_buy_sell("TY2op6AKcEkFhv8hxNJj3FBUfjManxYLSe", False, start, end, 18) # tusd SellGem
    print(f"tusd兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")


if __name__ == '__main__':
    print_result("2022-08-26", "2022-09-02")
    print_result("2022-09-02", "2022-09-09")

    # start, end = "2022-08-28", "2022-09-04"
    # count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", True, start, end) # usdt BuyGem
    # print(f"usdd兑换usdt, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", False, start, end) # usdt SellGem
    # print(f"usdt兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", True, start, end) # usdc BuyGem
    # print(f"usdd兑换usdc, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", False, start, end) # usdc SellGem
    # print(f"usdc兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")

    # start, end = "2022-08-21", "2022-08-28"
    # count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", True, start, end) # usdt BuyGem
    # print(f"usdd兑换usdt, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", False, start, end) # usdt SellGem
    # print(f"usdt兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", True, start, end) # usdc BuyGem
    # print(f"usdd兑换usdc, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", False, start, end) # usdc SellGem
    # print(f"usdc兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")

    # start, end = "2022-08-01", "2022-08-21"
    # count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", True, start, end) # usdt BuyGem
    # print(f"usdd兑换usdt, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TM9gWuCdFGNMiT1qTq1bgw4tNhJbsESfjA", False, start, end) # usdt SellGem
    # print(f"usdt兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", True, start, end) # usdc BuyGem
    # print(f"usdd兑换usdc, {start}~{end}, 交易数:{count}, 交易总额:{volume}")
    # count, volume = stats_buy_sell("TUcj1rpMgJCcFZULyq7uLbkmfh9xMnYTmA", False, start, end) # usdc SellGem
    # print(f"usdc兑换usdd, {start}~{end}, 交易数:{count}, 交易总额:{volume}")


