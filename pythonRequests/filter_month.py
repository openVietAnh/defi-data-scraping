import datetime
import csv

january, febuary = [], []
keys = ['id', 'amount', 'timestamp', 'reserve', 'user', 'caller', 'pool', 'borrowRate', 'borrowRateMode', 'stableTokenDebt', 'variableTokenDebt']

with open("large_merged.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for item in reader:
        if item[0] != "id":
            timestamp = int(item[2])
            month = datetime.datetime.fromtimestamp(timestamp).month
            dct = {keys[index]: item[index] for index in range(len(item))}
            if month == 1:
                january.append(dct)
            elif month == 2:
                febuary.append(dct)

print(len(january), len(febuary))
january.sort(key=lambda x: x["timestamp"])
febuary.sort(key=lambda x: x["timestamp"])

with open('january.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(january)

with open('febuary.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(febuary)
