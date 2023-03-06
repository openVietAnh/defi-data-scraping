# pylint: disable-msg=C0103
"""
    Get daily DAI data on Compound subgraph
"""
import csv
import requests

keys, token = None, []
current_time = 1574984855
last_transactions = set()

"""
{
  marketDailySnapshots(where: {market_: {name: "Compound Dai"}}) {
    market {
      dailySnapshots(
        first: 1000,
        orderBy: timestamp,
        orderDirection: asc,
        where: { timestamp_gt: 1574984855 }) {
        timestamp
        totalBorrowBalanceUSD
        totalValueLockedUSD
      }
    }
  }
}
"""

FIRST_PART_QUERY = """
{
  marketDailySnapshots(where: {market_: {name: "Compound Dai"}}) {
    market {
      dailySnapshots(
        first: 1000,
        orderBy: timestamp,
        orderDirection: asc,
        where: { timestamp_gt: """
SECOND_PART_QUERY = """
 }) {
        timestamp
        totalBorrowBalanceUSD
        totalValueLockedUSD
      }
    }
  }
}"""

# 8ac4185a3b923f4e3c7be52e5c45c4bd

while True:
    query = FIRST_PART_QUERY + str(current_time) + SECOND_PART_QUERY
    response = requests.post('https://gateway.thegraph.com/api/8ac4185a3b923f4e3c7be52e5c45c4bd/subgraphs/id/6tGbL7WBx287EZwGUvvcQdL6m67JGMJrma3JSTtt5SV7'
                             '',
                             json={'query': query})

    if response.status_code != 200:
        print("Problem reading from timestamp", current_time, ":", response.status_code)
        continue
    try:
        data = response.json()["data"]["marketDailySnapshots"]["market"]["dailySnapshots"]
    except (AttributeError, KeyError) as error:
        print("Error at timestamp", current_time)
        print(error)
        continue
    if len(data) == 0:
        break
    if keys is None:
        keys = data[0].keys()
    print(len(data), "rows found at timestamp", current_time)
    for token_data in data:
        token.append(token_data)
    # print(data[-1])
    current_time = int(data[-1]["timestamp"])

with open('dai.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(token)
