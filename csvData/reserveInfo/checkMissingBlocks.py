import csv

token_lst = ["DAI", "WBTC", "USDC", "USDT", "WETH"]
s = set()

for token in token_lst:
    with open(token + "_new_info.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            s.add(item[-1])

    count = 0
    with open("../hashtoBlockNum/" + token + "_filtered.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[1] not in s:
                count += 1
    
    print(count)