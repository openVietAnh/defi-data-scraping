import csv

token_lst = ["WBTC", "DAI", "USDT", "USDC"]
timestamp_to_usd_price = {}
with open("full_updated.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamp_to_usd_price[item[0]] = item[1]

for token in token_lst:
    print(token)
    data = []
    with open("../csvData/tokenPriceinETH/" + token + "_updated.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if token == "WBTC" and len(item[1]) == 15:
                eth_price = int(item[1]) * 100000
            else:
                eth_price = int(item[1])
            try:
                usd_price = eth_price / float(timestamp_to_usd_price[item[0]])
                data.append({"timestamp": item[0], "price": usd_price})
            except KeyError:
                pass
    with open("../csvData/tokenPriceinUSD/" + token + "-usd-price.csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ["timestamp", "price"])
        dict_writer.writeheader()
        dict_writer.writerows(data)