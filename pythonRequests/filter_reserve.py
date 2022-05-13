import csv

symbolToID = {}

with open("../csvData/reserves.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for reserve in reader:
        symbolToID[reserve[2]] = reserve[0]

symbols = ["WBTC", "WETH", "DAI", "USDC", "USDT"]
keys = None

with open("../csvData/january.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for token in symbols:
        borrows = []
        for index, item in enumerate(reader):
            if index == 0:
                keys = item
            if item[3] == symbolToID[token]:
                borrows.append({keys[i]: item[i] for i in range(len(keys))})
        print(token,":", len(borrows))
        with open(token + '_january.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(borrows)
