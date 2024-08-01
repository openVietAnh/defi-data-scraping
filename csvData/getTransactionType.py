import csv

TYPE = ("borrow", "deposit", "flashLoan", "liquidationCall", "redeemUnderlying", "repay", "swap", "usageAsCollateral")
transactionType = {}
TYPE_ID_INDEX = {
    "borrow": 4,
    "deposit": 2,
    "flashLoan": 1,
    "liquidationCall": 2,
    "redeemUnderlying": 1,
    "repay": 1,
    "swap": 2,
    "usageAsCollateral": 1,
}

for file_name in TYPE:
    with open("./update_data/" + file_name + ".csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            transactionType[item[TYPE_ID_INDEX[file_name]]] = file_name

data, keys = [], ["id", "pool", "timestamp", "user"]
typeNotFoundData = []
count = 0
with open("./update_data/allTransaction.csv", "r") as csv_file:
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
    DICT_WRITER = csv.DictWriter(output_file, ["id", "type", "user", "pool", "timestamp"] )
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
with open('./update_data/missing.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["id", "user", "pool", "timestamp"] )
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(typeNotFoundData)