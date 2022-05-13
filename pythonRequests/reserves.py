import requests
import csv

keys, reserves = ["id", "name", "symbol"], []
# Maximum indexed block number: 14745467

query = """
{
  reserves {
    id
    name
    symbol
  }
}
"""
response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                            '',
                            json={'query': query})

data = response.json()["data"]["reserves"]

with open('reserves.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(data)
