import csv

keys = ["price", "timestamp"]
time = set()
prices = []
count = 0

for i in range(5):
    with open(str(i) + ".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for item in reader:
            if item[1] not in time:
                prices.append({"price": item[0], "timestamp": item[1]})
                time.add(item[1])
            else:
                count += 1

print(count, len(prices))
with open('prices.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(prices)
