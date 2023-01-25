import csv

price = {}
with open("../tokenPriceinUSD/WBTC-usd-price.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        price[item[0]] = float(item[1])

count = 0
with open("WBTC_info.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        if item[0] not in price:
            count += 1

print(count)