"""
    Get reserve name and symbol
"""
import csv
import requests

KEYS = ["id", "name", "symbol"]

QUERY = """
{
  reserves {
    id
    name
    symbol
  }
}
"""
RESPONSE = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                         '',
                         json={'query': QUERY})

DATA = RESPONSE.json()["data"]["reserves"]

with open('reserves.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, KEYS)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(DATA)
