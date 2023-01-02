import csv

date = []
graph = {}
with open("compound_info.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    for item in reader:
        graph[item[1]] = (int(item[0]), float(item[3]) - float(item[2]))
        date.append(item[1])

llama = {}
with open("compound-defillama.csv", "r") as csv_file:
    reader = csv.reader(csv_file, delimiter=",")
    next(reader, None)
    next(reader, None)
    next(reader, None)
    next(reader, None)
    next(reader, None)
    for item in reader:
        try:
            llama[item[1]] = (int(item[2]), float(item[5]))
        except ValueError:
            pass

diff = []
for item in date:
    try:
        diff.append((item, graph[item][0] - llama[item][0], graph[item][1] - llama[item][1]))
    except KeyError:
        diff.append((item, 0, 0))
print(max(diff, key=lambda x: x[1]))
with open("diff.txt", "w") as f:
    f.writelines(map(lambda x: x[0] + "," + str(x[1]) + "," + str(x[2]) + "\n", diff))