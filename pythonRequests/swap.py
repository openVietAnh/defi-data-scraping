import requests
import csv
from datetime import datetime

keys, transactions = None, []
current_time = int(datetime.now().timestamp())

while True:
    query = """
    {
        swaps(where: {timestamp_lt: """ + str(current_time) + """}, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            pool {
                id
            }
            user {
                id
            }
            reserve {
                symbol
            }
            borrowRateModeFrom
            borrowRateModeTo
            stableBorrowRate
            variableBorrowRate
            timestamp
        }
    }
    """
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                                '',
                                json={'query': query})
    if response.status_code == 200:
        print("Read from timestamp", current_time, "successfully:", response.status_code)
    else:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
    
    try:
        data = response.json()["data"]["swaps"]
    except Exception:
        print("Error at timestamp", current_time)

    print(len(data), "transactions found")
    if len(data) == 0:
        break
    
    if keys is None:
        keys = data[0].keys()

    for transaction in data:
        transaction["user"] = transaction["user"]["id"]
        transaction["pool"] = transaction["pool"]["id"]
        transaction["reserve"] = transaction["reserve"]["symbol"]
        transactions.append(transaction)

    current_time = int(data[-1]["timestamp"])

with open('swap.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(transactions)
        