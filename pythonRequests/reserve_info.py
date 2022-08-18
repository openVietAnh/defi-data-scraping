import requests
import csv
from datetime import datetime

keys, info, token = None, [], "WBTC"
errors = []
block_numbers = set()

with open("../csvData/hashtoBlockNum/" + token + "_block.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        num = item[1]

        query = """
        {
            reserves(block: {number: """ + num + """}, where: {symbol: \"""" + token + """\"}) {
                decimals
                totalDeposits
                stableBorrowRate
                variableBorrowRate
                liquidityRate
                utilizationRate
                lastUpdateTimestamp
            }
        }
        """
        response = requests.post(
            'https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
            '',
            json={'query': query})
        if response.status_code != 200:
            print("Problem reading from block", num, ":", response.status_code)
            errors.append(num)
            continue

        try:
            data = response.json()["data"]["reserves"][0]
        except Exception:
            print("Error at block", num)
            errors.append(num)
            continue

        print("Get block", num, "at timestamp", data["lastUpdateTimestamp"])
        
        if keys is None:
            keys = list(data.keys()) + ["blockNumber"]

        data["blockNumber"] = num
        info.append(data)

with open('../csvData/' + token + '_info.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(info)
        