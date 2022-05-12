import csv

files = ["large_merged.csv"]
timestamps = []

for file in files:
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        timestamps += [row[2] for row in reader]

while "timestamp" in timestamps:
    timestamps.remove("timestamp")
print(min(timestamps), max(timestamps))
