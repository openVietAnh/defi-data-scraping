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

FIRST_QUERY_PART = """{
    userReserves(
        first: 1000
        block: {number: """
SECOND_QUERY_PART = """},
        where: {
            reserve: \""""
THIRD_QUERY_PART = """\",
            scaledATokenBalance_gt: 0,"""
FOURTH_QUERY_PART = """},
        orderBy: scaledATokenBalance,
        orderDirection: desc
    ) {
        user {
            id
        }
        scaledATokenBalance
    }
}"""

TOKEN = "DAI"
ID = "0x6b175474e89094c44da98b954eedeac495271d0f0xb53c1a33016b2dc2ff3653530bff1848a515c8c5"

data, errors = [], []

with open(TOKEN + "_1.txt", "r") as f:
    lastProgress = 0
    count = 0
    blocks = f.readlines()
    total_length = len(blocks)
    block_index = 0
    while block_index < total_length:
        try:
            lastFund = None
            userFunds = set()
            block = blocks[block_index].strip()
            lastTime = datetime.datetime.now()
            while True:
                bonus_condition = "" if lastFund is None else "scaledATokenBalance_lte: \"" + lastFund + "\""
                query = FIRST_QUERY_PART + block + SECOND_QUERY_PART + ID + THIRD_QUERY_PART + bonus_condition + FOURTH_QUERY_PART
                response = requests.post(
                    'https://api.thegraph.com/subgraphs/name/aave/protocol-v2'
                    '',
                    json={'query': query})
                if response.status_code != 200:
                    continue
                output = response.json()["data"]["userReserves"]
                index = 0
                while index < len(output) and output[index]["user"]["id"] in userFunds:
                    index += 1
                if index == len(output):
                    break
                for i in range(index, len(output)):
                    userFunds.add(output[i]["user"]["id"])
                lastFund = output[-1]["scaledATokenBalance"]
            data.append({"block": block, "depositers": len(userFunds)})
            finishTime = datetime.datetime.now()
            count += 1
            block_index += 1
            progress = count / total_length * 100
            delta = finishTime - lastTime
            end = delta / (progress - lastProgress) * (100 - progress)
            lastProgress = progress
            print(progress, "%;", len(userFunds))
            print("Estimated end at:", end.total_seconds() // 3600, end.total_seconds() % 3600 // 60)
            print(block_index, "/", total_length)
        except Exception as e:
            pass

 



    

