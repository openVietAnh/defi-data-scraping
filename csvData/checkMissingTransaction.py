import csv

id_set = set()

with open("allTransaction.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        id_set.add(item[0])

files = ["borrow", "deposit", "flashLoan", "liquidationCall", "rebalanceStableBorrowRate", "redeemUnderlying", "repay", "swap", "usageAsCollateral"]
missing = []
for f in files:
    with open(f + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in id_set:
                if f == "borrow":
                    missing.append(",".join([item[0],f, item[7]]) + "\n")
                else:
                    missing.append(",".join([item[0],f, item[-1]]) + "\n")

with open("missingTransactions.txt", "w") as f:
    f.writelines(missing)