# pylint: disable-msg=C0103
"""
    Get transaction hash from transaction block number using Web3 client
"""
import csv
from web3 import Web3
URL = "https://eth-mainnet.alchemyapi.io/v2/0e3D_mlVqAhNuFvqu1-Exd3ElNON88KE"
WEB3_PROVIDER = Web3(Web3.HTTPProvider(URL))
print(WEB3_PROVIDER.is_connected())

data, hash_set = [], set()
TOKEN_LST = ["DAI", "USDC", "USDT", "WBTC", "WETH"]

for token in TOKEN_LST:
    with open("../csvData/tokenTransactions/" + token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            tx_hash = item[0].split(":")[2]
            if tx_hash not in hash_set:
                hash_set.add(tx_hash)
                block_number = WEB3_PROVIDER.eth.get_transaction_receipt(tx_hash)["blockNumber"]
                print(tx_hash, block_number)
                data.append({"hash": tx_hash, "block": block_number})

    with open(token + '_block.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, ["hash", "block"])
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)
