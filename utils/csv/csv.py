import csv


def write_new_row(filename, row, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL):
    # row is a list of strings
    value = ','.join([x if x else '' for x in row])
    with open(filename, 'a+', newline='') as csvfile:
        csvfile.seek(0)
        if not any(value == line.rstrip('\r\n') for line in csvfile):
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(row)
