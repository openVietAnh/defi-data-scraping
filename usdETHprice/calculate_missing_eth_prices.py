# pylint: disable-msg=C0103
"""
    Calculate ETH price at multiple needed timestamps that AAVE V2 subgraph did not store
"""
import csv

timestamps = set()
time_lst = []
time_to_price = {}
data = []

with open("../csvData/tokenPriceinUSD/WETH-usd-price.csv", "r") as csv_file:
    READER = csv.reader(csv_file, delimiter=",")
    next(READER, None)
    for item in READER:
        timestamps.add(item[0])
        time_lst.append(int(item[0]))
        data.append({"timestamp": item[0], "price": item[1]})
        time_to_price[int(item[0])] = float(item[1])

start_index = 0

with open("../csvData/reserveInfo/WETH_info.csv", "r") as csv_file:
    READER = csv.reader(csv_file, delimiter=",")
    next(READER, None)
    for item in READER:
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
                before_price = time_to_price[time_lst[index + 1]]
                after_price = time_to_price[time_lst[index]]
                price_diff = after_price - before_price
                time_diff = time_lst[index] - time_lst[index + 1]
                change = (price_diff / time_diff) * (int(item[0]) - time_lst[index + 1])
                calculated_price = before_price + change
                data.append({"timestamp": item[0], "price": float(calculated_price)})

data.sort(key=lambda x: x["timestamp"])

with open('../csvData/tokenPriceinUSD/WETH-usd-price.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, ["timestamp", "price"])
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(data)
