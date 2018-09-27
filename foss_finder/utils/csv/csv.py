import csv
import os
import errno


def remove_file(filename):
    try:
        os.remove(filename)
    except OSError as e:
        # errno.ENOENT = no such file or directory
        if e.errno != errno.ENOENT:
            raise

def write_new_row(filename, row):
    # row is a list of strings
    value = ','.join([x if x else '' for x in row])
    with open(filename, 'a+', newline='') as csvfile:
        csvfile.seek(0)
        # add line only if it's not already present in the file
        if not any(value == line.rstrip('\r\n') for line in csvfile):
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(row)
