import csv

token_lst = ["WBTC", "DAI", "USDT", "USDC"]
timestamp_to_usd_price = {}
with open("usd_ethUpdatedPrice.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamp_to_usd_price[item[0]] = item[1]

for token in token_lst:
    print(token)
    data = []
    with open(token + "_updated.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if token == "WBTC":
                if len(item[1]) < 20:
                    eth_price = int(item[1]) * (10 ** (20 - len(item[1])))
                else:
                    eth_price = int(item[1])
            else:
                eth_price = int(item[1])
            try:
                usd_price = eth_price / float(timestamp_to_usd_price[item[0]])
                data.append({"timestamp": item[0], "price": usd_price})
            except KeyError:
                pass
    with open(token + "-usd-price.csv", 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)