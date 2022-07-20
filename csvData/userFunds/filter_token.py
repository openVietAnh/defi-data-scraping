import csv

# deposit
# id,user,caller,reserve,amount,timestamp
# liquidationCall
# id,pool,user,collateralReserve,collateralAmount,principalReserve,principalAmount,liquidator,timestamp
# redeemUnderlying
# id,pool,user,to,reserve,amount,timestamp
# usageAsCollateral
# id,pool,user,reserve,fromState,toState,timestamp

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]
files = ["deposit", "liquidationCall", "redeemUnderlying"]
transactions = {token: [] for token in token_lst}
reserve_index = {"deposit": 3, "liquidationCall": 3, "redeemUnderlying": 4}

for f in files:
    with open("../" + f + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[reserve_index[f]] in token_lst:
                if f == "deposit":
                    transactions[item[reserve_index[f]]].append(("deposit", item[-1], item[1], item[4]))
                elif f == "liquidationCall":
                    transactions[item[reserve_index[f]]].append(("liquidationCall", item[-1], item[2], item[4]))
                elif f == "redeemUnderlying":
                    transactions[item[reserve_index[f]]].append(("redeemUnderlying", item[-1], item[5], item[3]))
    
for token in token_lst:
    transactions[token].sort(key = lambda x: x[1])
    lines = []
    for item in transactions[token]:
        lines.append(",".join(item) + "\n")
    with open(token + ".csv", "w") as f:
        f.writelines(lines)
