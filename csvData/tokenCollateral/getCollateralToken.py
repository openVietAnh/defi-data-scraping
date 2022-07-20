import csv

# deposit
# id,user,caller,reserve,amount,timestamp
# borrow
# id,user,caller,reserve,amount,borrowRate,borrowRateMode,timestamp,stableTokenDebt,variableTokenDebt
# usageAsCollateral
# id,pool,user,reserve,fromState,toState,timestamp

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]
files = ["deposit", "borrow", "usageAsCollateral"]
transactions = []
deposit_id_to_reserve = {}
usage_id_to_reserve = {}

for f in files:
    with open("../" + f + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if f == "deposit":
                transactions.append(("deposit", item[-1], item[1], item[3]))
                deposit_id_to_reserve[item[0].split(":")[2]] = item[3]
            elif f == "borrow":
                transactions.append(("borrow", item[7], item[1], item[0], item[3]))
            elif f == "usageAsCollateral":
                transactions.append(("usageAsCollateral", item[-1], item[2], item[3], item[5]))
                usage_id_to_reserve[item[0].split(":")[2]] = item[3]
    
transactions.sort(key = lambda x: x[1])
user_collateral = {}
token_collateral = {token: set() for token in token_lst}
for item in transactions:
    if item[0] == "deposit":
        try:
            user_collateral[item[2]][item[-1]] = False
        except KeyError:
            user_collateral[item[2]] = {item[-1]: False}
    elif item[0] == "usageAsCollateral":
        try:    
            user_collateral[item[2]][item[3]] = False if item[-1] == "False" else True
        except KeyError:
            user_collateral[item[2]] = {item[3]: False if item[-1] == "False" else True}
    else:
        if item[-1] in token_lst:
            try:
                for collateral, enabled in user_collateral[item[2]].items():
                    if enabled:
                        token_collateral[item[-1]].add(collateral)
            except KeyError:
                try:
                    token_collateral[item[-1]].add(deposit_id_to_reserve[item[3].split(":")[2]])
                except KeyError:
                    token_collateral[item[-1]].add(usage_id_to_reserve[item[3].split(":")[2]])
        
for key, value in token_collateral.items():
    print(key, ":", len(value))
    print(value)
