import csv
import datetime

token = "WETH"
keys = [
    "timestamp", 
    "time", 
    "blockNumber", 
    "totalDeposits", 
    "depositRate", 
    "stableBorrowRate", 
    "variableBorrowRate", 
    "utilizationRate", 
    "userCount", 
    "HHI", 
    "depositers", 
    "borrowers", 
    "price"
]
start_date = datetime.datetime(2020, 12, 2)
info = {}

with open("../reserveInfo/" + token + "_full_info.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        date = datetime.datetime.fromtimestamp(int(item[0]))
        if date >= start_date:
            d = datetime.datetime(date.year, date.month, date.day)
            try:
                info[d]["totalDeposits"].append(float(item[3]))
                info[d]["depositRate"].append(float(item[4]))
                info[d]["stableBorrowRate"].append(float(item[5]))
                info[d]["variableBorrowRate"].append(float(item[6]))
                info[d]["utilizationRate"].append(float(item[7]))
                info[d]["userCount"].append(float(item[8]))
                info[d]["HHI"].append(float(item[9]))
                info[d]["depositers"].append(float(item[10]))
                info[d]["borrowers"].append(float(item[11]))
                info[d]["price"].append(float(item[12]))
            except KeyError:
                info[d] = {}
                info[d]["totalDeposits"] = [float(item[3])]
                info[d]["depositRate"] = [float(item[4])]
                info[d]["stableBorrowRate"] = [float(item[5])]
                info[d]["variableBorrowRate"] = [float(item[6])]
                info[d]["utilizationRate"] = [float(item[7])]
                info[d]["userCount"] = [float(item[8])]
                info[d]["HHI"] = [float(item[9])]
                info[d]["depositers"] = [float(item[10])]
                info[d]["borrowers"] = [float(item[11])]
                info[d]["price"] = [float(item[12])]

data = []
while start_date in info.keys():
    row = {}
    row["date"] = start_date.strftime('%d/%m/%Y')
    row["totalDeposits"] = sum(info[start_date]["totalDeposits"]) / len(info[start_date]["totalDeposits"])
    row["depositRate"] = sum(info[start_date]["depositRate"]) / len(info[start_date]["depositRate"])
    row["stableBorrowRate"] = sum(info[start_date]["stableBorrowRate"]) / len(info[start_date]["stableBorrowRate"])
    row["variableBorrowRate"] = sum(info[start_date]["variableBorrowRate"]) / len(info[start_date]["variableBorrowRate"])
    row["utilizationRate"] = sum(info[start_date]["utilizationRate"]) / len(info[start_date]["utilizationRate"])
    row["userCount"] = sum(info[start_date]["userCount"]) / len(info[start_date]["userCount"])
    row["HHI"] = sum(info[start_date]["HHI"]) / len(info[start_date]["HHI"])
    row["depositers"] = sum(info[start_date]["depositers"]) / len(info[start_date]["depositers"])
    row["borrowers"] = sum(info[start_date]["borrowers"]) / len(info[start_date]["borrowers"])
    row["price"] = sum(info[start_date]["price"]) / len(info[start_date]["price"])
    data.append(row)
    start_date += datetime.timedelta(days = 1);

with open(token + "_average.csv", 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["date"] + keys[3:])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
