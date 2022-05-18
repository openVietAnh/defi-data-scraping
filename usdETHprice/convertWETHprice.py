import csv

data = []
with open("fullPrices.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        data.append({"timestamp": item[0], "price": 1/ (float(item[1]) / 1000000000000000000)})

with open("../csvData/WETH-usd-price.csv", 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, ["timestamp", "price"])
    dict_writer.writeheader()
    dict_writer.writerows(data)