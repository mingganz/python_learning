import csv

csvFile = open("files/test.csv", 'wt')
try:
    Writer = csv.writer(csvFile)
    Writer.writerow(('number', 'number plus 2', 'number times 2'))
    for i in range(10):
        Writer.writerow((i, i+2, i*2))
finally:
    csvFile.close()
