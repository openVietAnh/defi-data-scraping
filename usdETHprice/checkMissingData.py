import csv

token_lst = ["WBTC", "DAI", "USDT", "USDC"]
missing = []
timestamp_to_price = {}
with open("full_updated.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamp_to_price[item[0]] = item[1]

for token in token_lst:
    with open("../csvData/reserveInfo/" + token + "_info.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in timestamp_to_price.keys():
                missing.append(item[0])

print(len(missing))
