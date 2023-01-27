import csv

file_lst = ["borrow", "deposit", "flashLoan", "liquidationCall", "redeemUnderlying", "repay", "swap", "usageAsCollateral"]

for file in file_lst:
    data = []

    with open(file + "_update.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        keys = next(reader, None)
        for item in reader:
            data.append({keys[i]: item[i] for i in range(len(keys))})

    data.sort(key = lambda x: x["timestamp"])

    with open(file + '_update.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)