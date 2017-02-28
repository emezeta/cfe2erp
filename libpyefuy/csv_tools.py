# coding: utf-8
#!/usr/bin/env python

from __future__ import print_function

import StringIO
import csv
import config

SEP = config.delimiter
EOL = config.lineterminator
OUT_DIR = config.out_path


class handle(object):


    def __init__(self, csv_fname):
        self.csv_fname = csv_fname
        self.lin_csv   = StringIO.StringIO()
        self.writer    = csv.writer(self.lin_csv, delimiter=SEP, lineterminator=EOL)


    def record(self, csv_row):
        # lrpmqtp charset!
        # no se puede int.encode int no es srtng! => pasar a str int, long y float
        to_str = list()
        for i in csv_row:
            if isinstance(i, (int, long, float)):
                i = str(i)
            to_str.append(i)

        self.writer.writerow([campo.encode('utf_8') for campo in to_str])


    def write_csv(self):
        with open(OUT_DIR + self.csv_fname, "w") as f:
            f.write(self.lin_csv.getvalue())
