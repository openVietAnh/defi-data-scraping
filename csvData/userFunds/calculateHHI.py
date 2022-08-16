# Start time
# DAI:  1606840850
# USDC: 1606914455 (lastest)
# USDT: 1606904131
# WBTC: 1606913751
# WETH: 1606777900

# End time
# DAI:  1659284341
# USDC: 1659286633
# USDT: 1659278863 (earliest)
# WBTC: 1659283944
# WETH: 1659286703

import csv
from web3 import Web3, EthereumTesterProvider
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/0e3D_mlVqAhNuFvqu1-Exd3ElNON88KE'))
print(w3.isConnected())

def calculate_hhi(user_funds):
    total = sum(user_funds.values())
    return sum([(value / total * 100) ** 2 for value in user_funds.values()])

def update_funds(user_funds, deposit_rate, before, after):
    for key, value in user_funds.items():
        gain = value * deposit_rate / 31556926 * (after - before)
        user_funds[key] += gain
    return user_funds

token_lst = ["USDC", "USDT", "WBTC", "WETH", "DAI"]

for token in token_lst:
    data = []
    user_funds = {}
    last_timestamp = 0
    deposit_rate = 0
    with open(token + ".csv", "r") as f:
        data = f.readlines()
        for item in data:
            info = item.strip().split(",")
            user_funds = update_funds(user_funds, deposit_rate, last_timestamp, int(info[1]))
            if info[0] == "deposit":
                try:
                    user_funds[info[2]] += float(info[3]) / (10 ** 18)
                except KeyError:
                    user_funds[info[2]] = float(info[3]) / (10 ** 18)
            elif info[0] == "redeemUnderlying":
                try:
                    user_funds[info[3]] -= float(info[2]) / (10 ** 18)
                except KeyError:
                    hash = info[-1]
                    user = w3.eth.get_transaction_receipt(hash)["from"].lower()
                    try:
                        user_funds[user] -= float(info[2]) / (10 ** 18)
                    except KeyError:
                        try:
                            user_funds[info[4]] -= float(info[2]) / (10 ** 18)
                        except KeyError:
                            print("not found", info)
            elif info[0] == "liquidationCall":
                try:
                    user_funds[info[2]] -= float(info[3]) / (10 ** 18)
                except KeyError:
                    hash = info[-1]
                    user = w3.eth.get_transaction_receipt(hash)["from"].lower()
                    try:
                        user_funds[user] -= float(info[2]) / (10 ** 18)
                    except KeyError:
                        print("User not found", user, hash)
            elif info[0] == "update":
                data.append({"timestamp": info[1], "HHI": calculate_hhi(user_funds)})
            else:
                deposit_rate = float(info[0])
            last_timestamp = int(info[1])
    
    with open(token + "_HHI.csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ["timestamp", "HHI"])
        dict_writer.writeheader()
        dict_writer.writerows(data)



