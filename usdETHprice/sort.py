# pylint: disable-msg=C0103
"""
    Sort rows in csv files by timestamp
"""
import csv

data = []

with open("fullPrices.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        data.append({"timestamp": item[0], "price": item[1]})

data.sort(key=lambda x: x["timestamp"])

with open('fullPrices.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
