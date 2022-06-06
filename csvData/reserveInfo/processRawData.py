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
    ("DAI", 18, 1),
    ("USDC", 6, 0),
    ("USDT", 6, 0),
    ("WBTC", 8, 1),
    ("WETH", 18, 1),
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
    with open(token[0] + "_raw_info.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            dct = {
                "totalDeposits": int(item[0 + token[2]]) / (10 ** token[1]),
                "stableBorrowRate": int(item[1 + token[2]]) / (10 ** 25),
                "variableBorrowRate": int(item[2 + token[2]]) / (10 ** 25),
                "depositRate": liquidationToDeposit(int(item[3 + token[2]])),
                "utilizationRate": item[4 + token[2]],
                "timestamp": item[5 + token[2]],
                "blockNumber": item[6 + token[2]],
                "time": datetime.datetime.fromtimestamp(int(item[5 + token[2]])).isoformat()
            }
            data.append(dct)
        data.sort(key = lambda x: x["timestamp"])

    with open(token[0] + '_info.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)