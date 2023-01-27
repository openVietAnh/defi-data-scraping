import csv

token_lst = ["DAI", "WBTC", "USDC", "USDT", "WETH"]
timestamps = set()
time_lst = []
time_to_price = {}
data = []

with open("usd_ethPrice.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        timestamps.add(item[0])
        time_lst.append(int(item[0]))
        data.append({"timestamp": item[0], "price": item[1]})
        time_to_price[int(item[0])] = int(item[1])

for token in token_lst:
    start_index = 0
    with open("../processed_info/" + token + "_processed_info.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in timestamps:
                index, time = start_index, int(item[0])
                if time < time_lst[0]:
                    data.append({"timestamp": item[0], "price": time_to_price[time_lst[0]]})
                elif time > time_lst[-1]:
                    data.append({"timestamp": item[0], "price": time_to_price[time_lst[-1]]})
                else:
                    while not time_lst[index] < time < time_lst[index + 1]:
                        index += 1
                    start_index = index
                    before_price = time_to_price[time_lst[index]]
                    after_price = time_to_price[time_lst[index + 1]]
                    price_diff = after_price - before_price
                    time_diff = time_lst[index + 1] - time_lst[index]
                    calculated_price = before_price + (price_diff / time_diff) * (int(item[0]) - time_lst[index])
                    data.append({"timestamp": item[0], "price": int(calculated_price)})

data.sort(key=lambda x: x["timestamp"])

with open('usd_ethUpdatedPrice.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
