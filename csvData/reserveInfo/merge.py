import csv

token_lst = ["DAI"]

for token in token_lst:
    userCount, tokenHHI, depositers, borrowers = {}, {}, {}, {}
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

    with open("../depositer/" + token + "_depositers.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            depositers[item[0]] = item[1]

    with open("../borrower/" + token + "_borrower.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            borrowers[item[0]] = item[1]

    data = []
    lastUserCount, lastHHI, lastDepositers, lastBorrowers = 0, 0, 0, 0
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

            if item[2] in depositers.keys():
                row["depositers"] = depositers[item[2]]
                lastDepositers = depositers[item[2]]
            else:
                row["depositers"] = lastDepositers
            data.append(row)

            if item[2] in borrowers.keys():
                row["borrowers"] = borrowers[item[2]]
                lastBorrowers = borrowers[item[2]]
            else:
                row["borrowers"] = lastBorrowers
            data.append(row)
    
    keys = keys + ["userCount", "HHI", "depositers", "borrowers"]
    with open(token + '_info.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
