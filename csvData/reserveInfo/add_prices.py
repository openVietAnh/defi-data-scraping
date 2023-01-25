import csv

price = {}
with open("../tokenPriceinUSD/WBTC-usd-price.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        price[item[0]] = float(item[1])

data = []
keys = ["timestamp","time","blockNumber","totalDeposits","depositRate","stableBorrowRate","variableBorrowRate","utilizationRate","userCount","HHI","depositers","borrowers","price"]
with open("WBTC_info.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        row = {keys[i]: item[i] for i in range(len(keys) - 1)}
        row["price"] = price[item[0]]
        data.append(row)
with open('WBTC_full_info.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)