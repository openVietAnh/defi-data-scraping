import csv

file_lst = ["borrow", "deposit", "flashLoan", "liquidationCall", "redeemUnderlying", "repay", "swap", "usageAsCollateral"]

for file in file_lst:
    data = []

    with open(file + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        keys = next(reader, None)
        for item in reader:
            data.append({keys[i]: item[i] for i in range(len(keys))})

    data.sort(key = lambda x: x["timestamp"])

    with open(file + '.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)