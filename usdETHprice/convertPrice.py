import csv

token_lst = ["WBTC", "DAI", "USDT", "USDC"]
timestamp_to_usd_price = {}
with open("fullPrices.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamp_to_usd_price[item[0]] = item[1]

for token in token_lst:
    data = []
    with open("../csvData/" + token + "-price.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            eth_price = int(item[0])
            usd_price = eth_price / float(timestamp_to_usd_price[item[1]])
            data.append({"timestamp": item[1], "price": usd_price})
    with open("../csvData/" + token + "-usd-price.csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ["timestamp", "price"])
        dict_writer.writeheader()
        dict_writer.writerows(data)