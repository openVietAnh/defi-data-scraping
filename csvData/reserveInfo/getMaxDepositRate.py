import csv

token_lst = ["DAI", "USDC", "USDT", "WBTC", "WETH"]

for token in token_lst:
    with open(token + "_TLV_USD.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)

        values = []
        for item in reader:
            values.append(float(item[4]))
        
        print(token, max(values))