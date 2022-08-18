import csv

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]

for token in token_lst:
    data, hashset = [], set()
    with open(token + "_new.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in hashset:
                data.append({"hash": item[0], "block": item[1]})
                hashset.add(item[0])

    with open(token + '_filtered.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ["hash", "block"])
        dict_writer.writeheader()
        dict_writer.writerows(data)