import csv
import requests
import datetime

# {
#   "data": {
#     "reserves": [
#       {
#         "id": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c5990xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
#         "symbol": "WBTC"
#       },
#       {
#         "id": "0x6b175474e89094c44da98b954eedeac495271d0f0xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
#         "symbol": "DAI"
#       },
#       {
#         "id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb480xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
#         "symbol": "USDC"
#       },
#       {
#         "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc20xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
#         "symbol": "WETH"
#       },
#       {
#         "id": "0xdac17f958d2ee523a2206206994597c13d831ec70xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
#         "symbol": "USDT"
#       }
#     ]
#   }
# }

def calculateHHI(userFunds):
    total = sum(userFunds.values())
    return sum([(value / total * 100) ** 2 for value in userFunds.values()])

TOKEN = "DAI"
ID = "0x6b175474e89094c44da98b954eedeac495271d0f0xb53c1a33016b2dc2ff3653530bff1848a515c8c5"
DECIMAL = 18

data, errors = [], []

with open(TOKEN + "_fund_block.csv", "r") as f:
    lastTime = datetime.datetime.now()
    lastProgress = 0
    count = 0
    blocks = f.readlines()
    total_length = len(blocks)
    for item in blocks:
        lastFund = None
        userFunds = {}
        block = item.strip()
        while True:
            bonus_condition = "" if lastFund is None else "scaledATokenBalance_lte: \"" + lastFund + "\""
            query = """
{
    userReserves(
        first: 1000
        block: {number: """ + block + """},
        where: {
            reserve: \"""" + ID + """\",
            scaledATokenBalance_gt: 0,""" + bonus_condition + """},
        orderBy: scaledATokenBalance,
        orderDirection: desc
    ) {
        user {
            id
        }
        scaledATokenBalance
    }
}
"""
            response = requests.post(
                'https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                '',
                json={'query': query})
            # print(query)
            if response.status_code != 200:
                print("Problem reading from block", block, ":", response.status_code)
                errors.append(block)
                continue
            try:
                output = response.json()["data"]["userReserves"]
            except Exception:
                print(response.json())
                print("Error at block", block)
                continue
            index = 0
            while index < len(output) and output[index]["user"]["id"] in userFunds.keys():
                index += 1
            if index == len(output):
                break
            print("Got", len(output) - index, " users")
            for i in range(index, len(output)):
                userFunds[output[i]["user"]["id"]] = float(output[i]["scaledATokenBalance"]) / DECIMAL
            lastFund = output[-1]["scaledATokenBalance"]
        hhi = calculateHHI(userFunds)
        data.append({"block": block, "HHI": hhi})
        finishTime = datetime.datetime.now()
        count += 1
        progress = count / total_length * 100
        delta = finishTime - lastTime
        end = datetime.datetime.now() + (delta / (progress - lastProgress) * (100 - progress))
        print(progress, "%;", hhi)
        print("Estimated end at:", end.hour, end.minute)

with open(TOKEN + '_HHI.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, ["block", "HHI"])
    dict_writer.writeheader()
    dict_writer.writerows(data)



    

