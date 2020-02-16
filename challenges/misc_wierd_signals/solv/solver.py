#!/usr/bin/python3

import csv

FLAG = []

with open("../public/wierd_signals.csv") as data:
    signals = csv.DictReader(data)
    last_e = 0
    tmp = ''
    for line in signals:
        e = line['E']
        if last_e != e:
            if line['RS'] == '1' and line['E'] == '1' and line['R/W'] == '0':  # we are writing data to controller
                if tmp == '':
                    tmp = line['DB7'] + line['DB6'] + line['DB5'] + line['DB4']
                    # in 4 bit mode data are sent in chunks of 4 bytes
                else:
                    FLAG.append(chr(int(tmp + line['DB7'] + line['DB6'] + line['DB5'] + line['DB4'], 2)))
                    # ASCII codes == controller character codes (at least for printable ASCII)
                    tmp = ''
        last_e = e

print(''.join(FLAG))
