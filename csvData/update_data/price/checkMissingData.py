import csv

token_lst = ["WBTC", "DAI", "USDT", "USDC"]
missing = []
timestamp_to_price = {}
with open("usd_ethUpdatedPrice.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamp_to_price[item[0]] = item[1]

for token in token_lst:
    with open("../processed_info/" + token + "_processed_info.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in timestamp_to_price.keys():
                missing.append(item[0])

print(len(missing))
