import requests
import csv
from datetime import datetime

keys, prices = ["timestamp", "price"], []
current_time = 1659286800

while True:
    query = """
    {
        usdEthPriceHistoryItems(
            first: 1000, 
            where: {
                timestamp_lt: """ + str(current_time) + """,
                timestamp_gt: 1654016400}
            orderBy: timestamp,
            orderDirection: desc
        ) {
            timestamp
            price
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
        data = response.json()["data"]["usdEthPriceHistoryItems"]
    except Exception:
        print("Error at timestamp", current_time)
        continue

    if len(data) == 0:
        break

    print(len(data), "rows found at timestamp", current_time)

    prices += data

    current_time = int(data[-1]["timestamp"])

with open('../csvData/update_data/price/usd_ethPrice.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(prices)
        