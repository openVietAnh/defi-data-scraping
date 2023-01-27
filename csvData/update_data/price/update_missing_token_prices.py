import csv

token_lst = ["DAI", "WBTC", "USDC", "USDT"]

for token in token_lst:
    timestamps = set()
    time_lst = []
    time_to_price = {}
    data = []
    with open(token + "_price_in_eth.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            timestamps.add(item[0])
            time_lst.append(int(item[0]))
            data.append({"timestamp": item[0], "price": item[1]})
            time_to_price[int(item[0])] = int(item[1])
    
    with open("../processed_info/" + token + "_processed_info.csv", "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        next(reader, None)
        for item in reader:
            if item[0] not in timestamps:
                # print(item[0])
                index, time = 0, int(item[0])
                if time > time_lst[0]:
                    data.append({"timestamp": item[0], "price": time_to_price[time_lst[0]]})
                elif time < time_lst[-1]:
                    data.append({"timestamp": item[0], "price": time_to_price[time_lst[-1]]})
                else:
                    while not time_lst[index] > time > time_lst[index + 1]:
                        index += 1
                    before_price = time_to_price[time_lst[index + 1]]
                    after_price = time_to_price[time_lst[index]]
                    price_diff = after_price - before_price
                    time_diff = time_lst[index] - time_lst[index + 1]
                    # print(before_price, after_price)
                    calculated_price = before_price + (price_diff / time_diff) * (int(item[0]) - time_lst[index + 1])
                    # print("Calculated price", calculated_price)
                    data.append({"timestamp": item[0], "price": int(calculated_price)})

    data.sort(key=lambda x: x["timestamp"])

    with open(token + '_updated.csv', 'w', newline='') as output_file:
        DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
        DICT_WRITER.writeheader()
        DICT_WRITER.writerows(data)
