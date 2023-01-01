import csv

data = []

price, diluted, circulating, fee, revenue = {}, {}, {}, {}, {}
with open("fee-revenue.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        fee[item[0]] = item[1]
        revenue[item[0]] = item[2]
    
with open("market-cap.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        diluted[item[0]] = item[1]
        circulating[item[0]] = item[2]

with open("price.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        price[item[0]] = item[1]

with open("tvl-borrow.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        rows = {}
        rows["Date"] = item[0]
        rows["Total Deposit"] = item[1]
        rows["Total Borrowed"] = item[2]
        rows["Utilization Rate"] = float(item[2]) / float(item[1])
        rows["Liquidity"] = float(item[1]) - float(item[2])
        rows["Fee"] = fee[item[0]]
        rows["Revenue"] = revenue[item[0]]
        try:
            rows["Fully Diluted Market Cap"] = diluted[item[0]]
        except KeyError:
            rows["Fully Diluted Market Cap"] = "TBD"
        try:
            rows["Circulating Market Cap"] = circulating[item[0]]
        except KeyError:
            rows["Circulating Market Cap"] = "TBD"
        try:
            rows["Price"] = price[item[0]]
        except:
            rows["Price"] = "TBD"
        data.append(rows)

with open('aave-RQ2.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, data[0].keys())
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)