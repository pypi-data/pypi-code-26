# -*- coding: utf-8 -*-

import sqlite3


# 데이터베이스 생성
def create_db(data="ace.db"):
    conn = sqlite3.connect(data)
    cur = conn.cursor()

    table_create_sql = """create table if not exists todo(
        id integer primary key autoincrement,
        title text not null,
        category text not null,
        due text not null,
        priority integer,
        place text not null,
        comment text not null,
        finished integer);"""

    cur.execute(table_create_sql)
    conn.close()
