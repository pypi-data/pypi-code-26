# -*- coding: utf-8 -*- 
import sqlite3
from . import duecheck as dc

def auto_fin():
    conn = sqlite3.connect("task.db")
    cur = conn.cursor()

    slct_data = "select * from todo where finished = ?"
    cur.execute(slct_data,['n'])
    records = cur.fetchall()
    for row in records:
        if not dc.istime(row[2]):
            sql = "update todo set finished = ? where id = ?"
            cur.execute(sql,['y',row[0]])
            conn.commit()
