# pylint: disable-msg=C0103
"""
    Calculate token prices at needed timestamps that AAVE V2 subgraph did not store
"""
import csv
import requests

TOKEN_LST = ["WBTC", "DAI", "USDC", "USDT"]

timestamp_to_prices = {}
with open("../usdETHprice/prices.csv", "r") as csvfile:
    READER = csv.reader(csvfile, delimiter=",")
    for item in READER:
        timestamp_to_prices[item[1]] = item[0]

for token in TOKEN_LST:
    with open("../csvData/" + token + "-price.csv", "r") as csvfile:
        READER = csv.reader(csvfile, delimiter=",")
        next(READER, None)
        for item in READER:
            if int(item[1]) not in timestamp_to_prices.keys():
                after_query = """
                {
                usdEthPriceHistoryItems(
                    orderBy: timestamp, 
                    orderDirection: asc, 
                    where: {
                    timestamp_gt: """ + item[1] + """
                    },
                    first: 1
                ) {
                    price
                    timestamp
                }
                }
                """

                before_query = """
                {
                usdEthPriceHistoryItems(
                    orderBy: timestamp, 
                    orderDirection: desc, 
                    where: {
                    timestamp_lt: """ + item[1] + """
                    },
                    first: 1
                ) {
                    price
                    timestamp
                }
                }
                """
                print("timestamp", item[1], "missing")
                response = requests.post(
                    'https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                    '',
                    json={'query': after_query})
                after_price = response.json()["data"]["usdEthPriceHistoryItems"][0]
                response = requests.post(
                    'https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                    '',
                    json={'query': before_query})
                before_price = response.json()["data"]["usdEthPriceHistoryItems"][0]
                price_diff = int(after_price["price"]) - int(before_price["price"])
                time_diff = after_price["timestamp"] - before_price["timestamp"]
                print(before_price, after_price)
                change = (price_diff / time_diff) * (int(item[1]) - before_price["timestamp"])
                calculated_price = int(before_price["price"]) + change
                print("Calculated price", calculated_price)
                timestamp_to_prices[int(item[1])] = calculated_price

DATA = [{"timestamp": key, "price": timestamp_to_prices[key]} for key in timestamp_to_prices]
with open("../usdETHprice/" + 'fullPrices.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(DATA)
