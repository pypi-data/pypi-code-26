import sqlite3, os
import click


def dump(name):
    con = sqlite3.connect(name)
    with open(f'{name}.sql', 'w') as f:
        for line in con.iterdump():
            f.write('%s\n' % line.replace("VARCHAR(","TEXT("))

import piecash

b = piecash.create_book("default_piecash.gnucash",overwrite=True)
b.save()

#dump("default_2_21.gnucash")
dump("default_piecash.gnucash")
