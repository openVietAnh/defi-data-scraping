import csv

data = []

with open("usd_ethPrice.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        data.append({"timestamp": item[0], "price": item[1]})

data.sort(key = lambda x: x["timestamp"])

with open('usd_ethPrice.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)