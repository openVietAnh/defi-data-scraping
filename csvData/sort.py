import csv

data, keys = [], ["id","pool","user","timestamp"]
with open("allTransaction.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        data.append({keys[index]: item[index] for index in range(len(keys))})

data.sort(key=lambda x: x["timestamp"])

with open('allTransaction.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
