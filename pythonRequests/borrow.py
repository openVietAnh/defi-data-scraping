# pylint: disable-msg=C0103
"""
    Get all AAVE V2 borrow transactions from The Graph
"""
import csv
import requests

keys, transactions = None, []
current_time = 1654016400
last_transactions = set()

FIRST_PART_QUERY = """
{
        borrows(where: {timestamp_lte: 
"""
SECOND_PART_QUERY = """
}, first: 1000, orderBy: timestamp, orderDirection: desc) {
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
            borrowRate
            borrowRateMode
            timestamp
            stableTokenDebt
            variableTokenDebt
        }
    }
"""

while True:
    query = FIRST_PART_QUERY + str(current_time) + SECOND_PART_QUERY
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                             '',
                             json={'query': query})

    if response.status_code != 200:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
        continue
    try:
        data = response.json()["data"]["borrows"]
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

with open('borrow.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(transactions)
