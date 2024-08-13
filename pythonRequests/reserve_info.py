# pylint: disable-msg=C0103
"""
    Get reserve info
    (deposit rate, borrow rate, utilization rate, total value locked)
    from AAVE V2 subgraph
"""
import requests
import csv
from datetime import datetime
from IPython.display import clear_output

total_length = 31678
keys, info, token = None, [], "DAI"
errors = []
count = 0

with open("drive/MyDrive/csvData/" + token + ".csv", "r") as f:
    reader = f.readlines()
    for i in range(0, len(reader), 10):
        block_range = reader[i:i + 10]
        query = "{\n\t"
        for item in block_range:
            num = item.strip()
            query += "b" + str(num) + ''': reserves(block: {number: ''' + num + '''}, where: {symbol: "''' + token + '''"}) {
                    decimals
                    totalDeposits
                    stableBorrowRate
                    variableBorrowRate
                    liquidityRate
                    utilizationRate
                    lastUpdateTimestamp
                }
            '''
        query += "\n}"
        response = requests.post(
            'https://gateway-arbitrum.network.thegraph.com/api/47fe3220cace15c6d958a2b9b3154b74/subgraphs/id/8wR23o1zkS4gpLqLNU4kG3JHYVucqGyopL5utGxP2q1N'
            '',
            json={'query': query})
        if response.status_code != 200:
            print("Problem reading 10 blocks from", num, ":", response.status_code)
            errors.append(num)
            continue

        try:
            data = response.json()["data"]
        except Exception:
            print("Error at block", num)
            errors.append(num)
            continue
        
        for item in block_range:
            key = "b" + str(item.strip())
            block_data = data[key][0]

            if keys is None:
                keys = list(block_data.keys()) + ["blockNumber"]

            block_data["blockNumber"] = num
        info.append(block_data)
        clear_output(wait=True)
        count += 10
        print(count / total_length * 100, "%")

with open(token + '_info.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(info)
