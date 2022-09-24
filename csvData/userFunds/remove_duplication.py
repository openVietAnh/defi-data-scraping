token_lst = ["DAI", "USDT", "USDC", "WBTC", "WETH"]

for token in token_lst:
    filtered = []
    s = set()
    with open(token + "_fund_block.csv", "r") as f:
        data = f.readlines()
        for item in data:
            if item not in s:
                filtered.append(item)
                s.add(item)

    with open(token + "_fund_block.csv", "w") as f:
        f.writelines(filtered)