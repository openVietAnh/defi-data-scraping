import csv

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT", "WETH_2"]

for token in token_lst:
    data, hashset = [], set()
    with open("../tokenTransactions/" + token + ".csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            tx_hash = item[0].split(":")[2]
            if tx_hash not in hashset:
                data.append({"hash": tx_hash, "block": item[1]})
                hashset.add(tx_hash)

    with open(token + '.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, ["hash", "block"])
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)