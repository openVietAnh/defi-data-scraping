import csv
import datetime

token_lst = ["WBTC"]
keys = ["timestamp", "time", "blockNumber", "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate", "utilizationRate", "userCount", "HHI"]
current_time = datetime.datetime(2020, 12, 2, 20, 8, 0)

# timestamp,time,blockNumber,totalDeposits,depositRate,stableBorrowRate,variableBorrowRate,utilizationRate,userCount,HHI
for token in token_lst:
    print(token)
    with open(token + ".csv", "r") as csvfile:
        data = []
        reader = csv.reader(csvfile, delimiter=",")
        next(reader, None)
        totalDeposits, depositRates, stable, variable, utilization, userCount, HHI = [], [], [], [], [], [], []
        for item in reader:
            time = datetime.datetime.fromtimestamp(float(item[0]))
            if time.day == current_time.day:
                totalDeposits.append(float(item[3]))
                depositRates.append(float(item[4]))
                stable.append(float(item[5]))
                variable.append(float(item[6]))
                utilization.append(float(item[7]))
                userCount.append(float(item[8]))
                HHI.append(float(item[9]))
            else:
                try:
                    format_time = "{}/{}/{}".format(current_time.day, current_time.month, current_time.year)
                    avgTotal = sum(totalDeposits) / len(totalDeposits)
                    avgDeposit = sum(depositRates) / len(depositRates)
                    avgStable = sum(stable) / len(stable)
                    avgVariable = sum(variable) / len(variable)
                    avgUlt = sum(utilization) / len(utilization)
                    avgUser = sum(userCount) / len(userCount)
                    avgHHI = sum(HHI) / len(HHI)
                    data.append({ "time": format_time,
                        "totalDeposits": avgTotal,
                        "depositRate": avgDeposit,
                        "stableBorrowRate": avgStable,
                        "variableBorrowRate": avgVariable,
                        "utilizationRate": avgUlt,
                        "userCount": avgUser,
                        "HHI": avgHHI})
                    totalDeposits, depositRates, stable, variable, utilization, userCount, HHI = [], [], [], [], [], [], []
                    totalDeposits.append(float(item[3]))
                    depositRates.append(float(item[4]))
                    stable.append(float(item[5]))
                    variable.append(float(item[6]))
                    utilization.append(float(item[7]))
                    userCount.append(float(item[8]))
                    HHI.append(float(item[9]))
                    current_time = time
                except ZeroDivisionError:
                    print(format_time)
                    print(len(data))
                    print(len(totalDeposits))
                    break
        format_time = "{}/{}/{}".format(current_time.day, current_time.month, current_time.year)
        avgTotal = sum(totalDeposits) / len(totalDeposits)
        avgDeposit = sum(depositRates) / len(depositRates)
        avgStable = sum(stable) / len(stable)
        avgVariable = sum(variable) / len(variable)
        avgUlt = sum(utilization) / len(utilization)
        avgUser = sum(userCount) / len(userCount)
        avgHHI = sum(HHI) / len(HHI)
        data.append({ "time": format_time,
            "totalDeposits": avgTotal,
            "depositRate": avgDeposit,
            "stableBorrowRate": avgStable,
            "variableBorrowRate": avgVariable,
            "utilizationRate": avgUlt,
            "userCount": avgUser,
            "HHI": avgHHI})

    with open(token + "_average.csv", 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, ["time", "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate", "utilizationRate", "userCount", "HHI"])
            dict_writer.writeheader()
            dict_writer.writerows(data)
