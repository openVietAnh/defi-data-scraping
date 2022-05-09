import requests
query = """
{
  borrows (block: {number: 14000000}, orderBy: timestamp, orderDirection: desc, where: { 
  }) {
    id
    amount
    timestamp
    reserve {
      id
    }
    user {
      id
    }
  }
}
"""
response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                            '',
                            json={'query': query})
print(response.status_code)
print(response.json())