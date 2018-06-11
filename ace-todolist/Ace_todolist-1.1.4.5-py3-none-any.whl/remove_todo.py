# -*- coding: utf-8 -*-

import sqlite3
from Ace_todolist import search

def remove_todo(searching=None):
    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()

    loop = 'y'

    while loop == 'y' or loop == 'Y':

        # 검색코드
        lists = search.search(searching)

        while len(lists) == 0:
            print("Nothing found! Please retry.")
            print()
            lists = search.search(searching)

        if len(lists) != 1:
            sel_id = input("Record id? ")
            while not sel_id.isdigit():
                sel_id = input("Record id? ")
        else:
            sel_id = lists[0][0]

        sql = "delete from todo where id = ?"
        cur.execute(sql, (sel_id, ))

        # 제거된 항목 뒤의 id를 앞으로 1씩 당기기
        cur.execute("update todo set id = id-1 where id > ?", (sel_id,))
        cur.execute("update SQLITE_SEQUENCE set SEQ = SEQ - 1 where name = 'todo'")
        conn.commit()

        loop = input("\nanything else you want to remove?/n yes:y no:n ")

    conn.close()
