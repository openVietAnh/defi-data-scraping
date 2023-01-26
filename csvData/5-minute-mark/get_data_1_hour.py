import csv
import datetime

# Start-time
# DAI: 2020-12-01T23:40:50
# USDC: 2020-12-02T20:07:35 (lastest)
# USDT: 2020-12-02T17:15:31
# WBTC: 2020-12-02T19:55:51
# WETH: 2020-12-01T06:11:40

# End-time
# DAI:  1659285305
# USDC: 1659286633
# USDT: 1659286247
# WETH: 1659286703
# WBTC: 1659283944 (earliest)

token_lst = ["WBTC"]
keys = ["timestamp", "time", "blockNumber", "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate", "utilizationRate", "userCount", "HHI", "depositers", "borrowers", "price"]
start_time = datetime.datetime(2020, 12, 2, 20, 8, 0)
end_time = datetime.datetime(2022, 7, 31, 23, 12, 24)

for token in token_lst:
    data = []
    time = start_time
    with open("../reserveInfo/" + token + "_full_info.csv", "r") as csvfile:
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
                # info["time"] = time.isoformat(timespec='seconds')
                info["time"] = "{}/{}/{} {}:{}".format(time.day, time.month, time.year, time.hour, time.minute)
                data.append(dict(info))
                time += datetime.timedelta(minutes=60)
            info = new_info
            if row_time > end_time:
                break
        info["timestamp"] = int(time.timestamp())
        info["time"] = "{}/{}/{} {}:{}".format(time.day, time.month, time.year, time.hour, time.minute)
        data.append(dict(info))

        with open(token + "_1hour.csv", 'w', newline='') as output_file:
            DICT_WRITER = csv.DictWriter(output_file, keys)
            DICT_WRITER.writeheader()
            DICT_WRITER.writerows(data)