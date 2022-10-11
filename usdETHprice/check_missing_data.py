# pylint: disable-msg=C0103
"""
    Check for missing needed price timestamp from reserve info file
"""
import csv


TOKEN_LST = ["WBTC", "DAI", "USDT", "USDC"]
missing = []
timestamp_to_price = {}
with open("full_updated.csv") as csvfile:
    READER = csv.reader(csvfile, delimiter=",")
    next(READER, None)
    for item in READER:
        timestamp_to_price[item[0]] = item[1]

for token in TOKEN_LST:
    with open("../csvData/reserveInfo/" + token + "_info.csv") as csvfile:
        READER = csv.reader(csvfile, delimiter=",")
        next(READER, None)
        for item in READER:
            if item[0] not in timestamp_to_price.keys():
                missing.append(item[0])

print(len(missing))
