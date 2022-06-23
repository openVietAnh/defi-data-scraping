import csv 

token_lst = ["DAI", "WBTC", "WETH", "USDC", "USDT"]

for token in token_lst:
    userAddress = set()
    data = []
    with open("./tokenTransactions/" + token + ".csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            userAddress.add(item[2])
            data.append({"timestamp": item[-1], "userCount": len(userAddress)})
    
    with open("./tokenUserCount/" + token + ".csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, ["timestamp", "userCount"])
        dict_writer.writeheader()
        dict_writer.writerows(data)