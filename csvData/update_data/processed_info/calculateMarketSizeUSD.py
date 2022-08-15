import csv

token_lst = ["DAI", "USDC", "USDT", "WBTC", "WETH"]

for token in token_lst:
    keys = ["timestamp", "time","blockNumber", "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate", "utilizationRate"]
    data = []
    tokenPrice = {}
    with open("../price/" + token + "-usd-price.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            tokenPrice[item[0]] = float(item[1])

    with open(token + "_processed_info.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            dct = {keys[index]: item[index] for index in range(len(keys))}
            dct["totalDeposits"] = float(dct["totalDeposits"]) * tokenPrice[item[0]]
            data.append(dct)
    
    with open(token + "_TLV_USD.csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)