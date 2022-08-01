import csv

token_lst = ["DAI", "USDC", "USDT", "WBTC", "WETH"]

for token in token_lst:
    with open(token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        distance, time = [], None
        for item in reader:
            if time is None:
                time = int(item[-1])
            else:
                distance.append(int(item[-1]) - time)
                time = int(item[-1])
        print(token, ":", sum(distance) / len(distance) / 60, "minutes")