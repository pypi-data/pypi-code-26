# -*- coding: utf-8 -*- 
import sqlite3
from pathlib import Path

home_dir = str(Path.home())
conn = sqlite3.connect(home_dir + "/task.db")
cur = conn.cursor()

def create_table():
    
    table_create_sql = """create table if not exists todo (
            id integer primary key autoincrement,
            what text not null,
            due text not null,
            importance integer,
            category text not null,
            finished text not null); """
    cur.execute(table_create_sql)
    conn.commit()
    conn.close()
