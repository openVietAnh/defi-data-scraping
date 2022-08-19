import csv 

token_lst = ["DAI", "USDT", "USDC", "WETH", "WBTC"]

for token in token_lst:
    s = set()
    with open("../reserveInfo/" + token + "_TLV_USD.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            s.add(item[2])

    count = 0
    with open(token + "_fund_block.csv", 'r') as f:
        data = f.readlines()
        for item in data:
            if item.strip() not in s:
                count += 1

    print(count)