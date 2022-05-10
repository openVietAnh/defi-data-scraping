import requests
import csv

keys, transactions_id, transactions = None, set(), []
# Maximum indexed block number: 14745467
MAX_BLOCK = 14000002

for block_number in range(14000000, MAX_BLOCK + 1):
    query = """
    {
    borrows (block: {number: 
    """ + str(block_number) + """}, orderBy: timestamp, orderDirection: desc, where: { 
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
        caller {
        id
        }
        pool {
            id
        }
        borrowRate
        borrowRateMode
        stableTokenDebt
        variableTokenDebt
    }
    }
    """
    response = requests.post('https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                                '',
                                json={'query': query})
    if response.status_code == 200:
        print("Read block number", block_number, "successfully:", response.status_code)
    else:
        print("Problem reading block number", block_number, ":", response.status_code)
    
    data = response.json()["data"]["borrows"]
    print(len(data), "transactions found")
    
    if keys is None:
        keys = data[0].keys()

    count = 0
    for transaction in data:
            if transaction["id"] not in transactions_id:
                transaction["user"] = transaction["user"]["id"]
                transaction["reserve"] = transaction["reserve"]["id"]
                transaction["pool"] = transaction["pool"]["id"]
                transaction["caller"] = transaction["caller"]["id"]
                # for key, value in transaction.items():
                #     print(key, value)
                transactions.append(transaction)
                transactions_id.add(transaction["id"])
                count += 1
            else:
                break
    print("New", count, "transaction(s) updated")

with open('borrow.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(transactions)
        