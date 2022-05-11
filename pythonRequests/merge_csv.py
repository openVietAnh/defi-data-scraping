import csv

files_name = ["borrow.csv", "borrow (1).csv", "borrow (2).csv", "borrow (3).csv"]
merged_data = []
keys = ['id', 'amount', 'timestamp', 'reserve', 'user', 'caller', 'pool', 'borrowRate', 'borrowRateMode', 'stableTokenDebt', 'variableTokenDebt']
id = set()

for file in files_name:
    with open(file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # print("Rows:", len(list(reader)))
        dct = {}
        duplicate_count = 0
        for row in reader:
            print(row[0])
            if row[0] not in id:
                id.add(row[0])
                for index, value in enumerate(row):
                    dct[keys[index]] = value
                merged_data.append(dct.copy())
            else:
                duplicate_count += 1
        print(duplicate_count, "duplicate(s) found")

print("Total:", len(merged_data))

with open('merged.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(merged_data)
        
