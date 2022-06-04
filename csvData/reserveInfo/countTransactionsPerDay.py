import csv
import datetime

token_lst = ["DAI", "USDC", "USDT", "WBTC", "WETH"]
day = None

for token in token_lst:
    transactionInDay, count = [], 0
    with open(token + "_raw_info.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            timestamp = int(item[-2])
            date = datetime.datetime.fromtimestamp(timestamp)
            if day is None:
                day, count = date.day, 1
            else:
                if day == date.day:
                    count += 1
                else:
                    day = date.day
                    transactionInDay.append(count)
                    count = 1
    print(token, sum(transactionInDay) / len(transactionInDay))
