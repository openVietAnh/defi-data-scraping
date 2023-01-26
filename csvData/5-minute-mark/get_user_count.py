import csv
import datetime

# DAI: 1606840850
# USDC: 1606914455 (latest)
# USDT: 1606904131
# WBTC: 1606913751
# WETH: 1606777900

token_lst = ["USDC", "USDT", "WBTC", "WETH", "DAI"]
keys = ["timestamp", "userCount"]
start_time = datetime.datetime(2020, 12, 2, 20, 8, 0)
end_time = datetime.datetime(2022, 7, 31, 23, 12, 24)

for token in token_lst:
    data = []
    time = start_time
    with open("../tokenUserCount/" + token + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        for item in reader:
            new_info = {keys[i]: item[i] for i in range(len(item))}
            row_time = datetime.datetime.fromtimestamp(int(item[0]))
            if row_time < time:
                info = new_info
                continue
            while time <= row_time and time <= end_time:
                info["timestamp"] = int(time.timestamp())
                data.append(dict(info))
                time += datetime.timedelta(minutes=5)
            info = new_info
            if row_time > end_time:
                break
        info["timestamp"] = int(time.timestamp())
        data.append(dict(info))

        with open(token + "-user.csv", 'w', newline='') as output_file:
            DICT_WRITER = csv.DictWriter(output_file, keys)
            DICT_WRITER.writeheader()
            DICT_WRITER.writerows(data)