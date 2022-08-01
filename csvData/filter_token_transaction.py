import csv

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]
hash_to_token = {}

token_transactions = {token: [] for token in token_lst}
keys = ["id", "type", "user", "pool", "timestamp"]

file_config = [
    ("borrow", 3),
    ("deposit", 3),
    ("repay", 4),
    ("usageAsCollateral", 3),
    ("redeemUnderlying", 4),
    ("swap", 3),
    ("liquidationCall", 3),
    ("flashLoan", 1),
]

for file in file_config:
    with open("./update_data/" + file[0] + "_update.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            hash_to_token[item[0].split(":")[2]] = item[file[1]]

with open("./update_data/allTransactionType.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        if hash_to_token[item[0].split(":")[2]] in token_lst:
            token_transactions[hash_to_token[item[0].split(":")[2]]].append({keys[index]: item[index] for index in range(len(keys))})

for token in token_lst:
    with open("./update_data/" + token + ".csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(token_transactions[token])
