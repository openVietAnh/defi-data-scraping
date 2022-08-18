import csv
# from web3 import Web3, EthereumTesterProvider
# w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/0e3D_mlVqAhNuFvqu1-Exd3ElNON88KE'))
# print(w3.isConnected())

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
hash_to_block = {}
reserve_index = {"deposit": 3, "liquidationCall": 3, "redeemUnderlying": 4}
token_block = {token: [] for token in token_lst}

for token in token_lst:
    with open("../hashtoBlockNum/" + token + "_filtered.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader, None)
        for item in reader:
            hash_to_block[item[0]] = item[1]

for f in files:
    count = 0
    with open("../" + f + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[reserve_index[f]] in token_lst:
                try:
                    token_block[item[reserve_index[f]]].append(int(hash_to_block[item[0].split(":")[2]]))
                except KeyError:
                    count += 1
    print(f, count)

for token in token_lst:
    token_block[token].sort()
    with open(token + "_fund_block.csv", "w") as f:
        f.writelines("\n".join(map(str, token_block[token])))