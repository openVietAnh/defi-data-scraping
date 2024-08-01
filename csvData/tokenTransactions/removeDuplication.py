import csv

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT", "WETH_2"]

for token in token_lst:
    data, hashset = [], set()
    with open(token + ".csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            tx_hash = item[0].split(":")[2]
            if tx_hash not in hashset:
                data.append(tx_hash)
                hashset.add(tx_hash)

    with open(token + '_filtered.csv', 'w') as output_file:
        output_file.writelines('\n'.join(data))
