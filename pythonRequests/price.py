"""
    Get token prices in ETH at multiple timestamp from AAVE V2 subgraph
"""
import csv
import requests

TOKEN_LST = ["USDT", "USDC", "DAI", "WBTC", "WETH"]

for token in TOKEN_LST:
    keys, prices = ["timestamp", "price"], []
    current_time = 1654016400
    while True:
        query = """
        {
        reserves(where: {symbol: \"""" + token +"""\"}) {
            price {
            priceHistory(
                where: {
                    timestamp_lt: """ + str(current_time) + """},
                    first: 1000,
                    orderBy: timestamp,
                    orderDirection: desc
                ) {
                    price
                    timestamp
            }
            }
        }
        }
        """
        response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                                 '',
                                 json={'query': query})
        if response.status_code != 200:
            print("Problem reading from timestamp", current_time, ":", response.status_code)
            continue
        try:
            data = response.json()["data"]["reserves"][0]["price"]["priceHistory"]
        except (KeyError, AttributeError) as error:
            print("Error at timestamp", current_time)
            print(error)
            continue
        if len(data) == 0:
            break
        print(len(data), "prices found at timestamp", current_time)
        prices += data
        current_time = int(data[-1]["timestamp"])

    with open(token + '_price_in_eth.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, keys)
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(prices)
