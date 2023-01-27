import csv

data = []
with open("usd_ethUpdatedPrice.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        data.append({"timestamp": item[0], "price": 1/ (float(item[1]) / 1000000000000000000)})

with open("WETH-usd-price.csv", 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)