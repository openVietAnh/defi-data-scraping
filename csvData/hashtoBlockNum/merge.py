import csv 

token_lst = ["DAI", "WETH", "WBTC", "USDC", "USDT"]

data = []
keys = ["hash", "block"]

for token in token_lst:
    with open(token + "_filtered.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            data.append({"hash": item[0], "block": item[1]})

with open('all.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)