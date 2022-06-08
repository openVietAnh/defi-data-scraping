import csv

token_lst = ["DAI", "WBTC" , "USDC", "USDT"]

for token in token_lst:
    transaction_timestamp = set()
    with open(token + "_updated.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            transaction_timestamp.add(item[0])

    count = 0
    with open(token + "_price_in_eth.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in transaction_timestamp:
                count += 1
    print(token, ":", count)