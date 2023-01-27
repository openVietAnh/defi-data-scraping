import csv

f_lst = ["allTransaction_update", "allTransactionType"]

for f in f_lst:
    data = []

    with open(f + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        keys = next(reader, None)
        for item in reader:
            data.append({keys[i]: item[i] for i in range(len(keys))})

    data.sort(key = lambda x: x["timestamp"])

    with open(f + '.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)