import csv

token_lst = ["DAI", "USDT", "USDC", "WBTC", "WETH"]

for token in token_lst:
    data = []

    with open(token + "_block.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        keys = next(reader, None)
        for item in reader:
            data.append({keys[i]: item[i] for i in range(len(keys))})

    data.sort(key = lambda x: x["block"])

    with open(token + '_block.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)