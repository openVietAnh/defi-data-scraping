# pylint: disable-msg=C0103
"""
    Calculate token price in USD from token price in ETH
"""
import csv

TOKEN_LST = ["WBTC", "DAI", "USDT", "USDC"]
timestamp_to_usd_price = {}
with open("full_updated.csv") as csvfile:
    READER = csv.reader(csvfile, delimiter=",")
    next(READER, None)
    for item in READER:
        timestamp_to_usd_price[item[0]] = item[1]

for token in TOKEN_LST:
    print(token)
    data = []
    with open("../csvData/tokenPriceinETH/" + token + "_updated.csv") as csvfile:
        READER = csv.reader(csvfile, delimiter=",")
        next(READER, None)
        for item in READER:
            if token == "WBTC":
                if len(item[1]) < 20:
                    eth_price = int(item[1]) * (10 ** (20 - len(item[1])))
                else:
                    eth_price = int(item[1])
            else:
                eth_price = int(item[1])
            try:
                usd_price = eth_price / float(timestamp_to_usd_price[item[0]])
                data.append({"timestamp": item[0], "price": usd_price})
            except KeyError:
                pass
    file_name = "../csvData/tokenPriceinUSD/" + token + "-usd-price.csv"
    with open(file_name, 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)
