# pylint: disable-msg=C0103
"""
    Get all liquidation call transactions from AAVE V2 subgraph
"""
import csv
import requests

keys, transactions = None, []
current_time = 1654016400
last_transactions = set()

FIRST_QUERY_PART = """
{
        liquidationCalls(where: {timestamp_lte: 
"""
SECOND_QUERY_PART = """
}, first: 1000, orderBy: timestamp, orderDirection: desc) {
            id
            pool {
                id
            }
            user {
                id
            }
            collateralReserve {
                symbol
            }
            collateralAmount
            principalReserve {
                symbol
            }
            principalAmount
            liquidator
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
        data = response.json()["data"]["liquidationCalls"]
    except (KeyError, AttributeError):
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
    for transaction in data[index:]:
        transaction["user"] = transaction["user"]["id"]
        transaction["pool"] = transaction["pool"]["id"]
        transaction["collateralReserve"] = transaction["collateralReserve"]["symbol"]
        transaction["principalReserve"] = transaction["principalReserve"]["symbol"]
        transactions.append(transaction)
    current_time = int(data[-1]["timestamp"])
    index = -1
    last_transactions = set()
    while data[index]["timestamp"] == data[-1]["timestamp"]:
        last_transactions.add(data[index]["id"])
        index -= 1

with open('liquidationCall.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(transactions)
        