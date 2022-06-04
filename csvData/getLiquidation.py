import csv

userCount, min, min_user = {}, 2000000, None
with open("../csvData/allTransactionType.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        if item[1] != "liquidationCall":
            try:
                userCount[item[2]] += 1
            except:
                userCount[item[2]] = 1
        else:
            if min > userCount[item[2]]:
                min = userCount[item[2]]
                min_user = item[2]

print(min_user, min)
