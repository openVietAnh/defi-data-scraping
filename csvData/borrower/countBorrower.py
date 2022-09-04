import csv
import requests
import datetime

FIRST_QUERY_PART = """{
    userReserves(
        first: 1000
        block: {number: """
SECOND_QUERY_PART = """},
        where: {
            reserve: \""""
THIRD_QUERY_PART = """\",
            currentTotalDebt_gt: 0,"""
FOURTH_QUERY_PART = """},
        orderBy: currentTotalDebt,
        orderDirection: desc
    ) {
        user {
            id
        }
        currentTotalDebt
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
                bonus_condition = "" if lastFund is None else "currentTotalDebt_lte: \"" + lastFund + "\""
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
                lastFund = output[-1]["currentTotalDebt"]
            data.append({"block": block, "borrowers": len(userFunds)})
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