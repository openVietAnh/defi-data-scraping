import csv
s = set()
with open("DAI_depositers.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader, None)
    for item in reader:
        s.add(item[0])
count = 0
with open("./../userFunds/DAI_fund_block.csv", "r") as f:
    data = f.readlines()
    for item in data:
        if item.strip() not in s:
            count += 1
print(count)