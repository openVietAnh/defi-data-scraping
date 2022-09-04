import csv
# from web3 import Web3, EthereumTesterProvider
# w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/0e3D_mlVqAhNuFvqu1-Exd3ElNON88KE'))
# print(w3.isConnected())

# borrow
# id,user,caller,reserve,amount,borrowRate,borrowRateMode,timestamp,stableTokenDebt,variableTokenDebt
# repay
# id,pool,user,repayer,reserve,amount,timestamp
# liquidationCall
# id,pool,user,collateralReserve,collateralAmount,principalReserve,principalAmount,liquidator,timestamp

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]
files = ["borrow", "repay", "liquidationCall"]
hash_to_block = {}
reserve_index = {"borrow": 3, "liquidationCall": 3, "repay": 4}
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
    with open(token + "_borrower_block.csv", "w") as f:
        f.writelines("\n".join(map(str, token_block[token])))