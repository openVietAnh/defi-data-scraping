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
    ("rebalanceStableBorrowRate", 3)
]

for file in file_config:
    with open(file[0] + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            hash_to_token[item[0]] = item[file[1]]

with open("allTransactionType.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        if hash_to_token[item[0]] in token_lst:
            token_transactions[hash_to_token[item[0]]].append({keys[index]: item[index] for index in range(len(keys))})

for token in token_lst:
    with open("./tokenTransactions/" + token + ".csv", 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(token_transactions[token])
