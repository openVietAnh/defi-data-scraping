import requests
import csv

keys = None
token_lst = ["USDT", "USDC", "DAI", "WBTC", "WETH"]

for token in token_lst:
    query = """
    {
    reserves(where: {symbol: \"""" + token +"""\"}) {
        price {
        priceHistory(first: 1000, orderBy: timestamp, orderDirection: desc) {
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
    
    data = response.json()["data"]["reserves"][0]["price"]["priceHistory"]
    
    if keys is None:
        keys = data[0].keys()

    with open("../csvData/" + token + '-price.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        