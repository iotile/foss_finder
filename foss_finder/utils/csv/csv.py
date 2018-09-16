import csv


def write_new_row(filename, row):
    # row is a list of strings
    value = ','.join([x if x else '' for x in row])
    with open(filename, 'a+', newline='') as csvfile:
        csvfile.seek(0)
        # add line only if it's not already present in the file
        if not any(value == line.rstrip('\r\n') for line in csvfile):
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(row)
