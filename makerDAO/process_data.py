import csv
from datetime import datetime

rows, keys = [], ["date", "totalBorrow", "totalValueLocked", "utilizationRate", "liquidity"]
with open("makerDAO.csv", "r") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    next(reader, None)
    for item in reader:
        row = {}
        row["date"] = datetime.fromtimestamp(int(item[0])).strftime('%d/%m/%Y')
        row["totalBorrow"] = item[1]
        row["totalValueLocked"] = item[2]
        try:
            row["utilizationRate"] = float(item[1]) / float(item[2])
        except ZeroDivisionError:
            row["utilizationRate"] = 0
        row["liquidity"] = float(item[2]) - float(item[1])
        rows.append(row)

with open('makerDAO_info.csv', 'w', newline='') as output_file:
    DICT_WRITER = csv.DictWriter(output_file, keys)
    DICT_WRITER.writeheader()
    DICT_WRITER.writerows(rows)
