import csv

token_lst = ["DAI", "USDC", "USDT", "WBTC", "WETH"]
keys = ["id", "type", "user", "pool", "timestamp"]

for token in ["WBTC"]:
    data = []

    with open(token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            data.append({keys[i]: item[i] for i in range(len(keys))})

    data.sort(key = lambda x: x["timestamp"])

    with open(token + '.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)