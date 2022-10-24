# Total deposit: divide by decimal
# Borrow rate: divide by 25
# Utilization rate: keep
# Deposit rate: Liquidity rate / 10 ^ 27 then use the following formula:
# (1 + rate / SECONDS_PER_YEAR) ** SECONDS_PER_YEAR - 1

import csv
import datetime

def liquidationToDeposit(liquidationRate):
    SECONDS_PER_YEAR = 31556926
    return (1 + liquidationRate / (10 ** 27) / SECONDS_PER_YEAR) ** SECONDS_PER_YEAR - 1

token_config = [
    ("DAI", 18),
    ("USDC", 6),
    ("USDT", 6),
    ("WBTC", 8),
    ("WETH", 18),
]

keys = [
    "timestamp", 
    "time", 
    "blockNumber", 
    "totalDeposits", 
    "depositRate",
    "stableBorrowRate", 
    "variableBorrowRate",
    "utilizationRate"
]

for token in token_config:
    data = []
    with open(token[0] + "_new_info.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            dct = {
                "totalDeposits": int(item[1]) / (10 ** token[1]),
                "stableBorrowRate": int(item[2]) / (10 ** 25),
                "variableBorrowRate": int(item[3]) / (10 ** 25),
                "depositRate": liquidationToDeposit(int(item[4])),
                "utilizationRate": item[5],
                "timestamp": item[6],
                "blockNumber": item[7],
                "time": datetime.datetime.fromtimestamp(int(item[6])).isoformat()
            }
            data.append(dct)
        data.sort(key = lambda x: x["timestamp"])

    with open(token[0] + '_info.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)