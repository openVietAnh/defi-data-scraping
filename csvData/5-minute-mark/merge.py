import csv

token_lst = ["WBTC", "WETH", "DAI", "USDC", "USDT"]

for token in token_lst:
    user_count = {}
    with open(token + "-user.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            user_count[item[0]] = item[1]
    
    data = []
    old_keys = ["timestamp", "time", "blockNumber", "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate", "utilizationRate"]
    with open(token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            info = {old_keys[i]: item[i] for i in range(len(item))}
            info["userCount"] = user_count[item[0]]
            data.append(dict(info))

    keys = ["timestamp", "time", "blockNumber", "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate", "utilizationRate", "userCount"]
    with open(token + "-info.csv", 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)