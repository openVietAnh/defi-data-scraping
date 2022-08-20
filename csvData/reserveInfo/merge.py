import csv

token_lst = ["USDT"]

for token in token_lst:
    userCount, tokenHHI = {}, {}
    with open("../tokenUserCount/" + token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            userCount[item[0]] = item[1]

    with open("../userFunds/" + token + "_HHI.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            tokenHHI[item[0]] = item[1]

    data = []
    lastUserCount, lastHHI = None, None
    keys = ["timestamp","time","blockNumber","totalDeposits","depositRate","stableBorrowRate","variableBorrowRate","utilizationRate"]
    with open(token + "_TLV_USD.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            row = {keys[i]: item[i] for i in range(len(keys))}
            if item[0] in userCount.keys():
                row["userCount"] = userCount[item[0]]
                lastUserCount = userCount[item[0]]
            else:
                row["userCount"] = lastUserCount
            
            if item[2] in tokenHHI.keys():
                row["HHI"] = tokenHHI[item[2]]
                lastHHI = tokenHHI[item[2]]
            else:
                row["HHI"] = lastHHI
            data.append(row)
    
    keys = keys + ["userCount", "HHI"]
    with open(token + '_info.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
