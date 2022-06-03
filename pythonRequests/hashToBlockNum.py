from web3 import Web3, EthereumTesterProvider
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/0e3D_mlVqAhNuFvqu1-Exd3ElNON88KE'))
print(w3.isConnected())

import csv
data, hash_set = [], set()
token_lst = ["DAI", "USDC", "USDT", "WBTC", "WETH"]

for token in token_lst:
    with open("../csvData/tokenTransactions/" + token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            hash = item[0].split(":")[2]
            if hash not in hash_set:
                hash_set.add(hash)
                block_number = w3.eth.get_transaction_receipt(hash)["blockNumber"]
                print(hash, block_number)
                data.append({"hash": hash, "block": block_number})

    with open(token + '_block.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ["hash", "block"])
        dict_writer.writeheader()
        dict_writer.writerows(data)