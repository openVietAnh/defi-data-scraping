# pylint: disable-msg=C0103
"""
    Get all flash loan transactions from AAVE V2 Subgraph
"""
import csv
import requests


keys, transactions = None, []
current_time = 1654016400
last_transactions = set()

FIRST_QUERY_PART = """
{
        flashLoans(where: {timestamp_lte: 
"""
SECOND_QUERY_PART = """
}, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            reserve {
                symbol
            }
            target
            amount
            totalFee
            initiator {
                id
            }
            timestamp
        }
    }
"""

while True:
    query = FIRST_QUERY_PART + str(current_time) + SECOND_QUERY_PART
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                             '',
                             json={'query': query})
    if response.status_code != 200:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
        continue
    try:
        data = response.json()["data"]["flashLoans"]
    except (KeyError, AttributeError) as error:
        print("Error at timestamp", current_time)
        print(error)
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
        transaction["initiator"] = transaction["initiator"]["id"]
        transaction["reserve"] = transaction["reserve"]["symbol"]
        transactions.append(transaction)
    current_time = int(data[-1]["timestamp"])
    index = -1
    last_transactions = set()
    while data[index]["timestamp"] == data[-1]["timestamp"]:
        last_transactions.add(data[index]["id"])
        index -= 1

with open('flashLoan.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(transactions)
        