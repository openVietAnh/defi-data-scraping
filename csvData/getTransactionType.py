import csv

TYPE = ("borrow", "deposit", "flashLoan", "liquidationCall", "redeemUnderlying", "repay", "swap", "usageAsCollateral")
transactionType = {}

for file_name in TYPE:
    with open("./update_data/" + file_name + "_update.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            transactionType[item[0]] = file_name

data, keys = [], ["id", "pool", "user", "timestamp"]
typeNotFoundData = []
count = 0
with open("./update_data/allTransaction_update.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        dct = {keys[index]: item[index] for index in range(len(keys))}
        try:
            dct["type"] = transactionType[item[0]]
            data.append(dct)
        except KeyError:
            typeNotFoundData.append(dct)
            count += 1
print("Missing type:", count)
with open('./update_data/allTransactionType.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, ["id", "type", "user", "pool", "timestamp"] )
    dict_writer.writeheader()
    dict_writer.writerows(data)
with open('./update_data/missing.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, ["id", "user", "pool", "timestamp"] )
    dict_writer.writeheader()
    dict_writer.writerows(typeNotFoundData)