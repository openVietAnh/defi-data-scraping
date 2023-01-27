import csv 

token_lst = ["USDC"]

for token in token_lst:
    s = set()
    with open(token + "_HHI_merged.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            s.add(item[0])

    count = 0
    with open(token + "_fund_block.csv", "r") as f:
        data = f.readlines()
        for item in data:
            if item.strip() not in s:
                count += 1

    print(count)
            