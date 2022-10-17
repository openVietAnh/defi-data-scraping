import requests
import csv
from datetime import datetime

keys, transactions = None, []
current_time = 1659286800
last_transactions = set()

while True:
    query = """
    {
        deposits(where: {timestamp_lte: """ + str(current_time) + """, timestamp_gt: 1654016400}, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            user {
                id
            }
            caller {
                id
            }
            reserve {
                symbol
            }
            amount
            timestamp
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
        data = response.json()["data"]["deposits"]
    except Exception:
        print("Error at timestamp", current_time)
        continue

    if len(data) == 0:
        break
    
    if keys is None:
        keys = data[0].keys()

    index = 0
    try:
        while data[index]["id"] in last_transactions:
            index += 1
    except IndexError:
            current_time -= 1
            continue
    print(len(data) - index, "transactions found at timestamp", current_time)

    for transaction in data[index:]:
        transaction["user"] = transaction["user"]["id"]
        transaction["reserve"] = transaction["reserve"]["symbol"]
        transaction["caller"] = transaction["caller"]["id"]
        transactions.append(transaction)

    current_time = int(data[-1]["timestamp"])
    index = -1
    last_transactions = set()
    while data[index]["timestamp"] == data[-1]["timestamp"]:
        last_transactions.add(data[index]["id"])
        index -= 1

with open('deposit.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(transactions)
        