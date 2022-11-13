# pylint: disable-msg=C0103
"""
    Get Compound daily info
"""
import csv
import requests

QUERY = """
{
  financialsDailySnapshots(first: 1000, orderBy: timestamp, orderDirection: asc) {
    timestamp
    totalValueLockedUSD
    totalDepositBalanceUSD
    totalBorrowBalanceUSD
  }
}"""

response = requests.post('https://gateway.thegraph.com/api/a9a237eb377f74564ede2d9f043d86f7/subgraphs/id/6tGbL7WBx287EZwGUvvcQdL6m67JGMJrma3JSTtt5SV7', '', json={'query': QUERY})
rows, keys = [], ["timestamp", "totalBorrowBalanceUSD", "totalValueLockedUSD", "totalDepositBalanceUSD"]
if response.status_code != 200:
    print("Problem reading:", response.status_code)
else:
    try:
        data = response.json()["data"]["financialsDailySnapshots"]
        for item in data:
            rows.append({keys[i]: item[keys[i]] for i in range(len(keys))})
        print(len(data))
    except Exception as e:
        print(e)

with open('compound.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", ""])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(rows)