# pylint: disable-msg=C0103
"""
    Get all AAVE V2 transactions from The Graph subgraph
"""
import csv
import requests

FIRST_PART_QUERY = """
{
        userTransactions(where: {timestamp_lte: """
SECOND_PART_QUERY = """
}, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            pool {
                id
            }
            user {
                id
            }
            timestamp
        }
    }
"""

keys, transactions = None, []
error = []
current_time = 1654016400
last_transactions = set()

while True:
    query = FIRST_PART_QUERY + str(current_time) + SECOND_PART_QUERY
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                             '',
                             json={'query': query})
    if response.status_code != 200:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
        continue
    try:
        data = response.json()["data"]["userTransactions"]
    except (AttributeError, KeyError) as error:
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
        transaction["pool"] = transaction["pool"]["id"]
        transaction["user"] = transaction["user"]["id"]
        transactions.append(transaction)
    current_time = int(data[-1]["timestamp"])
    index = -1
    last_transactions = set()
    while data[index]["timestamp"] == data[-1]["timestamp"]:
        last_transactions.add(data[index]["id"])
        index -= 1

with open('allTransaction.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(transactions)
        