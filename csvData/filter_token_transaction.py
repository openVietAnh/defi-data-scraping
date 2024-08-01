import csv

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]
hash_to_token = {}

token_transactions = {token: [] for token in token_lst}
keys = ["id", "type", "user", "pool", "timestamp"]

file_config = [
    ("borrow", 5),
    ("deposit", 3),
    ("repay", 4),
    ("usageAsCollateral", 3),
    ("redeemUnderlying", 3),
    ("swap", 4),
    ("liquidationCall", 6),
    ("flashLoan", 3),
]

TYPE_ID_INDEX = {
    "borrow": 4,
    "deposit": 2,
    "flashLoan": 1,
    "liquidationCall": 2,
    "redeemUnderlying": 1,
    "repay": 1,
    "swap": 2,
    "usageAsCollateral": 1,
}

for file in file_config:
    with open("./update_data/" + file[0] + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            hash_to_token[item[TYPE_ID_INDEX[file[0]]]] = item[file[1]]

with open("./update_data/allTransactionType.csv", "r") as csvfile:
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
