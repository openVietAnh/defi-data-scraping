from http.client import responses
import requests
import csv

keys = None
token_lst = ["USDT", "USDC", "DAI", "WBTC", "WETH"]

for index, token in enumerate(token_lst):
    timestamps = []
    with open("../csvData/" + token + "-price.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        for item in reader:
            timestamps.append(int(item[1])) 
    query = """
    {
        usdEthPriceHistoryItems(where: {timestamp_in: """ + str(timestamps) + """}, orderBy: timestamp, orderDirection: desc) {
            price
            timestamp
        }
    }
    """
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                                '',
                                json={'query': query})
    # print(response.status_code)
    # print(response.json())
    data = response.json()["data"]["usdEthPriceHistoryItems"]
    
    if keys is None:
        keys = data[0].keys()

    with open("../usdETHprice/" + str(index) + '.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)