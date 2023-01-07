import csv
s = set()
with open("WBTC_depositers.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader, None)
    for item in reader:
        s.add(item[0])
count = 0
lines = []
with open("./WBTC_depositer_block.csv", "r") as f:
    data = f.readlines()
    for item in data:
        if item.strip() not in s:
            count += 1
            lines.append(item)
with open("missing.txt", "w") as f:
    f.writelines(lines)
print(count)