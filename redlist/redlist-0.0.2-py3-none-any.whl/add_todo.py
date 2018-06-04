# -*- coding: utf-8 -*-
import sqlite3
from . import create_table as ct
from . import duecheck as dc

def add_todo():
    conn = sqlite3.connect("task.db")
    cur = conn.cursor()

    sql = "insert into todo (what, due, importance, category, finished) values (?, ?, ?, ?, ?)"

    while True:
        what = str(input("What? "))
        if what != '':
            break

    while True:
        due = str(input("Due? (yyyy-mm-dd hh:mm:ss) "))
        if dc.isdue(due):
            break
        elif due == '':
            due = '0000-00-00 00:00:00'
            break
        else:
            print('Invaild input! Please check your input')

    while True:
        importance = str(input("Importance? (1 ~ 5) "))
        if importance == '':
            importance = 0
            break
        elif importance.isdigit() and 1 <= int(importance) <= 5:
            break
        else:
            print('Invaild input! Please check your input')

    category = str(input("Category? "))
    if category == '':
        category = 'GENERAL'

    data = [what, due, int(importance), category, "n"]

    cur.execute(sql, data)
    conn.commit()

    print("")
