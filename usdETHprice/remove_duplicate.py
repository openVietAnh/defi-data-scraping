# pylint: disable-msg=C0103
"""
    Remove duplicated rows from csv file
"""
import csv

data = []
timestamp = set()

with open("fullPrices.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        if item[0] not in timestamp:
            data.append({"timestamp": item[0], "price": item[1]})
            timestamp.add(item[0])

with open('fullPrices.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
