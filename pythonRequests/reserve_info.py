# pylint: disable-msg=C0103
"""
    Get reserve info
    (deposit rate, borrow rate, utilization rate, total value locked)
    from AAVE V2 subgraph
"""
import csv
import requests

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
        except (KeyError, AttributeError) as error:
            print("Error at block", num)
            print(error)
            errors.append(num)
            continue
        print("Get block", num, "at timestamp", data["lastUpdateTimestamp"])
        if keys is None:
            keys = list(data.keys()) + ["blockNumber"]
        data["blockNumber"] = num
        info.append(data)

with open('../csvData/' + token + '_info.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(info)
