import csv

hash_set = set()

with open("WBTC_block.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        hash_set.add(item[0])

with open("../tokenTransactions/WBTC.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None) 
    for item in reader:
        if item[0].split(":")[2] not in hash_set:
            print(item[0].split(":")[2])