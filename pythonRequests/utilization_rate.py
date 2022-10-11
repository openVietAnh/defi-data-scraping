import requests
import csv

keys, history = ["block", "utilizationRate"], []
MAX_BLOCK = 13916166 + 10
# Maximum indexed block number: 14745467

for block_number in range(13916166, MAX_BLOCK + 1):
    query = """
    {
    reserves(block: {number: """ + str(block_number) + """}, where: {symbol: "WETH"}) {
        utilizationRate
    }
    }
    """
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                                '',
                                json={'query': query})

    data = response.json()["data"]["reserves"][0]
    data["block"] = block_number
    history.append(data)

with open('utilizationRateTest.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(history)
