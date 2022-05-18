import csv

token_lst = ["WBTC", "DAI", "USDT", "USDC"]
missing = []
timestamp_to_price = {}
with open("fullPrices.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamp_to_price[item[0]] = item[1]

for token in token_lst:
    with open("../csvData/" + token + "-price.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[1] not in timestamp_to_price.keys():
                missing.append(item[1])

print(missing)
