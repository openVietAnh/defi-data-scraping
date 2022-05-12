import csv
from os import listdir
from os.path import isfile, join

files_name = [f for f in listdir(".") if isfile(join(".", f))]

merged_data = []
keys = ['id', 'amount', 'timestamp', 'reserve', 'user', 'caller', 'pool', 'borrowRate', 'borrowRateMode', 'stableTokenDebt', 'variableTokenDebt']
id = set()

for file in files_name:
    if file.endswith(".csv"):
        with open(file) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            dct = {}
            duplicate_count = 0
            for row in reader:
                if row[0] not in id:
                    id.add(row[0])
                    for index, value in enumerate(row):
                        dct[keys[index]] = value
                    merged_data.append(dct.copy())
                else:
                    duplicate_count += 1
            print(duplicate_count, "duplicate(s) found")

print("Total:", len(merged_data))

with open('large_merged.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(merged_data)
